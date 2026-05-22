# MVP 검증 완료 보고서

**기능**: `mvp-home-orchestrator`  
**일자**: 2026-05-22  
**상태**: ✅ MVP 구현·자동 검증 완료

## 범위 (MVP)

| 항목 | 상태 |
|------|------|
| MCP Resources 5종 | ✅ |
| MCP Tools 10종 (릴레이·캘린더·알람·시스템·자동화) | ✅ |
| MCP Prompts 5종 | ✅ |
| YAML 정책 검증 | ✅ |
| 감사 로그 (audit.jsonl) | ✅ |
| file 캘린더 어댑터 | ✅ |
| Naver 읽기 명시적 NotImplemented | ✅ |
| class_day_wakeup 자동화 (`automation.prepare_class_day`) | ✅ |
| Docker Compose 스캐폴드 | ✅ |

## 검증 실행

```bash
python3 scripts/verify_mvp.py
```

결과: **18 tests OK** (단위 15 + API 통합 3)

### 커버리지 요약

- 릴레이 on/off, 상태, 예약·만료 실행
- 캘린더 내일 조회 (Asia/Seoul 기준)
- 알람 생성·프로필 변경·next alarm 정렬
- 입력 검증·감사 로그
- 수업일 알람 자동 준비
- HTTP `/health`, `/tools`, `/tools/*`, `/resource`

## 미포함 (MVP 이후)

- Google Calendar 실연동 (자격 증명 필요)
- Naver Calendar 읽기 (유지보수 가능 API 확인 전)
- ESP12E 실펌웨어·MQTT 하드웨어 E2E
- Open WebUI MCP 전송 레이어 (계약은 `/tools` REST로 동일)

## 다음 단계 제안

1. `deploy/env/backend.env` 실값 채우고 Compose 기동
2. Home Assistant `script.iot_alarm_run` 연동
3. ESP12E MQTT 토픽 실장치 연결
