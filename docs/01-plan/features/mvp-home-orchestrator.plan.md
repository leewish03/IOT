# MVP Home Orchestrator — 계획

## 목표

마스터 문서(`iot_home_orchestrator_master_plan_v2.docx`) 기준 **MVP**: MCP 계약 표면, 릴레이·캘린더·알람·예약·감사, file 캘린더, 정책 YAML, 로컬/Docker 검증.

## 완료 기준

- [x] `docs/10_mcp_spec.md` Tools/Resources 구현
- [x] `python3 scripts/verify_mvp.py` 전체 통과
- [x] `automation.prepare_class_day` (class_day_wakeup 정책 반영)
- [x] FastAPI REST (`/health`, `/tools`, `/resources`)

## 아키텍처

- `Orchestrator` — 도메인 조합
- Adapters — relay, calendar, MQTT, Home Assistant
- `McpCatalogServer` — MCP 계약 노출 (SDK 비의존)
