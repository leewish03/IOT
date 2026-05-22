# Render Workflows — Jarvis IoT

> **Blueprint(`render.yaml`)에는 Workflow를 넣을 수 없습니다.** Dashboard에서 별도 Workflow 서비스를 만듭니다.

## 1. Workflow 서비스 생성

1. [Render Dashboard](https://dashboard.render.com) → **New** → **Workflow**
2. GitHub 저장소 `leewish03/IOT` 연결, 브랜치 `main`
3. **Root Directory:** `workflows`
4. **Language:** Python 3
5. **Build:** `pip install -r requirements.txt`
6. **Start:** `python main.py`

## 2. 환경 변수

| 변수 | 설명 |
|------|------|
| `ORCHESTRATOR_URL` | `iot-orchestrator` 공개 URL (https://…) |
| `ORCHESTRATOR_TOKEN` | Blueprint가 생성한 `BACKEND_API_TOKEN`과 동일 |
| `RENDER_API_KEY` | (선택) 다른 Workflow 호출 시 |

## 3. 등록된 태스크

| Task | 용도 |
|------|------|
| `iot-workflows/ping_orchestrator` | 오케스트레이터 헬스 |
| `iot-workflows/poll_scene_latest` | OpenCV 최신 장면 JSON |
| `iot-workflows/scene_motion_alert` | `motion=moving` 일 때만 alert payload |

Dashboard → Workflow → **Tasks** 탭에서 slug 확인.

## 4. 스케줄 (Cron)

Workflows에는 내장 스케줄이 없습니다. **Cron Job**을 추가하세요.

1. **New** → **Cron Job**
2. Schedule: `*/5 * * * *` (5분마다)
3. Root: `workflows`, Build/Start 동일
4. Start command 예:

```bash
python -c "from render_sdk import Render; r=Render(); print(r.workflows.run_task('iot-workflows/scene_motion_alert', []))"
```

`RENDER_API_KEY`와 Workflow slug는 실제 Dashboard 이름에 맞게 수정.

## 5. 로컬 테스트

```bash
cd workflows
pip install -r requirements.txt
export ORCHESTRATOR_URL=http://127.0.0.1:8080
render workflows dev -- python main.py
# 다른 터미널
render workflows tasks list --local
```

## MCP (Cursor)

Render MCP가 **unauthorized** 또는 **workspace not set**이면:

1. Cursor → MCP → **Render** 인증
2. 에이전트에게 **워크스페이스 선택** 요청 (`list_workspaces` 후 본인이 선택)

자동으로 워크스페이스를 고르지 않습니다 (다른 계정 리소스 손상 방지).
