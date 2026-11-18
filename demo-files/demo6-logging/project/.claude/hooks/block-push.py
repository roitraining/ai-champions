#!/usr/bin/env python3
"""PreToolUse hook for Bash: block `git push` and write the decision to the same log.

Rule being proved: "Claude Code never pushes."  Decide: the charter. Enforce: this hook (exit 2). Prove: the log.
Reads only tool_name and tool_input from stdin.
"""
import datetime
import json
import os
import re
import sys

log = os.environ.get("CLAUDE_TOOL_LOG") or os.path.join(os.path.expanduser("~"), "claude-tool-calls.log")
data = json.load(sys.stdin)
command = (data.get("tool_input") or {}).get("command", "")
if re.search(r"\bgit\s+push\b", command):
    entry = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "event": "blocked", "rule": "no-push", "tool": data.get("tool_name"), "input": data.get("tool_input")}
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print("Blocked by the no-push rule. Claude Code does not push in this project. Commit locally and ask the user to push.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
