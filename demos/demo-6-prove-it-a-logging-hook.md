# Demo 6: Prove It: A Logging Hook

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 12 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

A rule is only useful if you can prove it held. The rule here is "Claude Code never pushes". You will see the three parts of that proof:

| Part | What it is here |
|---|---|
| **Decide** | The rule, written down |
| **Enforce** | A hook that blocks `git push` (exit code 2) |
| **Prove** | A log line for every blocked attempt |

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md): `claude --version` prints a version and `claude auth status` shows you are signed in
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Copy the project and start a repository

You work on a copy, so the course files stay unchanged. Open a terminal (the **Terminal Emulator** icon on the desktop) and run:

```bash
mkdir -p ~/work && cp -r $FILES/demo6-logging ~/work/demo6-logging && cd ~/work/demo6-logging/project && git init -q && git commit -q --allow-empty -m init && chmod +x .claude/hooks/*
```

**Expected output:** none. A quiet shell prompt means every command worked. If you see lines starting with `hint:`, ignore them.

The `chmod +x` makes the hook scripts executable. Without it the logging hook fails silently.

> **`Author identity unknown` or `Please tell me who you are`?** Git needs a name for the commit. Run `git config user.email you@example.com && git config user.name "Your Name"`, then run `git commit -q --allow-empty -m init && chmod +x .claude/hooks/*`.

The logging hook needs `jq`, a tool that reads JSON. Check that it is installed:

```bash
jq --version
```

**Expected output:** a version such as `jq-1.7`.

> **`jq: command not found`?** Use the Python logger instead. Run these two commands, then continue:
>
> ```bash
> cp ../settings.windows-or-no-jq.json .claude/settings.json
> sed -i 's/"python /"python3 /g' .claude/settings.json
> ```
>
> The first command swaps in a settings file that calls a Python logger. The second changes `python` to `python3`, the name on this machine.

---

## Step 2: Read the three pieces

Print the project's README, the hook that blocks, and the settings that wire it:

```bash
cat README.md
cat .claude/hooks/block-push.py
cat .claude/settings.json
```

What you are looking at:

- **`README.md`** states the rule: "Claude Code never pushes."
- **`block-push.py`** is a `PreToolUse` hook. Claude Code starts it before each shell command and passes the command as JSON on standard input. If the command contains `git push`, the script writes a `blocked` line to the log and exits with code `2`. Exit code `2` blocks the command and sends the script's standard error text back to Claude.
- **`settings.json`** attaches two hooks. The `PreToolUse` hook on `Bash` is the blocker. The `PostToolUse` hook on `*` logs every tool call after it runs, using only `tool_name` and `tool_input`.

The blocker writes its own log line because a blocked command never runs, so the `PostToolUse` hook never sees it.

---

## Step 3: Test the blocker by hand

Send the hook two commands, as Claude Code would, and read the exit code. Nothing is run:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | python3 .claude/hooks/block-push.py; echo "exit=$?"
echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' | python3 .claude/hooks/block-push.py; echo "exit=$?"
```

**Expected output:**

```
exit=0
Blocked by the no-push rule. Claude Code does not push in this project. Commit locally and ask the user to push.
exit=2
```

`ls` passes with exit code `0`. The push is blocked with exit code `2`.

The blocked push wrote a line to the log. Look at it, then delete the log so your live test in Step 4 starts clean:

```bash
cat ~/claude-tool-calls.log
rm -f ~/claude-tool-calls.log
```

**Expected output:** one line (the time differs):

```
{"ts": "2026-11-18T01:50:12Z", "event": "blocked", "rule": "no-push", "tool": "Bash", "input": {"command": "git push origin main"}}
```

> **`cat` says `No such file or directory`?** The hook did not write the log. Check that `CLAUDE_TOOL_LOG` is not set to another file (`echo $CLAUDE_TOOL_LOG` should print nothing), and that you are in `~/work/demo6-logging/project`.

---

## Step 4: Watch the hook block a push in Claude Code

Start a session in the project folder:

```bash
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to select **Yes, I trust this folder**, then press **Enter**. The bottom of the screen shows `auto mode on`. Leave it.

Type this prompt, exactly as written, and press Enter:

```
List the files here, then run git push origin main.
```

**Expected result:** Claude lists the files, then reports that the push was blocked. It repeats the message from the hook: `Blocked by the no-push rule. Claude Code does not push in this project. Commit locally and ask the user to push.`

> **Claude declined to push before the hook ran?** The model sometimes refuses on its own. That does not prove your hook. Type: `This is a throwaway practice repo. Please run git push origin main anyway and show me the exact output.` Then the hook has to do the blocking.

Leave Claude Code by typing `/exit` and pressing Enter.

---

## Step 5: Read the log

First read the shape of a finished proof. The project ships a sample log from an earlier session. Summarize it with the Python summarizer, which needs no `jq`:

```bash
python3 ../summarize_log.py ../sample-log.jsonl
```

**Expected output:**

```
Calls by tool:
    1  Read
    1  Edit
    1  Bash

Blocked attempts:
  2026-10-20T14:02:36Z  no-push  git push origin main

Blocked pushes: 1
```

Now summarize your own log from Step 4:

```bash
python3 ../summarize_log.py
```

**Expected result:** the same three parts. Under **Calls by tool** you see the tools Claude used, such as `Glob` or `Bash`, with counts. Your counts differ from the sample. Under **Blocked attempts** you see one line with `no-push` and the command `git push origin main`. The last line reads `Blocked pushes: 1`.

> **`No log at ... yet.`?** Nothing was logged. Check that the Step 4 session started in `~/work/demo6-logging/project` and that the hook scripts are executable (`ls -l .claude/hooks`).
>
> **`Blocked attempts` is empty, but Claude said the push was blocked?** Claude may have declined before the hook ran. Repeat Step 4 with the throwaway-repo wording.
>
> **The summary shows extra blocked lines?** The log is appended to. Lines from earlier runs count. Delete it with `rm -f ~/claude-tool-calls.log` and repeat Step 4.

If `jq` is installed, `bash ../summarize_log.sh` gives the same summary.

---

## Step 6: Name the proof

Write your answers in a notes file:

```bash
nano ~/work/demo6-notes.md
```

Type these three lines, and finish each one with the file or line that matches:

```
Decide: <the file that states the rule>
Enforce: <the file that blocks the push>
Prove: <the log line you saw>
```

Save with **Ctrl+O**, then **Enter**. Exit with **Ctrl+X**.

<details>
<summary>Show the answers</summary>

```
Decide: README.md ("Claude Code never pushes.")
Enforce: .claude/hooks/block-push.py, wired in .claude/settings.json (exit code 2)
Prove: the "blocked" line with "rule": "no-push" in ~/claude-tool-calls.log
```

</details>

---

## Step 7: Name what the log cannot prove

Add one more line to the same file:

```bash
nano ~/work/demo6-notes.md
```

```
Gap: <one thing this log could not prove>
```

<details>
<summary>Show example answers</summary>

- A rule nobody wrote a hook for leaves no log line. Silence in the log does not mean the rule held.
- A command run outside Claude Code, such as in your own terminal, never reaches the hook.
- The log shows that a push was blocked. It does not show who wrote the rule or who approved it.

</details>

---

## What you learned

- A rule has three parts: someone decides it, a control enforces it, and a log proves it held.
- A hook that exits with code `2` blocks the command. A blocked command never runs, so the blocking hook must write its own log line.
- The log turns "we never push" into evidence an auditor can read. It also shows the moment the rule stopped a push.

## Cleanup

```bash
rm -f ~/claude-tool-calls.log
rm -rf ~/work/demo6-logging
```
