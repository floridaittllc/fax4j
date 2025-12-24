"""Utility for rendering a Frigate configuration from the edge config model."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from .config_model import EdgeSiteConfig

LOGGER = logging.getLogger(__name__)


def _build_render_context(config: EdgeSiteConfig) -> Dict[str, Any]:
    return {
        "site_id": config.site_id,
        "device_id": config.device_id,
        "mqtt": config.mqtt.dict(),
        "cameras": [camera.dict() for camera in config.cameras],
    }


def render_frigate_config(config: EdgeSiteConfig) -> Path:
    """Render the Frigate configuration using Jinja2.

    Args:
        config: Parsed edge site configuration.

    Returns:
        Path to the rendered config file.
    """

    template_path = Path(config.frigate_template_path)
    output_path = Path(config.frigate_config_output)

    LOGGER.info("Rendering Frigate configuration from %s", template_path)
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=False,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    rendered = template.render(**_build_render_context(config))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered)
    LOGGER.info("Frigate config rendered to %s", output_path)
    return output_path
