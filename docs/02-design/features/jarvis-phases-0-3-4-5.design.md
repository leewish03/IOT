# Jarvis Phases 0·3·4·5 — 설계

## 아키텍처

```
[Browser Dashboard] ──Next API──► [LLM API] + [Orchestrator REST]
       │                              │
       │ chat / voice / vision        │ tools (relay, alarm, ha, sensor)
       └──────────────────────────────┴──► [FastAPI backend @ Pi/Render]
```

## Phase 0

- Tools: `ha.call_service`, `sensor.get_environment`, `sensor.set_environment`
- Resource: `home://sensors/environment`
- CORS for `web` origin

## Phase 3

- `POST /api/chat` — Anthropic/OpenAI tool loop → orchestrator
- `POST /api/voice` — Whisper STT → same agent loop

## Phase 4

- `POST /api/vision` — vision model analysis; optional `autoAct` → agent tools

## Phase 5

- shadcn `HomeDashboard`: tabs 수동 / 채팅 / 비전
- Model select: `claude-haiku-4.6`, `gpt-5.4-nano`

## Supabase

- `chat_messages`, `user_settings`, `vision_events` + RLS

## Render

- `render.yaml`: orchestrator (docker), dashboard (node), workflows (python ping)
