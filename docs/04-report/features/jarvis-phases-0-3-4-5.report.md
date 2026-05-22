# Jarvis Phases 0·3·4·5 — 완료 보고

**상태:** 구현·빌드·백엔드 스모크 검증 완료  
**Goal:** 대시보드에서 수동 제어 + 채팅 + 음성(Phase 3) + 비전(Phase 4), 모델 선택

## Phase 0 ✅

- `ha.call_service`, `sensor.get_environment`, `sensor.set_environment`
- Resource `home://sensors/environment`
- CORS (`CORS_ORIGINS`)
- 단위 테스트 19건 OK

## Phase 3 ✅ (코드·API)

- `POST /api/chat` — OpenAI / Anthropic HTTP tool loop
- `POST /api/voice` — Whisper STT → agent
- 대시보드: 채팅 입력, 4초 음성 버튼

**실사용:** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` 설정 필요

## Phase 4 ✅ (코드·API)

- `POST /api/vision` — 이미지 분석, `autoAct` 시 도구 실행
- 대시보드: 이미지 업로드 탭

## Phase 5 ✅

- Next.js + shadcn `HomeDashboard`
- 모델 (**2026-05 기준**): **Claude Haiku 4.6** → API `claude-haiku-4-6` (미개통 시 `claude-haiku-4-5-20251001`), **GPT-5.4 nano** → `gpt-5.4-nano` (스냅샷 `gpt-5.4-nano-2026-03-17`)
- Supabase migration: `supabase/migrations/20260522100000_jarvis_dashboard.sql`
- Render: `render.yaml` (orchestrator, dashboard, workflows)

## 검증 명령

```bash
# 백엔드
python3 scripts/verify_mvp.py

# 웹 빌드
cd web && npm run build

# 통합 (오케스트레이터 실행 중)
python3 -m uvicorn backend.app.main:app --port 8080 &
python3 scripts/e2e_smoke.py

# 전체
python3 scripts/verify_jarvis.py
```

## 로컬 실행

```bash
# 터미널 1
python3 -m uvicorn backend.app.main:app --reload --port 8080

# 터미널 2
cp web/.env.example web/.env.local  # API 키 입력
cd web && npm run dev
```

브라우저: http://localhost:3000

## 미검증 (키·하드웨어 필요)

- 실제 LLM/STT/비전 API 호출 (키 없으면 503)
- Supabase Auth UI
- Home Assistant live, 샤오미, IR
