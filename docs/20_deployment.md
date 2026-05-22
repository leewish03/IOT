# 배포 메모

## 기본 토폴로지

- Raspberry Pi: Home Assistant와 현장 장치/엣지 책임.
- Ubuntu 서버: Open WebUI, Custom MCP/Orchestrator 백엔드, MQTT broker, reverse proxy.
- ESP12-E: 릴레이 2채널, 상태 보고, 명령 수신 확인.

## 필요한 비밀값

- `BACKEND_API_TOKEN`
- broker 인증을 켠 경우 `MQTT_USERNAME` / `MQTT_PASSWORD`
- `HOME_ASSISTANT_TOKEN`
- 캘린더 provider 자격 증명

## Docker Compose 실행 전 준비

`deploy/env/backend.env.example`을 `deploy/env/backend.env`로 복사한 뒤 실제 값으로 수정합니다.
`APP_ENV`가 `local`이 아니면 `BACKEND_API_TOKEN=change-me` 상태로는 백엔드가 시작되지 않습니다.

로컬 개발 MQTT는 익명 접속을 허용하는 단순 Mosquitto 구성을 사용합니다. 운영 환경에서는
Mosquitto 설정 파일과 계정 파일을 별도로 마운트하고, 백엔드의 `MQTT_USERNAME` /
`MQTT_PASSWORD` 값을 함께 설정해야 합니다.

## Naver Calendar 결정

MVP는 Naver 어댑터 경계를 유지하지만, 유지 가능한 읽기 경로가 확인되기 전까지는
Naver를 동작하는 읽기 원천으로 취급하지 않습니다. 공식 공개 Calendar Open API 문서는
일정 생성 중심이므로, MVP 읽기 fallback은 로컬에서는 file/mock, 운영에서는 Google
Calendar로 둡니다.
