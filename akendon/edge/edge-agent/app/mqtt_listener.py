"""MQTT listener for Frigate events."""
from __future__ import annotations

import json
import logging
import queue
import threading
from typing import Callable, Iterable, Optional

import paho.mqtt.client as mqtt

from .config_model import FrigateMQTTConfig

LOGGER = logging.getLogger(__name__)


class MQTTEventListener:
    """Subscribe to Frigate MQTT events and forward them to a queue."""

    def __init__(self, config: FrigateMQTTConfig, topic_suffix: str = "events"):
        self.config = config
        self.topic = f"{self.config.topic_prefix}/{topic_suffix}"
        self._client = mqtt.Client()
        self._queue: "queue.Queue[dict]" = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc):  # type: ignore[override]
        if rc == 0:
            LOGGER.info("Connected to MQTT broker, subscribing to %s", self.topic)
            client.subscribe(self.topic)
        else:
            LOGGER.error("Failed to connect to MQTT broker (code %s)", rc)

    def _on_message(self, client: mqtt.Client, userdata, msg):  # type: ignore[override]
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            LOGGER.debug("Received MQTT message on %s", msg.topic)
            self._queue.put(payload)
        except json.JSONDecodeError as exc:
            LOGGER.warning("Failed to decode MQTT payload: %s", exc)

    def start(self):
        LOGGER.info("Starting MQTT listener for %s", self.topic)
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

        if self.config.username:
            self._client.username_pw_set(self.config.username, self.config.password)

        self._client.connect(self.config.host, self.config.port, keepalive=60)

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        while not self._stop_event.is_set():
            self._client.loop(timeout=1.0)

    def stop(self):
        LOGGER.info("Stopping MQTT listener")
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        try:
            self._client.disconnect()
        except Exception as exc:  # pragma: no cover - network dependent
            LOGGER.warning("Error during MQTT disconnect: %s", exc)

    def get_events(self, timeout: Optional[float] = 1.0) -> Iterable[dict]:
        """Yield events from the internal queue."""
        while True:
            try:
                yield self._queue.get(timeout=timeout)
            except queue.Empty:
                if self._stop_event.is_set():
                    break

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

