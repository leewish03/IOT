# Render production — leewish03/IOT

## Deployed service (dashboard)

| 항목 | 값 |
|------|-----|
| Service ID | `srv-d88dg2rbc2fs73eqisgg` |
| Public URL | https://iot-fl68.onrender.com |
| Dashboard 링크 | https://dashboard.render.com/web/srv-d88dg2rbc2fs73eqisgg |

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
SUPABASE_SERVICE_ROLE_KEY=<service_role — 비밀>
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
