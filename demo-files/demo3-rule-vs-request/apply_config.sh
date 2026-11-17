#!/usr/bin/env bash
# Copies one of the demo configs into project/.claude/settings.json.
# Usage: bash apply_config.sh A|B|C|D      (then restart Claude Code in project/)
set -e
here="$(cd "$(dirname "$0")" && pwd)"
case "$1" in
  A) src=A-request-only.json ;;
  B) src=B-read-deny.json ;;
  C) src=C-deny-plus-sandbox.json ;;
  D) src=D-bypass-mode-test.json ;;
  *) echo "Usage: bash apply_config.sh A|B|C|D"; exit 2 ;;
esac
mkdir -p "$here/project/.claude"
sed "s#__PROJECT__#$here/project#g" "$here/configs/$src" > "$here/project/.claude/settings.json"
echo "Applied $src to $here/project/.claude/settings.json"
# A is the request alone, so CLAUDE.md must be present. B, C and D are about the rule, so
# CLAUDE.md is moved aside: with it present the model refuses before it ever calls a tool,
# and the rule is never exercised (measured on Opus 5.5 and Haiku 5.5, 2026-11-17).
proj="$here/project"
if [ "$1" = "A" ]; then
  [ -e "$proj/CLAUDE.md.off" ] && mv "$proj/CLAUDE.md.off" "$proj/CLAUDE.md" && echo "Restored CLAUDE.md (the request)."
else
  [ -e "$proj/CLAUDE.md" ] && mv "$proj/CLAUDE.md" "$proj/CLAUDE.md.off" && echo "Moved CLAUDE.md aside to CLAUDE.md.off, so only the rule is in play."
fi
echo "Restart Claude Code in $here/project and run /status to confirm."
