"""Entry point for the edge agent.

Steps:
1. Load edge configuration JSON into models.
2. Render Frigate configuration using Jinja2 template.
3. Optionally launch Docker Compose services (MQTT + Frigate).
4. Subscribe to Frigate MQTT events, normalize them, and post to the cloud API.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import subprocess
from pathlib import Path
from typing import Optional

from .cloud_client import CloudClient
from .config_model import EdgeSiteConfig
from .event_normalizer import EventNormalizer
from .frigate_config_renderer import render_frigate_config
from .mqtt_listener import MQTTEventListener

LOG_LEVEL = os.getenv("EDGE_AGENT_LOG", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger("edge-agent")


def load_config(path: Path) -> EdgeSiteConfig:
    LOGGER.info("Loading edge configuration from %s", path)
    content = json.loads(path.read_text())
    return EdgeSiteConfig.parse_obj(content)


def launch_docker_compose(compose_file: Path, service: str | None = None) -> None:
    cmd = ["docker", "compose", "-f", str(compose_file), "up", "-d"]
    if service:
        cmd.append(service)
    LOGGER.info("Launching services via Docker Compose: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Edge Agent for Frigate integration")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("/opt/edge/config.json"),
        help="Path to edge JSON configuration",
    )
    parser.add_argument(
        "--cloud-url",
        required=True,
        help="Base URL for the cloud API (e.g., http://localhost:8000)",
    )
    parser.add_argument(
        "--cloud-api-key",
        help="Optional API key for cloud authentication",
    )
    parser.add_argument(
        "--skip-compose",
        action="store_true",
        help="Skip launching Docker Compose (Frigate must already be running)",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    config = load_config(args.config)
    render_frigate_config(config)

    if not args.skip_compose:
        launch_docker_compose(config.frigate_compose_file)

    normalizer = EventNormalizer(config)
    cloud_client = CloudClient(args.cloud_url, api_key=args.cloud_api_key)

    stop = False

    def _signal_handler(signum, frame):
        nonlocal stop
        LOGGER.info("Received signal %s, shutting down", signum)
        stop = True

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    with MQTTEventListener(config.mqtt) as listener:
        while not stop:
            for event in listener.get_events(timeout=1.0):
                edge_event = normalizer.normalize(event)
                try:
                    cloud_client.post_event(edge_event)
                except Exception as exc:  # pragma: no cover - network dependent
                    LOGGER.exception("Failed to post event: %s", exc)
            # loop returns control to check stop flag

    LOGGER.info("Edge agent shutdown complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
