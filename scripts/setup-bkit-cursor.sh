#!/usr/bin/env bash
# Link bkit skills into .cursor/skills for Cursor discovery.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_SRC="$ROOT/bkit/skills"
SKILLS_DST="$ROOT/.cursor/skills"
mkdir -p "$SKILLS_DST"
for dir in "$SKILLS_SRC"/*/; do
  name="$(basename "$dir")"
  target="$SKILLS_DST/$name"
  ln -sfn "../../bkit/skills/$name" "$target"
done
# Root config symlink (optional)
if [[ ! -f "$ROOT/bkit.config.json" ]]; then
  ln -sfn bkit/bkit.config.json "$ROOT/bkit.config.json"
fi
mkdir -p "$ROOT/docs/01-plan/features" "$ROOT/docs/02-design/features" \
  "$ROOT/docs/03-analysis" "$ROOT/docs/04-report/features" "$ROOT/.bkit/state"
echo "Linked $(find "$SKILLS_DST" -maxdepth 1 -type l | wc -l) skills into .cursor/skills"
echo "Done. Enable MCP servers in Cursor Settings if not auto-loaded from .cursor/mcp.json"
