#!/usr/bin/env python3
"""PreToolUse hook for Bash: stop a recursive force delete.

THIS IS THE FIXED VERSION. It prints the message and exits with 2.
Exit code 2 is a blocking error: the command does not run, and the message on stderr goes back to Claude.
"""
import json
import re
import sys

data = json.load(sys.stdin)
command = (data.get("tool_input") or {}).get("command", "")
if re.search(r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r", command):
    print("Blocked: recursive force delete is not allowed here. Delete files one at a time, or ask the user.", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
