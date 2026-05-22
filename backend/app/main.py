from __future__ import annotations

import os
from typing import Any

from .config import Settings
from .mcp_server import McpCatalogServer
from .services.orchestrator import Orchestrator

settings = Settings.from_env()
settings.validate_security()
orchestrator = Orchestrator(settings)
mcp_catalog = McpCatalogServer(orchestrator)

try:
    from fastapi import FastAPI, Header, HTTPException
except ImportError:  # pragma: no cover - deployment dependency path
    FastAPI = None  # type: ignore
    app = None
else:
    app = FastAPI(title="MCP IoT Home Orchestrator", version="0.1.0")

    try:
        from fastapi.middleware.cors import CORSMiddleware

        origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[o.strip() for o in origins if o.strip()],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    except ImportError:
        pass

    def _authorize(authorization: str | None) -> None:
        expected = f"Bearer {settings.backend_api_token}"
        if settings.backend_api_token == "change-me":
            return
        if authorization != expected:
            raise HTTPException(status_code=401, detail="Invalid backend token")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "env": settings.env}

    @app.get("/resources")
    def list_resources() -> list[dict[str, str]]:
        return mcp_catalog.list_resources()

    @app.get("/resources/{resource_path:path}")
    def read_resource(resource_path: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
        _authorize(authorization)
        uri = resource_path.replace("/", "://", 1) if "://" not in resource_path else resource_path
        try:
            return mcp_catalog.read_resource(uri)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/resource")
    def read_resource_by_uri(uri: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
        _authorize(authorization)
        try:
            return mcp_catalog.read_resource(uri)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/tools")
    def list_tools() -> list[dict[str, Any]]:
        return mcp_catalog.list_tools()

    @app.post("/tools/{tool_name}")
    def call_tool(
        tool_name: str,
        payload: dict[str, Any],
        authorization: str | None = Header(default=None),
    ) -> dict[str, Any]:
        _authorize(authorization)
        result = mcp_catalog.call_tool(tool_name, payload)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result

    @app.get("/prompts")
    def list_prompts() -> list[dict[str, str]]:
        return mcp_catalog.list_prompts()

    @app.get("/prompts/{name}")
    def get_prompt(name: str) -> dict[str, str]:
        try:
            return mcp_catalog.get_prompt(name)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
