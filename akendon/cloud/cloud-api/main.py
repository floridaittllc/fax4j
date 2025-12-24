from __future__ import annotations

import json
import logging
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("cloud-api")

app = FastAPI(title="Edge Event Receiver")


@app.post("/events")
async def receive_event(request: Request) -> JSONResponse:
    payload: Dict = await request.json()
    LOGGER.info("Received EdgeEvent: %s", json.dumps(payload))
    return JSONResponse({"status": "ok"})


@app.get("/")
async def healthcheck() -> JSONResponse:
    return JSONResponse({"status": "healthy"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
