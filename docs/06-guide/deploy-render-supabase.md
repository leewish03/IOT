# Render + Supabase production deploy

Jarvis dashboard (`web/`) on Render with optional Supabase persistence. Orchestrator runs as a sibling Render web service.

## Prerequisites

- Git repo on GitHub, GitLab, or Bitbucket (pushed to `main` or your deploy branch)
- [Supabase](https://supabase.com) account
- [Render](https://render.com) account
- Anthropic and/or OpenAI API keys (see `web/.env.example`)

## 1. Create a Supabase project

**이 저장소에 MCP로 연결·적용된 프로젝트 (2026-05-22):**

| 항목 | 값 |
|------|-----|
| 이름 | `persona-gospel` |
| Project ref | `wyqpcldqlyrqbppjdhhp` |
| API URL | `https://wyqpcldqlyrqbppjdhhp.supabase.co` |
| 적용 마이그레이션 | `jarvis_dashboard`, `jarvis_scene_events` + profiles 트리거·`vision_events.scene_json` |

다른 프로젝트를 쓰려면 아래 1번부터 새로 진행하세요.

1. [Supabase Dashboard](https://supabase.com/dashboard) → **New project** (pick region, set DB password).
2. Wait until the project is **Active**.
3. **Project Settings → API** — copy:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY` (server-only; never expose in client bundles)

## 2. Run database migrations

From the repo root (with [Supabase CLI](https://supabase.com/docs/guides/cli) installed):

```bash
supabase login
supabase link --project-ref <YOUR_PROJECT_REF>
supabase db push
```

Migrations live in `supabase/migrations/`:

- `user_settings`, `chat_messages`, `vision_events` (dashboard prefs + logs)
- `scene_events` (`scene_json` jsonb, `user_id`) for room/scene snapshots

Alternatively: **SQL Editor** in the dashboard → paste and run each migration file in order.

Verify tables: **Table Editor** should list `scene_events` with RLS enabled.

## 3. Deploy with Render Blueprint

1. Commit and push `render.yaml` to your Git remote.
2. Open a new Blueprint (replace with your HTTPS repo URL):

   `https://dashboard.render.com/blueprint/new?repo=https://github.com/<org>/<repo>`

3. Connect Git OAuth if prompted, review three services:
   - `iot-orchestrator` (Docker)
   - `iot-dashboard` (Node / Next.js)
   - `iot-workflows` (Python)
4. For env vars marked **sync: false**, Render will prompt empty values — you can skip and fill after **Apply**, or paste Supabase/API keys now.
5. Click **Apply** and wait for builds to finish.

### Blueprint wiring (`fromService`)

| Dashboard env | Source |
|---------------|--------|
| `ORCHESTRATOR_URL` | `iot-orchestrator` web service `hostport` |
| `ORCHESTRATOR_TOKEN` | `iot-orchestrator` env `BACKEND_API_TOKEN` (auto-generated) |

No manual copy of the orchestrator token is required if the Blueprint links succeed.

## 4. Set API keys and Supabase in Render

**iot-dashboard → Environment**:

| Variable | Required | Notes |
|----------|----------|--------|
| `NEXT_PUBLIC_SUPABASE_URL` | For DB persistence | From Supabase API settings |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | For DB persistence | Publishable key |
| `SUPABASE_SERVICE_ROLE_KEY` | Recommended server-side | Bypasses RLS for API routes; keep secret |
| `ANTHROPIC_API_KEY` | If using Haiku chat | |
| `OPENAI_API_KEY` | Nano chat, voice STT, vision | |
| `ANTHROPIC_HAIKU_MODEL` | Optional | Defaults in blueprint |
| `OPENAI_*_MODEL` | Optional | Model override vars |

Redeploy the dashboard after changing env vars.

Checklist script: `scripts/render-env-checklist.sh`

## 5. Connect orchestrator URL and CORS

1. **Production dashboard:** https://iot-fl68.onrender.com (`srv-d88dg2rbc2fs73eqisgg`). See `deploy/render-production.env.md`.
2. **Dashboard → iot-orchestrator → Environment**:
   - Set `CORS_ORIGINS` to that URL (comma-separated if you add more origins).
3. Confirm **iot-dashboard** has:
   - `ORCHESTRATOR_URL` populated (from Blueprint `fromService`)
   - `ORCHESTRATOR_TOKEN` matching orchestrator `BACKEND_API_TOKEN`
4. Smoke test: open the dashboard → manual relay / chat; browser network tab should call your orchestrator host without CORS errors.

## 6. Local parity

```bash
cp web/.env.example web/.env.local
# fill keys + ORCHESTRATOR_URL=http://127.0.0.1:8080
python3 -m uvicorn backend.app.main:app --port 8080
cd web && npm run dev
```

## Troubleshooting

| Symptom | Check |
|---------|--------|
| Chat 503 “API_KEY not configured” | `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` on `iot-dashboard` |
| Supabase errors | URL + keys; migrations applied; RLS policies |
| CORS / orchestrator 401 | `CORS_ORIGINS`, `ORCHESTRATOR_TOKEN` vs `BACKEND_API_TOKEN` |
| Blueprint validate | `render blueprints validate` (Render CLI) |

See also: [docs/20_deployment.md](../20_deployment.md), [render.yaml](../../render.yaml).
