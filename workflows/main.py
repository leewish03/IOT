"""Render Workflows — Jarvis IoT background tasks.

Deploy: Render Dashboard → New → Workflow (NOT via render.yaml Blueprint).
Root directory: workflows/
Build: pip install -r requirements.txt
Start: python main.py

Env: ORCHESTRATOR_URL, ORCHESTRATOR_TOKEN, optional IOT_DASHBOARD_URL
"""
from __future__ import annotations

import logging
import os

from render_sdk import Workflows

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Workflows(default_timeout=300)


def _orchestrator_headers() -> dict[str, str]:
    token = os.environ.get("ORCHESTRATOR_TOKEN", "")
    headers: dict[str, str] = {}
    if token and token != "change-me":
        headers["Authorization"] = f"Bearer {token}"
    return headers


@app.task
def ping_orchestrator() -> dict:
    """Health check for Pi/cloud orchestrator."""
    import httpx

    url = os.environ.get("ORCHESTRATOR_URL", "http://127.0.0.1:8080").rstrip("/")
    response = httpx.get(f"{url}/health", headers=_orchestrator_headers(), timeout=15)
    response.raise_for_status()
    return response.json()


@app.task
def poll_scene_latest() -> dict:
    """Fetch latest OpenCV scene snapshot (no image to LLM)."""
    import httpx

    url = os.environ.get("ORCHESTRATOR_URL", "http://127.0.0.1:8080").rstrip("/")
    response = httpx.get(f"{url}/scene/latest", headers=_orchestrator_headers(), timeout=30)
    if response.status_code == 404:
        return {"scene": None, "message": "No snapshot yet — enable CAMERA_DEVICE on orchestrator"}
    response.raise_for_status()
    scene = response.json()
    logger.info("scene person_count=%s motion=%s", scene.get("person_count"), scene.get("motion"))
    return {"scene": scene}


@app.task
def scene_motion_alert() -> dict:
    """Return scene when global motion detected (for cron / notifications)."""
    result = poll_scene_latest()
    scene = result.get("scene")
    if not scene:
        return result
    if scene.get("motion") == "moving":
        return {"alert": True, "summary_ko": scene.get("summary_ko"), "scene": scene}
    return {"alert": False, "scene": scene}


if __name__ == "__main__":
    app.start()
