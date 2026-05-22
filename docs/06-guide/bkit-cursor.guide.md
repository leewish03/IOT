# bkit × Cursor 사용 가이드

이 저장소는 [bkit-claude-code](https://github.com/popup-studio-ai/bkit-claude-code)를 `bkit/` 아래에 포함하고, Cursor Cloud Agent / IDE에서 동일한 워크플로를 쓸 수 있게 맞춰 두었습니다.

## 한 번만 설정

```bash
./scripts/setup-bkit-cursor.sh
```

- `bkit/skills/*` → `.cursor/skills/*` 심볼릭 링크
- `bkit.config.json` 루트 심볼릭 링크
- `docs/01-plan` … `04-report` 디렉터리 생성

Cursor **Settings → MCP**에서 `.cursor/mcp.json`의 `bkit-pdca`, `bkit-analysis` 서버가 활성인지 확인하세요.

## Claude Code와의 차이

| Claude Code | Cursor |
|-------------|--------|
| `/pdca plan foo` | 채팅: "pdca plan foo" 또는 "기능 foo 계획서 작성해줘" |
| `/sprint start s1` | "sprint start s1" — 에이전트가 `bkit/skills/sprint/SKILL.md`를 읽고 진행 |
| 서브에이전트 자동 스폰 | **Task** 도구 + `AGENTS.md` / `bkit/agents/*.md` |
| 훅·플러그인 자동 실행 | 규칙 `.cursor/rules/bkit.mdc` + 스킬·MCP로 동등 동작 유도 |

## 추천 시작 순서

1. **단일 기능**: "pdca pm 로그인" → PM 분석 후 plan/design/do…
2. **여러 기능 릴리스**: "sprint master-plan Q2 --features auth,billing"
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

## IOT 프로젝트와 함께

애플리케이션 코드는 `bkit/` 밖에 두고, 기능 개발·검증·문서화만 bkit 워크플로를 사용하면 됩니다.

## 업스트림 업데이트

```bash
cd bkit && git pull   # submodule을 쓰는 경우
# 또는 popup-studio-ai/bkit-claude-code 에서 새 릴리스를 bkit/에 다시 복사
./scripts/setup-bkit-cursor.sh
```

라이선스: bkit은 Apache-2.0 (`bkit/LICENSE`).
