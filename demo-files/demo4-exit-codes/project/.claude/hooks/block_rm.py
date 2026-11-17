#!/usr/bin/env python3
"""PreToolUse hook for Bash: stop a recursive force delete.

THIS IS THE BROKEN VERSION. It prints the right message and then exits with 1.
Exit code 1 is a non-blocking error: the command still runs.
Fix: make it exit with 2.
"""
import json
import re
import sys

data = json.load(sys.stdin)
command = (data.get("tool_input") or {}).get("command", "")
if re.search(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r", command):
    print("Blocked: recursive force delete is not allowed here. Delete files one at a time, or ask the user.", file=sys.stderr)
    sys.exit(1)
sys.exit(0)
