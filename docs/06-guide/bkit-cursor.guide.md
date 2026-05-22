# bkit × Cursor 사용 가이드

이 저장소는 [bkit-claude-code](https://github.com/popup-studio-ai/bkit-claude-code)를 `bkit/` 아래에 포함하고, **MCP IoT 홈 오케스트레이터** 앱 코드와 함께 Cursor에서 동작하도록 맞춰 두었습니다.

## "매번 bkit 써줘" 말 안 해도 되게 — 프롬프트 저장 위치

| 저장 위치 | 용도 | 이 프로젝트 |
|-----------|------|-------------|
| **`.cursor/rules/*.mdc`** + `alwaysApply: true` | 이 repo를 열 때 **항상** 적용되는 프로젝트 규칙 | ✅ `.cursor/rules/bkit.mdc` (적극 활용·병렬 Task·게이트 강제) |
| **`AGENTS.md`** (repo 루트) | Cloud Agent / Agent 모드 기본 지시 | ✅ 루트 `AGENTS.md` |
| **Cursor Settings → Rules** | 모든 프로젝트 공통 **사용자 규칙** | 선택 |
| **`.cursor/skills/`** | 스킬 정의 (호출 가능한 워크플로) | ✅ `bkit/skills` 링크 44개 |
| ~~채팅에 매번 붙이기~~ | 비추천 | 규칙 파일로 대체함 |

**플러그인/마켓플레이스 설치가 아님** — 위 파일들이 "항상 켜진 프롬프트" 역할을 합니다.

## 한 번만 설정

```bash
./scripts/setup-bkit-cursor.sh
```

- `bkit/skills/*` → `.cursor/skills/*` 심볼릭 링크
- `bkit.config.json` 루트 심볼릭 링크
- `docs/01-plan` … `04-report` 디렉터리 생성

Cursor **Settings → MCP**에서 `.cursor/mcp.json`의 `bkit-pdca`, `bkit-analysis` 서버가 활성인지 확인하세요.

## IoT 앱 디렉터리 (bkit 밖)

| 경로 | 내용 |
|------|------|
| `backend/app/` | 오케스트레이터, MCP 레지스트리, 릴레이·캘린더·HA |
| `policies/` | YAML 정책 |
| `edge/` | ESP12E, Pi 에이전트 |
| `deploy/` | Docker Compose |
| `webui/` | Open WebUI 설정 |

기능 개발 시 bkit으로 `docs/`에 계획·설계를 쓰고, 코드는 위 경로에 반영합니다.

## Claude Code와의 차이

| Claude Code | Cursor |
|-------------|--------|
| `/pdca plan foo` | 채팅: "pdca plan foo" 또는 "기능 foo 계획서 작성해줘" |
| `/sprint start s1` | "sprint start s1" — 에이전트가 `bkit/skills/sprint/SKILL.md`를 읽고 진행 |
| 서브에이전트 자동 스폰 | **Task** 도구 + `AGENTS.md` / `bkit/agents/*.md` |
| 훅·플러그인 자동 실행 | 규칙 `.cursor/rules/bkit.mdc` + 스킬·MCP로 동등 동작 유도 |

## 추천 시작 순서

1. **단일 기능**: "pdca pm 릴레이-예약" → PM 분석 후 plan/design/do…
2. **여러 기능 릴리스**: "sprint master-plan Q2 --features relay,calendar,ha-alarm"
3. **자동화 수준**: "control level 2" (기본: L2 반자동)

## 문서 위치

| 단계 | 경로 |
|------|------|
| 계획 | `docs/01-plan/features/{feature}.plan.md` |
| 설계 | `docs/02-design/features/{feature}.design.md` |
| 갭 분석 | `docs/03-analysis/{feature}.analysis.md` |
| 완료 보고 | `docs/04-report/features/{feature}.report.md` |

## 품질 게이트 (요약)

- **M1** 설계-구현 일치율 90% 미만 → `iterate` (최대 5회)
- **M3** critical 이슈 → 중단 후 사용자 결정
- **S1** dataFlow 85% 미만 → 7-hop 재검증

자세한 내용: `bkit/README.md`, `bkit/README-FULL.md`.

## 업스트림 업데이트

```bash
# popup-studio-ai/bkit-claude-code 새 릴리스를 bkit/에 반영 후
./scripts/setup-bkit-cursor.sh
```

라이선스: bkit은 Apache-2.0 (`bkit/LICENSE`).
