#!/usr/bin/env python3
"""Credential smell scanner for Demo 10. Reads files, runs nothing, sends nothing.

Usage: python3 smell_scan.py lakeside-api

It looks for five smells:
  1. a key or token written into a file (a FAKE-... placeholder here)
  2. an apiKeyHelper script that only echoes a fixed value
  3. a .env file with no Read deny rule covering it
  4. a secret name that sounds shared (ORG_WIDE, SHARED) or an inventory row with no expiry
  5. a CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY set in a script or settings file
A scan finds patterns. It cannot tell you who owns a credential or whether it was rotated.
"""
import json
import os
import re
import sys

SKIP = {".git", "__pycache__"}
KEY_VALUE = re.compile(r"(FAKE-(?:KEY|TOKEN|PASSWORD)-DO-NOT-USE[\w-]*|sk-ant-[A-Za-z0-9_-]{8,})")
SET_VAR = re.compile(r"(CLAUDE_CODE_OAUTH_TOKEN|ANTHROPIC_API_KEY)\s*[=:]\s*[\"']?(?!\$\{\{)(?!\$)[^\s\"']+")
SHARED = re.compile(r"\b(ORG_WIDE|SHARED|COMMON|TEAM_ALL)[A-Z_]*", re.I)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    root = sys.argv[1]
    found = []
    has_env_file = False
    deny_covers_env = False
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            if name == ".env" or name.startswith(".env."):
                has_env_file = True
            try:
                text = open(path, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            if rel.replace("\\", "/") == ".claude/settings.json":
                try:
                    cfg = json.loads(text)
                    deny = (cfg.get("permissions") or {}).get("deny") or []
                    deny_covers_env = any(".env" in d and d.startswith("Read") for d in deny)
                except ValueError:
                    pass
            lines = text.splitlines()
            if name.endswith(".sh") and ("token" in name.lower() or "key" in name.lower()):
                body = [l for l in lines if l.strip() and not l.startswith("#")]
                if len(body) == 1 and body[0].startswith("echo"):
                    found.append((2, rel, 1, "helper script only echoes a fixed value: " + body[0][:40]))
            for n, line in enumerate(lines, 1):
                if name in (".env",) or name.endswith(".env"):
                    continue
                if KEY_VALUE.search(line) and not name.endswith(".sh"):
                    found.append((1, rel, n, "key or token value written into a file"))
                if SET_VAR.search(line):
                    found.append((5, rel, n, "credential variable set in a file: " + SET_VAR.search(line).group(1)))
                m = SHARED.search(line)
                if m and name.endswith((".yml", ".yaml", ".csv")):
                    found.append((4, rel, n, "shared-sounding secret name: " + m.group(0)))
            if name.endswith(".csv") and "expires" in (lines[0] if lines else ""):
                header = lines[0].split(",")
                for n, line in enumerate(lines[1:], 2):
                    cells = line.split(",")
                    if len(cells) == len(header) and cells[header.index("expires")].strip().lower() in ("none", "never", ""):
                        found.append((4, rel, n, "inventory row with no expiry: " + cells[0]))
    if has_env_file and not deny_covers_env:
        found.append((3, ".env", 0, "an .env file exists and no Read deny rule covers it"))
    found.sort()
    for smell, rel, n, why in found:
        print("smell %d  %s%s  %s" % (smell, rel, (":%d" % n) if n else "", why))
    print("\n%d finding(s) across %d smell type(s)." % (len(found), len({f[0] for f in found})))
    return 0


if __name__ == "__main__":
    sys.exit(main())
