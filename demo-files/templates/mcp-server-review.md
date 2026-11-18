# MCP Server Review Checklist

> **Generic template.** Use it before a server is added to a project or to a team's fixed set. Your team replaces and extends it.

**Server name:** ______________  **Source (repository or vendor):** ______________  **Reviewer:** ______________  **Date:** __________

| # | Question | Answer | Pass? |
|---|---|---|---|
| 1 | Who wrote it, and can you read its source? |  |  |
| 2 | How is it started (a local command, or a remote URL)? A local command runs with your user's rights. |  |  |
| 3 | What can it reach: files, network, a database, a ticket system? |  |  |
| 4 | As which identity does it authenticate (the user, a service account, a shared key)? |  |  |
| 5 | Where does the credential come from (each user's environment variable, a sign-in through `/mcp`, a per-user header)? It must not be written into a shared file. |  |  |
| 6 | What tools does it expose, and which of them change something? |  |  |
| 7 | Can its output carry text written by an outsider (tickets, web pages, emails)? If yes, treat that text as untrusted. |  |  |
| 8 | Is it pinned to a version, or does it fetch the newest code on every start? |  |  |
| 9 | Who owns it after approval, and who removes it? |  |  |

Remember: MCP servers run outside the sandbox. A sandbox rule does not limit what a server can do.

**Decision:** [ ] Add  [ ] Add with limits  [ ] Reject      Reason:
