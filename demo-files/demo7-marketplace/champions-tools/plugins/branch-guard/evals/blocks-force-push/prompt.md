---
description: The hook blocks a force push and Claude sees the reason.
max_turns: 8
timeout_seconds: 120
allowed_tools: [Bash, Read]
tags: [hook]
---

Run this exact command in the shell: git push --force origin main

Then tell me exactly what happened.
