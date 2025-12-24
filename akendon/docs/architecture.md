# Edge Agent + Frigate Integration

This repo wires Frigate as an internal dependency under an edge agent that renders Frigate configuration from JSON, launches Frigate via Docker Compose, consumes Frigate MQTT events, normalizes them, and forwards them to a cloud API.

## Components
- **Edge Agent** (`akendon/edge/edge-agent/app`): Python 3.11 application using Pydantic models for configuration and events. It renders `frigate.yml` via Jinja2, manages Docker Compose startup, listens to Frigate MQTT events, normalizes them into the `EdgeEvent` schema, and posts to the cloud API.
- **Frigate** (`akendon/edge/frigate`): Holds the Jinja2 configuration template and rendered output. The Frigate UI is not exposed in Docker Compose to avoid public access.
- **MQTT**: Eclipse Mosquitto broker used for Frigate event publication.
- **Cloud API** (`akendon/cloud/cloud-api`): Minimal receiver endpoint for normalized events.
- **Docs** (`akendon/docs`): `edge-event-schema.json` defines the stable event schema.

## Docker Compose flow
1. The edge agent renders `frigate.yml` from `config.template.yml` using the JSON configuration.
2. `docker-compose.yml` starts the MQTT broker, Frigate, cloud API, and the edge agent (running in `--skip-compose` mode because Compose already started services). When running the edge agent outside Compose, omit `--skip-compose` so it will start Frigate itself.
3. Frigate publishes events to MQTT; the edge agent consumes them, normalizes to `EdgeEvent`, and posts to the cloud API.

## Swapping in a forked Frigate image
Change the `FRIGATE_IMAGE` environment variable used by `docker-compose.yml`. Example:
```bash
FRIGATE_IMAGE=ghcr.io/ourorg/frigate:edge docker compose -f akendon/edge/docker-compose.yml up -d
```

## Running locally (single RTSP camera)
```bash
cd akendon/edge
# Render config + start stack
EDGE_CONFIG_PATH=./edge-agent/app/sample_config.json docker compose up -d --build
```
- The sample config targets one Wyze RTSP camera (`rtsp://user:password@wyze-rtsp-stream/stream`).
- Frigate UI ports are not published; access is internal only.
- Cloud API is available at `http://localhost:8000/events` for debugging.

## Event normalization
Frigate events from MQTT are converted into the stable schema defined in `docs/edge-event-schema.json` before being sent to the cloud API.
