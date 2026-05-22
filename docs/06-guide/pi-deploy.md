# 라즈베리 파이 원샷 배포

집 안 Pi 한 대에서 **MQTT · 오케스트레이터 · 웹 대시보드**를 Docker Compose로 띄우는 방법입니다.

## 준비

- Raspberry Pi OS (64비트 권장), 인터넷 연결
- 저장소 클론 또는 `/opt/iot-home`에 코드 복사
- API 키: `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` (채팅·음성·비전)
- 운영 시 `BACKEND_API_TOKEN`을 `change-me`가 아닌 값으로 설정 (`APP_ENV`가 `local`이 아니면 필수)

## 1) 코드 받기

```bash
sudo mkdir -p /opt/iot-home
sudo git clone <저장소-URL> /opt/iot-home
cd /opt/iot-home
```

이미 클론한 폴더에서 작업해도 됩니다. 설치 스크립트는 기본 경로 `/opt/iot-home`을 씁니다.

## 2) 환경 파일 복사·수정

```bash
cd /opt/iot-home/deploy/env
cp backend.env.example backend.env
cp web.env.example web.env
```

`backend.env`에서 최소한 확인할 항목:

| 변수 | 설명 |
|------|------|
| `BACKEND_API_TOKEN` | API 인증 토큰 (웹의 `ORCHESTRATOR_TOKEN`과 동일하게 맞출 것) |
| `MQTT_*` | 브로커 주소·토픽 (Compose 안에서는 `mqtt` 호스트) |
| `HOME_ASSISTANT_*` | HA 연동 시 URL·토큰 |
| `CAMERA_DEVICE` | Pi 카메라 장치 경로 (예: `/dev/video0`) |
| `SCENE_FPS` | 장면 캡처 주기(초당 프레임, 예: `1`) |

`web.env`에서:

| 변수 | 설명 |
|------|------|
| `ORCHESTRATOR_URL` | Compose 기본값 `http://orchestrator:8080` 유지 |
| `ORCHESTRATOR_TOKEN` | `backend.env`의 `BACKEND_API_TOKEN`과 동일 |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | 대시보드 LLM 기능 |

## 3) Docker Compose로 직접 실행

```bash
cd /opt/iot-home/deploy/docker-compose
docker compose build
docker compose up -d
```

확인:

- 웹: `http://<Pi-IP>:3000`
- 오케스트레이터: `http://<Pi-IP>:8080/health`
- MQTT: `1883`

카메라를 컨테이너에 넘기려면 `deploy/docker-compose/docker-compose.yml`의 `orchestrator` 서비스에 있는 `devices` 주석을 해제하고, `backend.env`의 `CAMERA_DEVICE`를 실제 장치에 맞게 설정합니다.

## 4) systemd로 부팅 시 자동 기동 (권장)

한 번에 설치:

```bash
cd /opt/iot-home
sudo bash scripts/pi-install.sh
```

수동으로도 가능합니다:

```bash
sudo cp deploy/systemd/*.service deploy/systemd/*.target /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable iot-stack.target
sudo systemctl start iot-stack.target
```

동작 구조:

- `iot-docker.service` — `docker compose up -d` (전체 스택)
- `iot-orchestrator.service` — orchestrator(+mqtt) 기동 확인
- `iot-web.service` — web 기동 확인
- `iot-stack.target` — 위 유닛 묶음, 부팅 시 활성화

상태 확인:

```bash
sudo systemctl status iot-stack.target
docker compose -f /opt/iot-home/deploy/docker-compose/docker-compose.yml ps
```

중지:

```bash
sudo systemctl stop iot-stack.target
```

## 5) 업데이트

```bash
cd /opt/iot-home
git pull
cd deploy/docker-compose
docker compose build
docker compose up -d
# systemd 사용 시:
sudo systemctl restart iot-stack.target
```

## 문제 해결

| 증상 | 확인 |
|------|------|
| 백엔드가 바로 종료됨 | `APP_ENV`와 `BACKEND_API_TOKEN` (`change-me` 금지) |
| 웹에서 도구 호출 실패 | `web.env`의 `ORCHESTRATOR_TOKEN` = `backend.env` 토큰 |
| 카메라 없음 | `ls -l /dev/video*` · compose `devices` 주석 해제 |
| 빌드 느림 | Pi에서 첫 `docker compose build`는 10분 이상 걸릴 수 있음 |

자세한 비밀값·토폴로지: [docs/20_deployment.md](../20_deployment.md)
