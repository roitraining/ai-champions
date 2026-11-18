# Demo 5: A Fixed MCP Set

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 15 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

Two MCP servers run on your machine, so no account or network is needed. `notes` is the approved server. `shadow-sync` stands in for a server nobody reviewed. You install a managed MCP file that allows only `notes`, and show that each user authenticates as themselves with no secret in the shared file.

An MCP server is a program Claude Code starts and calls for extra tools. A local server runs with your user's rights, outside the sandbox.

## Prerequisites

- [ ] `claude auth status` shows you are signed in (see [`SETUP.md`](../SETUP.md))
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`
- [ ] You can use `sudo`. Steps 4 and 9 write and remove files in `/etc/claude-code` and `/opt`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Check both servers without Claude Code

Open a terminal (the **Terminal Emulator** icon on the desktop). The test script starts each server and calls one tool, with no model involved:

```bash
cd $FILES/demo5-mcp
python3 servers/test_servers.py
```

**Expected output:**

```
[ok] notes as alice: Authenticated as: alice
[ok] notes as bo: Authenticated as: bo
[ok] notes with no token: Not authenticated. Set NOTES_TOKEN in your own shell before starting Claude Code.
[ok] shadow-sync: shadow-sync is running as user <you>. It could read anything that user can read, for example files under /home/<you>. It is not limited by the sandbox.
```

Your username replaces `<you>`. Four lines read `[ok]`. The `notes` server reads a variable called `NOTES_TOKEN` and maps it to a user. The `shadow-sync` line says what any local server can do: read what you can read.

---

## Step 2: Write the project file

The project declares both servers. Generate its `.mcp.json`:

```bash
bash setup_project.sh
cat project/.mcp.json
```

**Expected output:**

```
Wrote /home/<you>/champions/demo-files/demo5-mcp/project/.mcp.json
{
  "mcpServers": {
    "notes": { "command": "python3", "args": ["/home/<you>/champions/demo-files/demo5-mcp/servers/notes_server.py"] },
    "shadow-sync": { "command": "python3", "args": ["/home/<you>/champions/demo-files/demo5-mcp/servers/shadow_server.py"] }
  }
}
```

---

## Step 3: Run with both servers

This is the "before" state. Set your identity, then start Claude Code in the project:

```bash
export NOTES_TOKEN=FAKE-TOKEN-DO-NOT-USE-alice
cd project
claude
```

Set `NOTES_TOKEN` before you start `claude`. The server reads it at startup.

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to move to **Yes, I trust this folder**, then press **Enter**.

Next Claude Code lists the two project servers, `notes` and `shadow-sync`, with a tick next to each. This demo needs both loaded, so approve both: use the arrow keys to move to **Enable selected** and press **Enter**. The bottom of the screen shows `auto mode on`. Leave it.

Type `/mcp` and press Enter. **Expected result:** both servers are listed. Now type this prompt and press Enter:

```
Call the whoami tool of the notes server and show me its exact answer.
```

**Expected result:** Claude calls the tool and reports:

```
Authenticated as: alice
```

Type this prompt:

```
Call the sync_notes tool of the shadow-sync server and show me its exact answer.
```

**Expected result:** Claude reports:

```
shadow-sync is running as user <you>. It could read anything that user can read, for example files under /home/<you>. It is not limited by the sandbox.
```

Read that answer. A server nobody reviewed is running as you.

Leave Claude Code by typing `/exit` and pressing Enter.

> **Claude Code asks permission to call a server's tool?** Allow it. Server tools ask by default.
>
> **`Not authenticated. Set NOTES_TOKEN in your own shell before starting Claude Code.`?** `NOTES_TOKEN` was not set in the shell that started `claude`. Exit Claude Code, run the `export` line again, and restart `claude`.

---

## Step 4: Install the managed MCP file

This is the first `sudo` step. The script does two things:

- copies the server scripts to `/opt/champions-mcp`, where a user cannot edit them
- writes `/etc/claude-code/managed-mcp.json`, which defines only `notes`

If a managed MCP file is already there, the script saves a backup first. Go back to the demo folder and run:

```bash
cd ..
sudo bash install_managed_mcp.sh
```

`sudo` may ask for your password. Type it and press Enter. The password does not show as you type.

**Expected output:**

```
Installed /etc/claude-code/managed-mcp.json. The file holds no secret: NOTES_TOKEN is read from each user's own environment.
Restart Claude Code. Check: claude mcp list
```

Read the file:

```bash
cat /etc/claude-code/managed-mcp.json
```

**Expected output:**

```
{
  "mcpServers": {
    "notes": {
      "command": "python3",
      "args": ["/opt/champions-mcp/notes_server.py"],
      "env": { "NOTES_TOKEN": "${NOTES_TOKEN}" }
    }
  }
}
```

Find `${NOTES_TOKEN}`. It is a placeholder for each user's own environment variable, not a value. Every user on the machine can read this file, so it must hold no secret.

---

## Step 5: Check that only `notes` loads

Run this in the same terminal. `NOTES_TOKEN` is still set from Step 3:

```bash
cd project
claude mcp list
```

**Expected output:**

```
Checking MCP server health…

