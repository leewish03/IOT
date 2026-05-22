#!/usr/bin/env bash
# Render production env checklist for Jarvis IoT Blueprint (render.yaml)
set -euo pipefail

cat <<'EOF'
Render env checklist — Jarvis IoT (render.yaml)

=== iot-orchestrator ===
| Variable            | Set by Blueprint | You must set |
|---------------------|------------------|--------------|
| APP_ENV             | production       | —            |
| CORS_ORIGINS        | default URL*     | Update to real dashboard URL after deploy |
| BACKEND_API_TOKEN   | generateValue    | —            |

* Production dashboard: https://iot-fl68.onrender.com (srv-d88dg2rbc2fs73eqisgg)

=== iot-dashboard (web) ===
| Variable                         | Set by Blueprint     | You must set (sync:false) |
|----------------------------------|----------------------|---------------------------|
| ORCHESTRATOR_URL                 | fromService hostport | —                         |
| ORCHESTRATOR_TOKEN               | fromService token    | —                         |
| NEXT_PUBLIC_SUPABASE_URL         | —                    | yes (Supabase API)        |
| NEXT_PUBLIC_SUPABASE_ANON_KEY    | —                    | yes                       |
| SUPABASE_SERVICE_ROLE_KEY        | —                    | yes (server secret)       |
| ANTHROPIC_API_KEY                | —                    | yes if using Haiku        |
| OPENAI_API_KEY                   | —                    | yes for nano/voice/vision |
| ANTHROPIC_HAIKU_MODEL            | default in yaml      | optional override         |
| ANTHROPIC_HAIKU_FALLBACK_MODEL   | default in yaml      | optional                  |
| OPENAI_NANO_MODEL                | default in yaml      | optional                  |
| OPENAI_NANO_FALLBACK_MODEL       | default in yaml      | optional                  |
| OPENAI_VISION_MODEL              | default in yaml      | optional                  |
| OPENAI_STT_MODEL                 | default in yaml      | optional                  |

=== iot-workflows ===
| Variable | Notes |
|----------|--------|
| (none in blueprint) | Add env in Dashboard if workflows need secrets |

=== Supabase (not Render env) ===
- Run: supabase db push (or SQL migrations in supabase/migrations/)
- Tables: user_settings, chat_messages, vision_events, scene_events

EOF
