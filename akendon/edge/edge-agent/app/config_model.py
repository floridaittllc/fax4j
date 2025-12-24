"""Configuration and schema models for the edge agent.

All models are Pydantic-based to ensure strict validation and clarity.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, validator


class FrigateMQTTConfig(BaseModel):
    host: str = Field(..., description="MQTT broker hostname or IP")
    port: int = Field(1883, description="MQTT broker port")
    username: Optional[str] = Field(None, description="MQTT username")
    password: Optional[str] = Field(None, description="MQTT password")
    topic_prefix: str = Field(
        "frigate",
        description="Root topic prefix used by Frigate for publishing events",
    )


class Zone(BaseModel):
    name: str = Field(..., description="Zone name used in Frigate configuration")
    coordinates: List[str] = Field(..., description="Polygon coordinates for the zone")


class CameraConfig(BaseModel):
    camera_id: str = Field(..., description="Unique camera identifier")
    name: str = Field(..., description="Human-friendly camera name")
    rtsp_url: str = Field(..., description="RTSP URL for the camera feed")
    detect: bool = Field(True, description="Whether detection is enabled")
    record: bool = Field(True, description="Whether recording is enabled")
    zones: List[Zone] = Field(default_factory=list)
    snapshots_retention_days: int = Field(1, ge=0, description="Retention for snapshots")
    clips_retention_days: int = Field(1, ge=0, description="Retention for clips")

    @validator("rtsp_url")
    def validate_rtsp_url(cls, value: str) -> str:
        if not value.startswith("rtsp://") and not value.startswith("rtsps://"):
            raise ValueError("rtsp_url must start with rtsp:// or rtsps://")
        return value


class EdgeSiteConfig(BaseModel):
    site_id: str = Field(..., description="Unique site identifier")
    device_id: str = Field(..., description="Unique device/agent identifier")
    mqtt: FrigateMQTTConfig
    cameras: List[CameraConfig] = Field(..., description="Cameras managed by Frigate")
    frigate_template_path: Path = Field(
        Path("/opt/edge/frigate/config.template.yml"),
        description="Path to the Jinja2 template for Frigate configuration",
    )
    frigate_config_output: Path = Field(
        Path("/opt/edge/frigate/config.yml"),
        description="Rendered Frigate configuration output path",
    )
    frigate_compose_file: Path = Field(
        Path("/opt/edge/docker-compose.yml"),
        description="Path to docker-compose file used to run Frigate",
    )


class EdgeEvent(BaseModel):
    device_id: str
    site_id: str
    camera_id: str
    label: str
    score: float
    ts_start: float = Field(..., description="Unix timestamp when the event started")
    ts_end: Optional[float] = Field(None, description="Unix timestamp when the event ended")
    snapshot_path: Optional[str] = Field(
        None, description="Path to snapshot for the event if available"
    )
    clip_path: Optional[str] = Field(None, description="Path to the clip for the event")
    raw_json: dict = Field(..., description="Original Frigate event payload")

    class Config:
        json_encoders = {Path: lambda p: str(p)}
