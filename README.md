# IOT

IoT application workspace with **bkit** (AI Native Development OS) integrated for Cursor.

## bkit quick start

1. Run setup once:

```bash
./scripts/setup-bkit-cursor.sh
```

2. In Cursor chat (Korean or English), for example:

- `pdca pm my-feature` — PM 분석 후 PDCA 사이클
- `sprint master-plan release --features a,b,c` — 스프린트 마스터 플랜
- `bkit help` — 전체 스킬·에이전트 목록

3. Read the guide: [docs/06-guide/bkit-cursor.guide.md](docs/06-guide/bkit-cursor.guide.md)

## Layout

| Path | Purpose |
|------|---------|
| `bkit/` | Upstream toolkit (skills, agents, lib, MCP servers) |
| `.cursor/rules/bkit.mdc` | Always-on workflow rules |
| `.cursor/skills/` | Symlinks to `bkit/skills/*` (after setup) |
| `.cursor/mcp.json` | bkit-pdca + bkit-analysis MCP |
| `AGENTS.md` | Subagent index for Task tool |
| `docs/` | PDCA artifacts (Korean) |

Upstream: https://github.com/popup-studio-ai/bkit-claude-code
