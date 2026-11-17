#!/usr/bin/env bash
# Summarizes the demo log. Needs jq.
# Usage: bash summarize_log.sh [logfile]
log="${1:-${CLAUDE_TOOL_LOG:-$HOME/claude-tool-calls.log}}"
[ -f "$log" ] || { echo "No log at $log yet."; exit 1; }
echo "Calls by tool:"
jq -r 'select(.event=="tool_call") | .tool' "$log" | sort | uniq -c | sort -rn
echo
echo "Blocked attempts (rule, command):"
jq -r 'select(.event=="blocked") | "\(.ts)  \(.rule)  \(.input.command)"' "$log"
echo
echo "Count of blocked pushes: $(jq -r 'select(.event=="blocked" and .rule=="no-push")' "$log" | grep -c '"rule"')"
