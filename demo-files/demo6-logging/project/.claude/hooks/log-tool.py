#!/usr/bin/env python3
"""Python version of log-tool.sh, for machines without jq (a Windows laptop, for example).
Reads only tool_name and tool_input from stdin. Same log format as log-tool.sh."""
import datetime
import json
import os
import sys

log = os.environ.get("CLAUDE_TOOL_LOG") or os.path.join(os.path.expanduser("~"), "claude-tool-calls.log")
data = json.load(sys.stdin)
entry = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "event": "tool_call", "tool": data.get("tool_name"), "input": data.get("tool_input")}
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")
sys.exit(0)
