# Agents — bkit on Cursor

## Cloud Agent / default mandate

**Always use bkit proactively.** The user will not repeat "use bkit" each time.

- Start from `bkit/skills/pdca/SKILL.md` or `sprint/SKILL.md` based on task scope.
- Spawn parallel **Task** subagents by default for non-trivial work (do not wait for `/pdca team`).
- Enforce quality gates; use MCP `bkit-pdca` / `bkit-analysis` when status or metrics are needed.
- Opt-out only if the user explicitly asks to skip bkit or docs.

Project rules: `.cursor/rules/bkit.mdc` (`alwaysApply: true`).

---

Specialist personas live in `bkit/agents/`. In Cursor, spawn them with the **Task** tool (`subagent_type`: `generalPurpose` or `explore`) and paste the relevant agent file as the system prompt basis.

## Core orchestration

| Agent file | Role | When to use |
|------------|------|-------------|
| `pm-lead.md` | PM team lead | `/pdca pm`, discovery, PRD |
| `cto-lead.md` | Architecture options | design phase, 3 options |
| `gap-detector.md` | Design vs code gap | analyze, iterate, M1 gate |
| `pdca-iterator.md` | Auto-repair loops | iterate phase |
| `qa-lead.md` | QA team | `/pdca qa`, L1–L5 |
| `report-generator.md` | Completion reports | report phase |
| `sprint-master-planner.md` | Release master plan | `/sprint master-plan` |
| `sprint-orchestrator.md` | Sprint lifecycle | `/sprint start` |
| `code-analyzer.md` | Static/deep analysis | M3 gate, reviews |

## Specialists (parallel)

`developer` patterns: use `frontend-architect.md`, `security-architect.md`, `infra-architect.md`, `bkend-expert.md`, `enterprise-expert.md` as needed.

PM sub-agents: `pm-discovery.md`, `pm-strategy.md`, `pm-research.md`, `pm-prd.md`.

QA sub-agents: `qa-strategist.md`, `qa-test-planner.md`, `qa-test-generator.md`, `qa-debug-analyst.md`, `qa-monitor.md`.

## How to invoke

1. Read `bkit/skills/<workflow>/SKILL.md` for the current phase.
2. If the skill lists `agents:`, open the mapped file under `bkit/agents/`.
3. Task prompt template: *"You are {name} from bkit. Follow the agent definition below. Workspace root is the repo root; docs in docs/; config in bkit.config.json."* + agent body.

Full catalog: `bkit/skills/bkit/SKILL.md` and `bkit/commands/bkit.md`.
