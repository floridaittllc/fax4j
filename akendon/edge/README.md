# Edge stack

This directory contains the edge stack combining Frigate, an MQTT broker, the edge agent, and a minimal cloud API receiver.

## Quickstart
1. Update `edge-agent/app/sample_config.json` with your RTSP credentials and MQTT values.
2. Render config + start services:
   ```bash
   cd akendon/edge
   EDGE_CONFIG_PATH=./edge-agent/app/sample_config.json docker compose up -d --build
   ```
3. The edge agent will listen on MQTT, normalize events, and forward them to the cloud API (`http://localhost:8000/events`).

## Notes
- Frigate UI ports are intentionally not published to avoid end-user access.
- Swap the Frigate image by setting `FRIGATE_IMAGE`, e.g. `FRIGATE_IMAGE=ghcr.io/ourorg/frigate:tag docker compose up -d`.
- If running the edge agent outside Docker, call:
  ```bash
  python -m app.main --config /opt/edge/config.json --cloud-url http://localhost:8000
  ```
  The agent will render `frigate.yml` and bring up services via Docker Compose unless `--skip-compose` is provided.
