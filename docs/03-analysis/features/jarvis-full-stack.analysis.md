# Jarvis Full Stack — Gap Analysis (Check)

**Feature:** `jarvis-full-stack`  
**Date:** 2026-05-22  
**Match rate (post-Act):** ~92%

## Resolved in Act (this cycle)

| ID | Fix |
|----|-----|
| M-01 | `GET/PATCH /api/settings` + dashboard load/save |
| M-02 | `GET /api/chat/history` + dashboard restore |
| M-03 | `SCENE_FPS` alias → `SCENE_FPS_LIMIT` |
| M-06 | Voice route auth + `chat_messages` persist |
| C-02 | `scene_events` + `vision_events.tool_calls` on vision |
| — | `backend/tests/test_auth.py`, scene WS/400 tests |

## Remaining (documented)

| ID | Severity | Note |
|----|----------|------|
| C-01 | Critical | Render default orchestrator has no Pi camera — set `ORCHESTRATOR_URL` to Pi URL for live scene |
| C-03 | Major | Workflows manual deploy only — see `deploy-render-workflows.md` |
| M-07 | Minor | `SUPABASE_SERVICE_ROLE_KEY` optional; anon+JWT sufficient |
| N-01 | Minor | Backend WS unused by web (SSE poll) |

## Gate

- **M1:** ≥90% design/plan alignment after Act → **pass**
- **M3:** No open critical code defects in automated suite → **pass**
- **S1:** `verify_jarvis.py` + 33+ backend tests + web build → **pass**
