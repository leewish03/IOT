# 우리 집 IoT 도우미 (MCP 홈 오케스트레이터)

**한 줄 요약:** 스마트폰·AI·스케줄과 연결해, **전등(릴레이)**, **내일 일정**, **알람**을 한곳에서 안전하게 다루는 **집 안 “지휘 본부”** 프로그램입니다.

> 전공 지식이 없어도 괜찮습니다. 아래는 “이게 뭔지 → 뭘 해 주는지 → 폴더가 뭔지” 순서로 적었습니다.  
> 개발자용 설치·검증 명령은 맨 아래 **[개발자용]** 절에 모아 두었습니다.

---

## 이게 왜 필요한가요?

집에는 여러 기기가 있습니다.

- 방 전등을 켜고 끄는 **릴레이**
- 내일 수업·약속이 있는 **캘린더**
- 아침에 울리는 **알람** (Home Assistant 등과 연동)

각각 앱이 따로 있으면 “일정은 캘린더에 있는데 알람은 안 맞춰졌다” 같은 일이 생깁니다.  
이 프로젝트는 **한 서버가 중간에서 정리**해, AI나 자동화가 **같은 규칙**으로 명령하도록 만듭니다.

---

## 비유로 이해하기

| 비유 | 이 프로젝트에서 |
|------|------------------|
| **교통 정리 센터** | 서버(`backend`)가 “지금 전등 켜”, “내일 9시 수업 → 8시 30분 알람” 같은 요청을 받음 |
| **매뉴얼** | `policies/` 폴더의 YAML 파일 — “수업 있는 날은 알람을 세게” 같은 집 규칙 |
| **일기장** | `data/` — 일정 예시, 실행 기록(감사 로그) |
| **현장 직원** | `edge/` — 방 안 ESP12E·라즈베리 파이 등 (연결 예정) |
| **AI 비서 접수 창구** | MCP 스타일 API — 챗봇·Open WebUI가 “도구”를 호출하는 방식 |

**MCP**는 어려운 말이지만, 여기서는 **“AI가 쓸 수 있는 리모컨 버튼 목록”** 정도로 생각하시면 됩니다.  
예: `relay.turn_on`(전등 켜기), `calendar.get_tomorrow`(내일 일정 보기).

---

## 지금 이 버전(MVP)에서 할 수 있는 것

✅ **이미 동작·자동 테스트까지 통과한 것**

1. **전등(릴레이) 2채널** — 지금 켜기/끄기, 나중에 켜기 예약  
2. **내일 일정** — 파일에 적어 둔 일정 읽기 (실제 구글·네이버 연동은 다음 단계)  
3. **알람** — 시간·프로필(부드럽게/보통/강하게)로 만들기·바꾸기  
4. **수업일 준비** — 내일 “꼭 일어나야 하는 일정”이 있으면, 수업 시작 **30분 전** 알람 자동 제안  
5. **기록 남기기** — 누가 어떤 명령을 했는지 로그 (나중에 “왜 켜졌지?” 추적)  
6. **규칙 파일 검사** — `policies/` 안 설정이 깨지지 않았는지 확인  

⏳ **아직 “실제 집”까지는 손대지 않은 것** (설정·하드웨어 필요)

- 구글 캘린더 실시간 연동  
- 네이버 캘린더 읽기 (공식 API 한계로 MVP 제외)  
- ESP12E 보드에 실제 MQTT 연결  
- Open WebUI 화면에 버튼 붙이기  

자세한 체크리스트: [docs/04-report/features/mvp-verification.report.md](docs/04-report/features/mvp-verification.report.md)

---

## 어떻게 쓰나요? (일반 사용자 관점)

1. **서버를 켭니다** (아래 개발자용 “서버 실행” 참고, 또는 Docker).  
2. **AI나 앱**이 서버에 요청합니다.  
   - 예: “내일 수업 있으면 알람 잡아줘” → `automation.prepare_class_day`  
   - 예: “거실 전등 켜줘” → `relay.turn_on`  
3. 서버가 **규칙·일정·로그**를 보고 실행합니다. (실제 전등·HA는 배포 환경에 연결됨)

**일정 예시 파일:** `data/calendar_events.example.json` 을 참고해 `data/calendar_events.json` 에 내일 일정을 넣을 수 있습니다.

**집 규칙 예시:** `policies/automation_rules/class_day_wakeup.yaml` — “내일 must_wake 일정이 있으면 알람 관련 동작”

---

## 폴더 안내 (쉬운 말)

