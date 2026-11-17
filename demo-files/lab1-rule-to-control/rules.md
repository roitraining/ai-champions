# Team rules to turn into controls (fictional team: Ledgerlite)

These three rules are written down and nothing enforces them yet.

1. **No pushes, no forced deletes.** Claude Code never runs `git push`, and never runs a recursive force delete (`rm -rf`).
2. **Secrets stay unread.** Claude Code never reads `.env` or `config/secrets.env`.
3. **Blocked means logged.** When a rule blocks an action, the attempt is written to a log, so the team can prove the rule held.

Your job: make each rule a control that works, then record where the team stands in the charter.
