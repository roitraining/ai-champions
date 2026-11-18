#!/usr/bin/env bash
# Runs the hook by hand with sample input. No model call and no Claude Code session needed.
# Usage: bash test_exit_codes.sh
here="$(cd "$(dirname "$0")" && pwd)"
hook="$here/project/.claude/hooks/block_rm.py"
py=python3; command -v python3 >/dev/null 2>&1 || py=python
blocked='{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf build"}}'
safe='{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"ls build"}}'
echo "--- dangerous command"
echo "$blocked" | $py "$hook"; echo "exit code: $?   (2 blocks, 1 does not)"
echo "--- safe command"
echo "$safe" | $py "$hook"; echo "exit code: $?   (0 lets it run)"
