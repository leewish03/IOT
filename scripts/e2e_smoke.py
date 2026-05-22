#!/usr/bin/env python3
"""Smoke test orchestrator + optional web (requires servers running)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

ORCH = os.environ.get("ORCHESTRATOR_URL", "http://127.0.0.1:8080")
WEB = os.environ.get("WEB_URL", "http://127.0.0.1:3000")


def get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode())


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"error": body}


def main() -> int:
    errors: list[str] = []

    try:
        health = get(f"{ORCH}/health")
        assert health.get("status") == "ok", health
        print("OK orchestrator health")
    except Exception as exc:
        errors.append(f"orchestrator health: {exc}")

    try:
        status, body = post_json(f"{ORCH}/tools/relay.turn_on", {"channel": "ch1"})
        assert status == 200 and body.get("success"), body
        print("OK relay.turn_on")
    except Exception as exc:
        errors.append(f"relay: {exc}")

    try:
        status, body = post_json(f"{ORCH}/tools/sensor.get_environment", {})
        assert status == 200 and body.get("success"), body
        print("OK sensor.get_environment")
    except Exception as exc:
        errors.append(f"sensor: {exc}")

    try:
        get(f"{WEB}/api/orchestrator/tool?action=health")
        print("OK web proxy health (web server running)")
        models = get(f"{WEB}/api/models")
        assert "models" in models, models
        print("OK web /api/models")
    except Exception as exc:
        print(f"SKIP web (start: cd web && npm run dev): {exc}")

    if errors:
        print("FAILURES:", file=sys.stderr)
        for item in errors:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print("Smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
