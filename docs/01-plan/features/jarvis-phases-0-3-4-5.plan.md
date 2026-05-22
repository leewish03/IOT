# Jarvis Phases 0·3·4·5 — 계획

## Goal

대시보드에서 **수동 IoT 제어**, **채팅 명령**, **음성(Phase 3)**, **비전 판단(Phase 4)** 이 실제 동작하며, AI 모델 **Claude Haiku 4.6** / **GPT-5.4 nano** 선택 가능. Supabase + Render + shadcn 웹.

## Phase 정의

| Phase | 내용 | 완료 기준 |
|-------|------|-----------|
| **0** | 오케스트레이터 + HA 호출 + 환경 센서 리소스 + CORS | API·단위 테스트 통과 |
| **3** | STT → LLM 도구 호출 → 오케스트레이터 | `/api/voice` E2E, 채팅과 동일 도구 루프 |
| **4** | 이미지 → 비전 LLM → (선택) 도구 실행 | `/api/vision` E2E |
| **5** | shadcn 대시보드: 수동 스위치 + 채팅 + 음성 + 모델 선택 | Playwright/통합 테스트 또는 API 스모크 |

## 스택

- `backend/` FastAPI (24h Pi)
- `web/` Next.js + shadcn
- `supabase/migrations/` 인증·설정·채팅 로그
- `workflows/` Render Workflows (비전 배치, 선택)
- `render.yaml` Blueprint

## 비포함 (이번 Goal 이후)

- 실제 샤오미/IR 하드웨어 E2E (HA live + 토큰 필요)
- Open WebUI
