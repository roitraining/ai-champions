---
description: The lint hook fires when a bad RELEASE_NOTES.md is written, and Claude sees its message.
max_turns: 8
timeout_seconds: 120
allowed_tools: [Read, Glob, Grep, Write]
tags: [hook]
---

Create a file named RELEASE_NOTES.md whose entire content is the single line: TODO write this later

Then tell me exactly what the checker said about it.
