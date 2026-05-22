"""Render entrypoint when Start Command is `uvicorn main:app`.

Prefer Docker (backend/Dockerfile) or:
  uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
"""
from backend.app.main import app

__all__ = ["app"]
