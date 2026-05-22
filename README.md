# MCP IoT 홈 오케스트레이터

`iot_home_orchestrator_master_plan_v2.docx`에 정의된 MCP 기반 IoT 홈 오케스트레이터의 초기 구현 스캐폴드입니다.

개발 워크플로는 **bkit** (PDCA, Sprint, 품질 게이트)을 기본으로 사용합니다. 별도로 "bkit 써줘"라고 말하지 않아도 `.cursor/rules/bkit.mdc`가 항상 적용됩니다.

## 구현된 내용

- 릴레이 2채널 상태 조회, 즉시 on/off, 중앙 예약 실행
- 파일/mock 캘린더 어댑터, Naver 읽기 제한 명시, Google 어댑터 자리
- Home Assistant 서비스 추상화를 통한 알람 생성과 프로필 변경
- MCP 스타일 Resource/Tool/Prompt 레지스트리, Tool 호출 감사 로그
- YAML 정책 (`policies/`), Docker Compose (`deploy/`), 엣지 (`edge/`)
- `backend/app/schemas/json` JSON Schema 계약

## 빠른 검증

```bash
python -m unittest discover -s backend/tests
```

## 로컬 API 서버

```bash
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
```

## 주요 기본값

- 시간대: `Asia/Seoul`
- 기본 릴레이: `relay_esp12e_room_a`
- 데이터: `./data`, 정책: `./policies`

## 레포 구조

| Path | Purpose |
|------|---------|
| `backend/` | FastAPI 오케스트레이터 |
| `policies/` | 릴레이·알람·자동화 YAML |
| `edge/` | ESP12E, Pi 에이전트 |
| `deploy/` | Docker Compose |
| `webui/` | Open WebUI 설정 |
| `bkit/` | AI 개발 키트 (스킬, 에이전트, MCP) |
| `docs/` | bkit PDCA 문서 (한국어) |

## bkit (Cursor)

```bash
./scripts/setup-bkit-cursor.sh
```

- 가이드: [docs/06-guide/bkit-cursor.guide.md](docs/06-guide/bkit-cursor.guide.md)
- 예: `pdca plan relay-scheduler`, `sprint master-plan release --features a,b`

Upstream bkit: https://github.com/popup-studio-ai/bkit-claude-code
