"""Client for posting normalized events to the cloud API."""
from __future__ import annotations

import logging
from typing import Optional

import requests

from .config_model import EdgeEvent

LOGGER = logging.getLogger(__name__)


class CloudClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def post_event(self, event: EdgeEvent) -> requests.Response:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        url = f"{self.base_url}/events"
        LOGGER.info("Posting event for camera %s to cloud", event.camera_id)
        response = requests.post(url, headers=headers, data=event.json())
        response.raise_for_status()
        return response
