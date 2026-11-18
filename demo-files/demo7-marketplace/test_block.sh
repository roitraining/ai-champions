#!/usr/bin/env bash
# Runs the branch-guard hook by hand with sample input. No model call and no Claude Code session needed.
# Usage: bash test_block.sh
here="$(cd "$(dirname "$0")" && pwd)"
hook="$here/champions-tools/plugins/branch-guard/scripts/block_force_push.py"
py=python3; command -v python3 >/dev/null 2>&1 || py=python
try() {
  echo "--- $1"
  printf '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"%s"}}' "$1" | $py "$hook"
  echo "exit code: $?   ($2)"
}
try "git push --force origin main" "2 blocks"
try "git push origin main" "2 blocks"
try "git push origin feature/login" "0 lets it run"
try "git status" "0 lets it run"
