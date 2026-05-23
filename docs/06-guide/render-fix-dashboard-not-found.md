# Render — `{"detail":"Not Found"}` at `/`

## 원인

`https://iot-fl68.onrender.com` 은 **FastAPI 오케스트레이터(API)** 입니다.

- ✅ `https://iot-fl68.onrender.com/health` → `{"status":"ok"}`
- ❌ `https://iot-fl68.onrender.com/` → 예전에는 404 (API에 HTML 없음)

**집 Jarvis 대시보드(Next.js)** 는 **다른 Render Web Service** 이거나, 같은 URL을 **web** 으로 다시 배포해야 합니다.

---

## 해결 A — 대시보드 서비스 추가 (권장)

1. Render → **New** → **Web Service** → GitHub `leewish03/IOT`
2. 설정:

| 필드 | 값 |
|------|-----|
| Name | `iot-dashboard` (원하는 이름) |
| Root Directory | `web` |
| Runtime | Node |
| Build | `npm ci && npm run build` |
| Start | `npm run start` |

3. Environment:

```
ORCHESTRATOR_URL=https://iot-fl68.onrender.com
ORCHESTRATOR_TOKEN=<iot-fl68 의 BACKEND_API_TOKEN 과 동일>
NEXT_PUBLIC_SUPABASE_URL=https://wyqpcldqlyrqbppjdhhp.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<Supabase anon/publishable>
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

4. 배포 후 **대시보드 URL** (예: `https://iot-dashboard-xxxx.onrender.com`) 로 접속

5. **iot-fl68 (API)** Environment:

```
CORS_ORIGINS=https://iot-dashboard-xxxx.onrender.com
DASHBOARD_PUBLIC_URL=https://iot-dashboard-xxxx.onrender.com
```

6. Supabase Auth Redirect:

```
https://iot-dashboard-xxxx.onrender.com/auth/callback
```

(`iot-fl68` 이 API 전용이면 Supabase redirect는 **대시보드 URL**에만 넣습니다.)

---

## 해결 B — Blueprint (서비스 2개 한 번에)

1. Render → **New Blueprint** → repo `leewish03/IOT` → `render.yaml` Apply
2. `iot-orchestrator` URL + `iot-dashboard` URL 이 각각 생김
3. 브라우저는 **iot-dashboard** URL 사용

---

## 해결 C — Pi 오케스트레이터 + Render 대시보드만

| 위치 | 역할 |
|------|------|
| Raspberry Pi | `uvicorn` + `CAMERA_DEVICE` |
| Render `web` | Next.js 대시보드 |

`ORCHESTRATOR_URL=https://<Pi 공개 URL>` (또는 Tailscale 등)

---

## 확인

| URL | 기대 |
|-----|------|
| API `/health` | JSON ok |
| API `/` | 서비스 안내 JSON (코드 최신 배포 후) |
| Dashboard `/` | Jarvis 한국어 UI |
