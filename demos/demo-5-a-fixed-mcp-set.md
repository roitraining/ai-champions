# Demo 5: A Fixed MCP Set

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Demos](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** Fix the set of MCP servers a team may use, and show that each user authenticates as themselves with no secret in the shared file. Time: about 15 minutes.

**Files:** `$FILES/demo5-mcp`: `servers/notes_server.py`, `servers/shadow_server.py`, `servers/mcp_min.py`, `servers/test_servers.py`, `setup_project.sh`, `install_managed_mcp.sh`, `remove_managed_mcp.sh`, `install_managed_mcp.ps1`, `remove_managed_mcp.ps1`. Review aid: `$FILES/templates/mcp-server-review.md`.

**Context:** Two small local servers run on your machine, so no account or network is needed. `notes` is the approved server. It reads a per-user environment variable, `NOTES_TOKEN`, and maps it to a user. `shadow-sync` stands in for a server nobody reviewed. A `managed-mcp.json` file gives exclusive control: only the servers it defines load, and `claude mcp add` fails. The file is readable by every user on the machine, so it holds no secret. It refers to `${NOTES_TOKEN}` and each user supplies their own value.

**Steps:**

1. Check that both servers work without Claude Code: `python3 servers/test_servers.py`. Four lines read `ok`.
2. Write the project file: `bash setup_project.sh`. It creates `project/.mcp.json` declaring both servers.
3. `export NOTES_TOKEN=FAKE-TOKEN-DO-NOT-USE-alice`, then `cd project && claude`. Approve the project servers if asked. Run `/mcp`. Both servers appear. Ask Claude to call the `whoami` tool of `notes`, then the `sync_notes` tool of `shadow-sync`. Read the second answer: a local server runs with the user's rights. Exit.
4. Install the managed file: `sudo bash install_managed_mcp.sh`. Read it: `cat /etc/claude-code/managed-mcp.json`. Find `${NOTES_TOKEN}`: there is no secret in it.
5. Restart `claude` in `project`. Run `claude mcp list` in another shell. Only `notes` is listed.
6. Try to add a server: `claude mcp add --transport http test https://example.com/mcp`. It fails with a message that an enterprise MCP configuration is active and has exclusive control.
7. In a second terminal, `export NOTES_TOKEN=FAKE-TOKEN-DO-NOT-USE-bo`, start `claude` in `project`, and ask for `whoami` again. It answers `bo`. Same file, different identity.
8. Review a server before adding it: fill in two rows of `templates/mcp-server-review.md` for `shadow-sync` (what can it reach, what identity does it use).
9. Clean up: `sudo bash remove_managed_mcp.sh`.

**Expected result:** Before the managed file, both servers load. After it, only `notes` loads, adding a server fails, and two users get two identities from one shared file.

**Why this matters:** A server is code that runs with the user's rights, outside the sandbox, and it authenticates as someone. A fixed set removes the unreviewed ones. Per-user credentials mean the log shows who did what, and a leaver's access ends with their own login.
