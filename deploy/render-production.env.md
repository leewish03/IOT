# Render production — leewish03/IOT

## Deployed service

| 항목 | 값 |
|------|-----|
| Service ID | `srv-d88dg2rbc2fs73eqisgg` |
| Public URL | https://iot-fl68.onrender.com |
| Dashboard 링크 | https://dashboard.render.com/web/srv-d88dg2rbc2fs73eqisgg |

## Deploy 실패 수정 (`Could not import module "main"`)

로그에 `uvicorn main:app` 이 보이면 **오케스트레이터(Python)** 로 올린 상태입니다.

**Start Command (둘 중 하나):**

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

(루트 `main.py`가 `backend.app.main:app` 을 re-export 함)

**권장:**

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

**Next.js 대시보드**를 이 URL에 올리려면 서비스 타입이 달라야 합니다.

| 항목 | 값 |
|------|-----|
| Root Directory | `web` |
| Build Command | `npm ci && npm run build` |
| Start Command | `npm run start` |

오케스트레이터는 **Docker** (`render.yaml` → `iot-orchestrator`) 또는 루트 Python + 위 uvicorn 명령.

## Supabase Auth redirect

Supabase → **Authentication** → **URL configuration** → Redirect URLs:

```
https://iot-fl68.onrender.com/auth/callback
```

Site URL (선택): `https://iot-fl68.onrender.com`

## iot-dashboard 환경 변수 (이 서비스에 설정)

필수:

```
NEXT_PUBLIC_SUPABASE_URL=https://wyqpcldqlyrqbppjdhhp.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<Supabase Dashboard → API>
SUPABASE_SERVICE_ROLE_KEY=<아래 참고>
ANTHROPIC_API_KEY=<Anthropic>
OPENAI_API_KEY=<OpenAI>
```

Blueprint 연동 시 자동:

```
ORCHESTRATOR_URL=<iot-orchestrator 호스트>
ORCHESTRATOR_TOKEN=<BACKEND_API_TOKEN과 동일>
```

## iot-orchestrator (별도 서비스가 있을 때)

```
CORS_ORIGINS=https://iot-fl68.onrender.com
```

오케스트레이터 URL이 다르면 `ORCHESTRATOR_URL`을 그 주소로 맞춥니다.

## `SUPABASE_SERVICE_ROLE_KEY` 는 뭘 넣나요?

Supabase **서버 전용 비밀 키**입니다. RLS를 우회해 API 라우트에서 DB에 쓸 때 씁니다. **브라우저·GitHub에 올리지 마세요.**

1. [Supabase Dashboard](https://supabase.com/dashboard/project/wyqpcldqlyrqbppjdhhp/settings/api)
2. **Project API keys** 섹션
3. **`service_role`** (또는 **Secret key**) → **Reveal** → 복사
4. Render **iot-dashboard** → Environment → `SUPABASE_SERVICE_ROLE_KEY` 에 붙여넣기

`NEXT_PUBLIC_SUPABASE_ANON_KEY` 와 **다른 값**입니다.

- `anon` / publishable → 프론트(공개 가능)
- `service_role` → 서버만 (절대 `NEXT_PUBLIC_` 접두사 사용 금지)

현재 웹 앱은 대부분 **anon + 로그인 사용자 JWT**로 `chat_messages` 등에 저장하므로, Auth만 쓰면 service_role은 **선택**입니다. 나중에 관리자 배치·서버 전용 쓰기를 넣을 때 필요합니다.
