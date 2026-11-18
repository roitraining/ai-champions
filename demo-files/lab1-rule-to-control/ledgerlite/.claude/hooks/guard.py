#!/usr/bin/env python3
"""PreToolUse hook for Bash. Rule 1: no pushes, no forced deletes.

Starter version. It has bugs. Read it, test it by hand, fix it:

    echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' | python3 .claude/hooks/guard.py; echo $?
"""
import json
import re
import sys

data = json.load(sys.stdin)
command = (data.get("tool_input") or {}).get("command", "")

if re.match(r"git push", command) or re.search(r"rm -rf", command):
    print("Blocked by team rule 1.", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