notes: python3 /opt/champions-mcp/notes_server.py - ✔ Connected
```

Only `notes` is listed, and it runs from `/opt/champions-mcp`. `shadow-sync` is gone, even though the project's `.mcp.json` still declares it. A managed MCP file gives exclusive control: only the servers it defines load. Servers you added yourself, or connected through your account, stop loading too.

---

## Step 6: Try to add a server

```bash
claude mcp add --transport http test https://example.com/mcp
```

**Expected output:**

```
Cannot add MCP server: enterprise MCP configuration is active and has exclusive control over MCP servers
```

The command fails. A user cannot add a server while the managed file is in place.

---

## Step 7: Two users, one file

Open a second terminal tab: choose **File**, then **Open Tab** in the terminal's menu bar, or press **Ctrl+Shift+T**. In the new tab, set your variables and start Claude Code as a second user:

```bash
export FILES=~/champions/demo-files
export NOTES_TOKEN=FAKE-TOKEN-DO-NOT-USE-bo
cd $FILES/demo5-mcp/project
claude
```

Type this prompt and press Enter:

```
Call the whoami tool of the notes server and show me its exact answer.
```

**Expected result:** Claude reports:

```
Authenticated as: bo
```

The first tab used the `alice` value and this tab uses the `bo` value. The managed file is the same. Each user brought their own identity in an environment variable.

Leave Claude Code by typing `/exit` and pressing Enter. You can close the second tab.

---

## Step 8: Review the unapproved server

Before a server is added to a team's fixed set, someone reviews it. A review checklist is in `templates/mcp-server-review.md`. Copy it and open the copy:

```bash
mkdir -p ~/work
cp $FILES/templates/mcp-server-review.md ~/work/shadow-sync-review.md
nano ~/work/shadow-sync-review.md
```

**Your task:** fill in the **Answer** column for two rows, for `shadow-sync`:

- row 3: what can it reach?
- row 4: as which identity does it authenticate?

Press **Ctrl+O**, then **Enter**, to save. Press **Ctrl+X** to exit. To find the answers, re-read the `shadow-sync` output from Step 3.

<details>
<summary>Show example answers</summary>

| # | Question | Answer |
|---|---|---|
| 3 | What can it reach: files, network, a database, a ticket system? | Anything your user can read, for example files under your home folder. It is not limited by the sandbox. |
| 4 | As which identity does it authenticate? | It does not authenticate anyone. It runs as the user who started Claude Code, with that user's rights. |

Row 2 would also read: started by a local command, so it runs with your user's rights. Your wording can differ. What matters is that you named the reach and the identity.

</details>

---

## Step 9: Remove the managed file

Close any Claude Code sessions. This is the second `sudo` step. The script deletes `/etc/claude-code/managed-mcp.json`, puts back the backup if it saved one in Step 4, and deletes `/opt/champions-mcp`. Run it from the demo folder:

```bash
cd $FILES/demo5-mcp
sudo bash remove_managed_mcp.sh
```

**Expected output:**

```
Removed /etc/claude-code/managed-mcp.json.
```

Check that nothing is left:

```bash
ls /etc/claude-code
ls /opt/champions-mcp
unset NOTES_TOKEN
```

**Expected output:** the first command prints nothing. The second prints:

```
ls: cannot access '/opt/champions-mcp': No such file or directory
```

> **Skipped this step, or the script failed?** The managed file stays in force for every user on the machine until it is removed. Claude Code on this machine loads only `notes`, and `claude mcp add` keeps failing. Run the `sudo bash remove_managed_mcp.sh` command again before you leave.

---

## What you saw

- Before the managed file, both servers loaded, and the unreviewed one ran as you.
- After it, only `notes` loaded, adding a server failed, and two users got two identities from one shared file.

A server is code that runs with the user's rights, outside the sandbox, and it authenticates as someone. A fixed set removes the unreviewed ones. Per-user credentials mean the log shows who did what, and a leaver's access ends with their own login.

## Cleanup

Step 9 is the cleanup. To remove the project file and your review notes:

```bash
rm -f $FILES/demo5-mcp/project/.mcp.json ~/work/shadow-sync-review.md
```
