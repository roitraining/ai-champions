# Plugin Security Review Checklist

> **Generic template.** Run it before a plugin is trusted or distributed. Your team replaces and extends it.

**Plugin:** ______________  **Version:** ______  **Source:** ______________  **Reviewer:** ______________  **Date:** __________

1. Where did the marketplace come from? Run `claude plugin marketplace list` and check the source.
2. List what the plugin contains: `claude --plugin-dir <dir> plugin details <name>`. Note commands, skills, agents, hooks and servers.
3. Read `hooks/hooks.json` and every script it names. Hooks run with your user's rights and outside the sandbox.
4. Read `.mcp.json` if present. Servers run outside the sandbox too.
5. Read any `bin/` directory.
6. Read every command, skill and agent file. They enter the context window as instructions, so look for text that tells Claude to do something the user did not ask for.
7. Check that hook paths use `${CLAUDE_PLUGIN_ROOT}` and not a fixed path on one machine.
8. Check that a checking agent has only read tools.
9. Note the always-on cost from `plugin details`. Descriptions are in the context window every turn.
10. Is the version pinned? If the marketplace updates the plugin, the reviewed files can change. Decide who re-reviews.

**Decision:** [ ] Trust  [ ] Trust with limits  [ ] Do not trust      Reason:
