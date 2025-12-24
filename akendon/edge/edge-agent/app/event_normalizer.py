"""Normalize Frigate events into EdgeEvent schema."""
from __future__ import annotations

import logging
from typing import Any, Dict

from .config_model import EdgeEvent, EdgeSiteConfig

LOGGER = logging.getLogger(__name__)


class EventNormalizer:
    def __init__(self, config: EdgeSiteConfig):
        self.config = config

    def normalize(self, frigate_event: Dict[str, Any]) -> EdgeEvent:
        camera_id = frigate_event.get("camera") or frigate_event.get("after", {}).get(
            "camera"
        )
        label = frigate_event.get("label") or frigate_event.get("after", {}).get(
            "label"
        )
        score = frigate_event.get("score") or frigate_event.get("after", {}).get(
            "score"
        )
        start_time = frigate_event.get("start_time") or frigate_event.get(
            "before", {}
        ).get("start_time")
        end_time = frigate_event.get("end_time") or frigate_event.get("after", {}).get(
            "end_time"
        )
        snapshot = self._extract_media_path(frigate_event, "thumbnail", "snapshot")
        clip = self._extract_media_path(frigate_event, "clip")

        edge_event = EdgeEvent(
            device_id=self.config.device_id,
            site_id=self.config.site_id,
            camera_id=camera_id or "unknown",
            label=label or "unknown",
            score=float(score or 0.0),
            ts_start=float(start_time or 0.0),
            ts_end=float(end_time) if end_time is not None else None,
            snapshot_path=snapshot,
            clip_path=clip,
            raw_json=frigate_event,
        )
        LOGGER.debug("Normalized event: %s", edge_event.json())
        return edge_event

    @staticmethod
    def _extract_media_path(event: Dict[str, Any], *keys: str) -> str | None:
        for key in keys:
            value = event.get(key)
            if isinstance(value, str):
                return value
            if isinstance(value, dict):
                path = value.get("path") or value.get("url")
                if path:
                    return path
        return None
