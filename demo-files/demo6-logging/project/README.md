# logging-hook demo project (fictional)

A scratch project for Demo 6. Run `git init` and make one commit here first.

Rule: "Claude Code never pushes."

- Decide: written in the team charter.
- Enforce: `.claude/hooks/block-push.py` exits 2 on `git push`.
- Prove: `summarize_log.sh` reads the log and shows each blocked attempt.

The log goes to `~/claude-tool-calls.log`. Set `CLAUDE_TOOL_LOG` to use another file.