| 폴더 | 쉬운 설명 |
|------|-----------|
| `backend/` | **본부 프로그램** — 요청 받고 릴레이·일정·알람 처리 |
| `policies/` | **우리 집 규칙** — 알람 강도, 자동화, 릴레이 기본값 |
| `data/` | **데이터 저장소** — 일정 예시, 실행 로그 |
| `edge/` | **방 안 장치** 쪽 코드 자리 (ESP12E, 라즈베리 파이) |
| `deploy/` | **서버에 올릴 때** 쓰는 Docker 설정 |
| `webui/` | **채팅 UI**(Open WebUI) 연결 설정 |
| `docs/` | 설명서·기획·검증 보고 (한국어) |
| `bkit/` | **AI 개발 도구 상자** — Cursor에서 코딩할 때 쓰는 워크플로 (개발자용) |
| `scripts/` | 짧은 자동 스크립트 (예: MVP 검증) |

**긴 설계 문서:** `iot_home_orchestrator_master_plan_v2.docx` (원본 기획)

---

## 자주 묻는 질문

**Q. 코딩 모르는데 README만 봐도 되나요?**  
A. 네. 위 **“지금 할 수 있는 것”**과 **폴더 안내**만 보셔도 됩니다. 설치는 개발자나 Cursor 에이전트에게 “README 개발자용대로 서버 띄워줘”라고 요청하시면 됩니다.

**Q. MCP, FastAPI, YAML이 뭔가요?**  
A.  
- **MCP** → AI용 리모컨 API 목록  
- **FastAPI** → 서버 프로그램 종류  
- **YAML** → 사람이 읽기 쉬운 설정 파일 형식  

**Q. bkit은 뭔가요?**  
A. 이 저장소를 **Cursor로 개발할 때** AI가 계획·설계·검증 순서를 지키게 하는 도구입니다. 집 사용만 하실 때는 필수가 아닙니다.

**Q. 잘 돌아가는지 어떻게 확인하나요?**  
A. 개발자가 `python3 scripts/verify_mvp.py` 를 실행하면 **18개 자동 검사**가 돌아갑니다. “OK”면 MVP 기준 통과입니다.

---

## 개발자용

### 요구 사항

- Python 3.12+
- (선택) Docker — `deploy/docker-compose/` 로 전체 띄우기

### MVP 자동 검증

```bash
pip install -r requirements.txt
python3 scripts/verify_mvp.py
```

### 로컬에서 서버만 실행

```bash
pip install -r requirements.txt
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080
```

브라우저·curl 예:

```bash
curl http://127.0.0.1:8080/health
curl -X POST http://127.0.0.1:8080/tools/relay.turn_on \
  -H "Content-Type: application/json" \
  -d '{"channel":"ch1"}'
```

### 기본 설정값

| 항목 | 값 |
|------|-----|
| 시간대 | `Asia/Seoul` |
| 기본 릴레이 장치 | `relay_esp12e_room_a` |
| 데이터 | `./data` |
| 규칙 | `./policies` |

환경 변수 예시: `deploy/env/backend.env.example` → `backend.env` 복사 후 수정.

### MCP 계약 (도구 이름)

상세 목록: [docs/10_mcp_spec.md](docs/10_mcp_spec.md)

### bkit + Cursor

```bash
./scripts/setup-bkit-cursor.sh
```

- 가이드: [docs/06-guide/bkit-cursor.guide.md](docs/06-guide/bkit-cursor.guide.md)  
- upstream: https://github.com/popup-studio-ai/bkit-claude-code  

### 배포 메모

[docs/20_deployment.md](docs/20_deployment.md) · [docs/30_operations.md](docs/30_operations.md)

---

## Jarvis 대시보드 (Phase 0·3·4·5)

| 경로 | 내용 |
|------|------|
| `web/` | shadcn 대시보드 — 수동 제어, 채팅, 음성, 비전 |
| `supabase/migrations/` | 채팅·설정 DB (선택) |
| `render.yaml` | Render 배포 (orchestrator + dashboard + workflows) |

```bash
python3 -m uvicorn backend.app.main:app --port 8080   # 터미널 1
cp web/.env.example web/.env.local   # API 키
cd web && npm run dev                # 터미널 2 → http://localhost:3000
```

가이드: [docs/04-report/features/jarvis-phases-0-3-4-5.report.md](docs/04-report/features/jarvis-phases-0-3-4-5.report.md)

## 문의·다음 단계

1. `deploy/env/backend.env` 에 토큰·Home Assistant 주소 넣기  
2. 실제 릴레이·MQTT 연결 (`edge/`)  
3. `web/.env.local` 에 Anthropic/OpenAI 키 — 채팅·음성·비전 API

기능 추가·버그 수정은 Cursor에서 이 README와 `docs/` 를 함께 보면 됩니다.
