"""Render Workflows — optional vision poll (calls web vision API)."""
from __future__ import annotations

import os

from render_sdk import Render, task


@task
def ping_orchestrator() -> dict:
    import httpx

    url = os.environ.get("ORCHESTRATOR_URL", "http://127.0.0.1:8080")
    response = httpx.get(f"{url.rstrip('/')}/health", timeout=15)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    Render().run()
