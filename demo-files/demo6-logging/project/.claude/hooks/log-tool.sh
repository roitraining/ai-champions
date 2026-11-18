#!/bin/bash
# PostToolUse logging hook. Reads only tool_name and tool_input from stdin.
# Needs jq. Log file: $CLAUDE_TOOL_LOG, or ~/claude-tool-calls.log.
log="${CLAUDE_TOOL_LOG:-$HOME/claude-tool-calls.log}"
jq -c '{ts: (now | todate), event: "tool_call", tool: .tool_name, input: .tool_input}' >> "$log"
exit 0
