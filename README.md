# MCP IoT 홈 오케스트레이터

`iot_home_orchestrator_master_plan_v2.docx`에 정의된 MCP 기반 IoT 홈 오케스트레이터의
초기 구현 스캐폴드입니다.

## 구현된 내용

- 릴레이 2채널 상태 조회, 즉시 on/off, 중앙 예약 실행.
- 파일/mock 캘린더 어댑터, Naver 읽기 제한 명시, Google 어댑터 자리.
- Home Assistant 서비스 추상화를 통한 알람 생성과 프로필 변경.
- 마스터 문서의 계약을 반영한 MCP 스타일 Resource/Tool/Prompt 레지스트리.
- 모든 Tool 호출에 대한 감사 로그.
- 사용자가 직접 수정할 수 있는 YAML 정책 파일.
- Docker Compose/배포 템플릿과 엣지 영역 자리.
- `backend/app/schemas/json` 아래 JSON Schema 계약 파일.

핵심 서비스는 의존성을 가볍게 유지했으며 번들 Python 런타임으로 테스트할 수 있습니다.
FastAPI, uvicorn, paho-mqtt, PyYAML은 배포용 의존성으로 정리되어 있습니다.

## 빠른 검증

```powershell
& 'C:\Users\WISH\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest discover -s backend/tests
```

## 로컬 API 서버

먼저 의존성을 설치한 뒤 실행합니다.

```powershell
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
```

FastAPI가 설치되어 있지 않아도 핵심 오케스트레이터 모듈과 테스트는 동작합니다.

## 주요 기본값

- 시간대: `Asia/Seoul`
- 기본 릴레이 장치 ID: `relay_esp12e_room_a`
- 기본 백엔드 저장소: `./data`
- 기본 정책 경로: `./policies`
- Mock 캘린더 예시: `./data/calendar_events.example.json`
- 알람 출력 대상: Home Assistant script/service 추상화
- Naver Calendar: 읽기 연동 가능성 검토 대상으로 두며, MVP 읽기 fallback은 Google/file 어댑터입니다.
