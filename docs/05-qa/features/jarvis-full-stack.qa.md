# Jarvis Full Stack — QA Report

**Date:** 2026-05-22  
**Environment:** CI workspace (Python 3.12, Node 20)

## L1 Unit — Backend

| Suite | Tests | Result |
|-------|------:|--------|
| `backend/tests/test_orchestrator.py` | 15 | PASS |
| `backend/tests/test_api.py` | 3 | PASS |
| `backend/tests/test_scene.py` | 14 | PASS |
| `backend/tests/test_auth.py` | 4 | PASS |

**Command:** `python3 scripts/verify_mvp.py` (includes discover)

## L2 Integration — Scene API

| Case | Result |
|------|--------|
| POST `/scene/analyze` PNG | PASS |
| GET `/scene/latest` 404 → 200 | PASS |
| Empty upload → 400 | PASS |
| WS `/ws/scene` after analyze | PASS |
| Bearer auth when token set | PASS |

## L3 Contract — MCP tools

| Tool | Result |
|------|--------|
| `scene.analyze`, `scene.get_latest` | PASS |
| `relay.turn_on`, `sensor.get_environment` | PASS |

## L4 System — Web build

| Check | Result |
|-------|--------|
| `npm run build` | PASS |
| Routes: chat, voice, vision, scene/*, auth, settings, chat/history | Present |

## L5 E2E (manual / optional)

| Case | Command | Notes |
|------|---------|-------|
| Orchestrator smoke | `python3 scripts/e2e_smoke.py` | Requires uvicorn :8080 |
| Web proxy | same + `npm run dev` | `/api/orchestrator/tool?action=health` |
| Production | https://iot-fl68.onrender.com/health | User-deployed |

## Regression gate

```bash
python3 scripts/verify_jarvis.py
```

Expected: 33 backend tests OK, web build OK.

## Not in automated scope

- Live LLM API (keys required)
- Pi camera hardware
- Render MCP deploy
- Supabase Auth browser flow
