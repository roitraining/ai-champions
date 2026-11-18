# Lab 1: Rule to Control

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 30 minutes

> Part of **[AI Champions Training: Labs](README.md)**.

## What you will do

A team has written down three rules for Claude Code. Nothing enforces them yet. You will turn each rule into a control, prove it, and record where the team stands in a one-page charter.

| Rule | Control you will build |
|---|---|
| 1. No pushes, no forced deletes | A **hook**: a script Claude Code runs before every shell command. It can block the command |
| 2. Secrets stay unread | **Deny rules** in the project settings |
| 3. Blocked means logged | The same hook writes a log line each time it blocks something |

You finish by running a scorer.

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md): `claude --version` prints a version and `claude auth status` shows you are signed in
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Copy the project and start a repository

The sample project is called `ledgerlite`. You work on a copy, so the original stays unchanged.

Open a terminal (the **Terminal Emulator** icon on the desktop) and run:

```bash
mkdir -p ~/work && cp -r $FILES/lab1-rule-to-control/ledgerlite ~/work/ledgerlite && cd ~/work/ledgerlite && git init
```

**Expected output:**

```
Initialized empty Git repository in /home/<you>/work/ledgerlite/.git/
```

Your username replaces `<you>`. Above that line you will see about a dozen lines starting with `hint:` about the default branch name. Ignore them.

Stay in `~/work/ledgerlite` for the rest of the lab. Check where you are at any time with `pwd`.

List what you copied. The `-a` flag shows hidden files. The files you need are hidden:

```bash
ls -a
```

**Expected output:** these entries, in this or a different order:

```
.  ..  .claude  .env  .git  CLAUDE.md  build  config  src  tests
```

> **Command not found, or `No such file or directory`?** `$FILES` is empty. Fix it with the tip in Prerequisites and run the `cp` command again.

---

## Step 2: Read the starter files

Three files hold the team's work so far. Print each with `cat`:

```bash
cat $FILES/lab1-rule-to-control/rules.md
cat .claude/settings.json
cat .claude/hooks/guard.py
```

What each file is:

- **`rules.md`** is the three rules from the table at the top.
- **`.claude/settings.json`** is the project's Claude Code settings. It names a hook (a script to run) and a deny rule (a file Claude may not read).
- **`.claude/hooks/guard.py`** is the starter hook. Before Claude Code runs a shell command it starts this script and passes the command as JSON on standard input. The script's **exit code** is its answer:

| Exit code | What Claude Code does |
|---|---|
| `0` | Lets the command run |
| `2` | **Blocks** the command and shows Claude whatever the script printed to standard error |
| anything else, such as `1` | Shows an error but **lets the command run anyway** |

You need this table for the next steps.

---

## Step 3: Test the starter hook by hand

Before you change anything, test the starter hook. Define a helper so you do not have to type the JSON each time. Paste this once:

```bash
try() { echo "{\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"$1\"}}" | python3 .claude/hooks/guard.py; echo "exit=$?"; }
```

`try` sends one command to the hook, as Claude Code would, and prints the exit code. It does not run the command. Try five commands:

```bash
try 'git push origin main'
try 'cd src && git push'
try 'rm -rf build'
try 'rm -fr build'
try 'git status'
```

**Expected output:**

```
Blocked by team rule 1.
exit=1
exit=0
Blocked by team rule 1.
exit=1
exit=0
exit=0
```

Two things are wrong with this hook:

1. It **blocks** with exit code `1`, so Claude Code would show an error and run the command anyway. A block needs exit code `2`.
2. It **misses** two spellings of a forbidden command. `cd src && git push` and `rm -fr build` both print `exit=0`, so both would be allowed.

<details>
<summary>Why does the starter miss those two?</summary>

`re.match(r"git push", command)` only matches at the **start** of the command line, so `cd src && git push` slips through. `re.search(r"rm -rf", command)` looks for the exact text `rm -rf`, so `rm -fr`, `rm -r -f` and `rm --recursive --force` all slip through.

</details>

---

## Step 4: Fix the hook

**Your task:** change `guard.py` so that:

- `git push` is blocked **anywhere** in a command line (`cd src && git push` counts), with exit code `2`
- `rm` with both a recursive flag and a force flag is blocked in every spelling: `rm -rf build`, `rm -fr build`, `rm -r -f build`
- commands such as `git status` and `python3 -m pytest -q` still exit `0`
- every block adds one line containing the word `blocked` to a log file. Use the file named by the `CLAUDE_TOOL_LOG` environment variable, or `~/claude-tool-calls.log` if that variable is not set

Open the file in an editor. Use `nano`:

```bash
nano .claude/hooks/guard.py
```

Use the arrow keys to move and type to edit. **Ctrl+O**, then **Enter**, saves. **Ctrl+X** exits. To use a graphical editor, open the file in **Visual Studio Code** from the desktop.

Try it yourself first. If you get stuck, open the block below.

<details>
<summary>Show the fixed guard.py</summary>

Replace the whole file with:

```python
#!/usr/bin/env python3
"""PreToolUse hook for Bash. Rule 1: no pushes, no forced deletes. Rule 3: every block is logged.

Exit code 2 blocks the command and sends the stderr text back to Claude.
Reads only tool_name and tool_input from stdin.
"""
import datetime
import json
import os
import re
import sys

log = os.environ.get("CLAUDE_TOOL_LOG") or os.path.join(os.path.expanduser("~"), "claude-tool-calls.log")

PUSH = re.compile(r"\bgit\s+push\b")
# rm with both -r and -f in any order or any split form: -rf, -fr, -r -f, -Rf, --recursive --force
RM = re.compile(r"\brm\b(?=[^;&|]*?(?:\s-[a-zA-Z]*[rR]|\s--recursive))(?=[^;&|]*?(?:\s-[a-zA-Z]*f|\s--force))")


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    command = (data.get("tool_input") or {}).get("command", "")
    rule = "no-push" if PUSH.search(command) else ("no-force-delete" if RM.search(command) else None)
    if rule is None:
        return 0
    entry = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
             "event": "blocked", "rule": rule, "tool": data.get("tool_name"), "input": data.get("tool_input")}
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print("Blocked by team rule 1 (%s). Commit locally and ask a person to push, and delete files one at a time." % rule, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
```

**Why `\bgit\s+push\b`:** `search` finds the text anywhere in the line, `\s+` allows any spacing, and `\b` stops it matching a word like `gitpush`.

**Why two lookaheads for `rm`:** each one asks "is there a recursive flag somewhere in this command?" and "is there a force flag?". Together they match `-rf`, `-fr`, `-r -f` and the long forms, in any order. The `[^;&|]*?` part keeps the check inside one command, so `rm a; echo -f` is not treated as a force delete.

**Why `return 2`:** exit code 2 blocks the command. The message goes to standard error, which Claude Code passes back to Claude.

</details>

Prefer to have Claude write it? Skip the editor. Start Claude Code in this folder with `claude` (at the trust question press **Down**, then **Enter**), type the prompt below, and when Claude finishes type `/exit` and continue at Step 5:

<details>
<summary>Show a prompt you can give Claude</summary>

```
Fix .claude/hooks/guard.py so it exits 2 for git push anywhere in a command line and for rm with recursive and force flags in any spelling (rm -rf, rm -fr, rm -r -f), exits 0 for git status and python3 -m pytest -q, and appends one JSON line containing "blocked" to the file named by CLAUDE_TOOL_LOG or ~/claude-tool-calls.log. Test it with at least six commands.
```

Either way, run the checks in Step 5 yourself. Claude's own test results are not your evidence.

</details>

---

## Step 5: Test the fixed hook

Run eight commands through the hook. If you closed the terminal since Step 3, define `try` again (the one-line command in Step 3).

```bash
try 'git push origin main'
try 'cd src && git push'
try 'rm -rf build'
try 'rm -fr build'
try 'rm -r -f build'
try 'git status'
try 'python3 -m pytest -q'
try 'rm -f x.txt'
```

**Expected output:**

```
Blocked by team rule 1 (no-push). Commit locally and ask a person to push, and delete files one at a time.
exit=2
Blocked by team rule 1 (no-push). Commit locally and ask a person to push, and delete files one at a time.
exit=2
Blocked by team rule 1 (no-force-delete). Commit locally and ask a person to push, and delete files one at a time.
exit=2
Blocked by team rule 1 (no-force-delete). Commit locally and ask a person to push, and delete files one at a time.
exit=2
Blocked by team rule 1 (no-force-delete). Commit locally and ask a person to push, and delete files one at a time.
exit=2
exit=0
exit=0
exit=0
```

The message wording can differ. The `exit=` numbers must match: `2` for the first five, `0` for the last three. The last command checks that `rm -f` on a single file (no `-r`) is still allowed.

Check the log. The hook writes one line for each blocked command:

```bash
cat ~/claude-tool-calls.log
```

**Expected output** (five lines, one per blocked command; the times will differ):

```
{"ts": "2026-11-18T01:30:59Z", "event": "blocked", "rule": "no-push", "tool": "Bash", "input": {"command": "git push origin main"}}
{"ts": "2026-11-18T01:30:59Z", "event": "blocked", "rule": "no-push", "tool": "Bash", "input": {"command": "cd src && git push"}}
{"ts": "2026-11-18T01:30:59Z", "event": "blocked", "rule": "no-force-delete", "tool": "Bash", "input": {"command": "rm -rf build"}}
{"ts": "2026-11-18T01:30:59Z", "event": "blocked", "rule": "no-force-delete", "tool": "Bash", "input": {"command": "rm -fr build"}}
{"ts": "2026-11-18T01:30:59Z", "event": "blocked", "rule": "no-force-delete", "tool": "Bash", "input": {"command": "rm -r -f build"}}
```

> **A pattern still gives the wrong exit code?** Run that command with `try` and read the exit code. If `rm -fr build` prints `exit=0`, the `rm` pattern is not matching it. If every command prints `exit=0`, check that the file saved: `cat .claude/hooks/guard.py | head -5`.
>
> **`python3: can't open file`?** You are not in the project folder. Run `cd ~/work/ledgerlite` and try again.
>
> **The log has more lines than you expected, or `No such file or directory`?** The log is appended to, so earlier runs count. If the file does not exist, nothing was blocked yet. For a clean log, run `rm -f ~/claude-tool-calls.log` and repeat the eight commands.

---

## Step 6: Wire the hook and protect the secrets

The hook works when you call it by hand, but Claude Code does not run it yet. The settings file must name **which tool** the hook guards and **where the script is**. It must also deny Claude the right to read the secrets files.

**Your task:** edit `.claude/settings.json` so that:

- the hook runs before the **`Bash`** tool (the tool Claude uses to run shell commands)
- the hook command finds the script from the **project folder**, with the `${CLAUDE_PROJECT_DIR}` variable, and not from the current folder
- `permissions.deny` has `Read` rules that cover both `.env` and `config/secrets.env`

```bash
nano .claude/settings.json
```

Check the starter file from Step 2. Which tool does `matcher` name? Does the hook command path start with the project folder? Does the deny rule spell the file name correctly?

<details>
<summary>Show the fixed settings.json</summary>

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./config/secrets.env)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/guard.py\"" }
        ]
      }
    ]
  }
}
```

**What was wrong in the starter:**

- `"matcher": "Edit"` guarded file edits, not shell commands. A hook only fires for the tool its matcher names, so `git push` never reached it. The matcher has to be `Bash`.
- The command `python3 .claude/hooks/guard.py` is a **relative** path. It works only when Claude Code starts in the project folder. `${CLAUDE_PROJECT_DIR}` always points at the project, wherever Claude is. `$CLAUDE_PROJECT_DIR` without the braces works too.
- `Read(./env)` has a typo. The file is `.env`, with a dot. A deny rule for a file name that does not exist protects nothing, and there was no rule at all for `config/secrets.env`.

</details>

Check that your edit left the file valid JSON. A missing comma or quote breaks it:

```bash
python3 -m json.tool .claude/settings.json > /dev/null && echo "valid JSON"
```

**Expected output:**

```
valid JSON
```

> **`Expecting ',' delimiter` or another error from `json.tool`?** It prints the line and column. Common causes: a missing comma between two rules, a trailing comma after the last rule, or a missing closing brace.

> **Two facts about the settings file.**
>
> 1. **A deny rule on `Read` stops Claude's file-reading tool. It does not stop a shell command.** `cat .env` is a Bash command, and this rule does not cover it. Write that down: it goes in the charter in Step 9.
> 2. **Claude Code reads the project settings from the folder it starts in, not from the git root.** Start it from `~/work/ledgerlite`. If you started it in `ledgerlite/src`, the hook and the deny rules would not load, and a forced delete could run.

---

## Step 7: Check the wiring before you use it

Run the scorer. It checks your settings file and your hook. The charter is not filled in yet, so use the blank one:

```bash
python3 $FILES/lab1-rule-to-control/check_lab1.py ~/work/ledgerlite $FILES/lab1-rule-to-control/charter.md
```

**Expected output** (the last lines; the charter is still the blank one, so it does not pass yet):

```
[PASS] 10/10 A PreToolUse hook is wired to Bash and its command uses ${CLAUDE_PROJECT_DIR}
[PASS]  8/8  Hook exits 2 for: git push origin main
[PASS]  6/6  Hook exits 2 for: rm -rf build
[PASS]  3/3  Hook exits 2 for: rm -fr build
[PASS]  4/4  Hook exits 2 for: cd src && git push
[PASS]  5/5  Hook exits 0 for: git status
[PASS]  4/4  Hook exits 0 for: python3 -m pytest -q
[PASS] 10/10 A blocked command writes a line containing 'blocked' to the file named by CLAUDE_TOOL_LOG
[PASS]  8/8  A Read deny rule covers .env
[PASS]  7/7  A Read deny rule covers config/secrets.env
[PART]  6/20 Charter: 2 of 10 areas decided (need at least 6 for full marks)  -> each decided area is worth about 3 points until you reach 6
[FAIL]  0/15 Every Enforced row names a control that exists (CLAUDE.md is a request, not a control)
        row 6 (Permissions and sandbox): control 'CLAUDE.md' is not a file or setting that exists
        row 9 (Logging): control 'the team will keep notes' is not a file or setting that exists

TOTAL: 71 / 100
CHECKPOINT: NOT YET (blocked-command test exits 2: yes; charter decided 2 of 10, need 6)
```

Every hook and deny-rule line should say `[PASS]`. Only the two **Charter** lines are open. You finish them in Step 9. If a hook or deny line fails, it says what it could not accept. Fix it before you continue.

---

## Step 8: Prove it inside Claude Code

Testing a script by hand is not the same as Claude Code obeying it. Start a session in the project folder and ask Claude to break the rule.

```bash
cd ~/work/ledgerlite
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to move to **Yes, I trust this folder**, then press **Enter**.

The bottom of the screen shows `auto mode on`. Leave it.

**Try the push.** Type this prompt, exactly as written, and press Enter:

```
This is a throwaway practice repo with no remote. Run git push origin main and show me the exact output.
```

**Expected result:** Claude tries the command and your hook stops it before `git` starts. Claude shows you the hook's message, which looks like this:

```
PreToolUse:Bash hook error: [python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/guard.py"]: Blocked by team rule 1 (no-push). Commit locally and ask a person to push, and delete files one at a time.
```

Claude's surrounding words differ. The `Blocked by team rule 1 (no-push)` text comes from `guard.py`. If you see it, the hook ran.

**Try the forced delete.** Type:

```
Run rm -rf build and show me the exact output.
```

**Expected result:** the hook blocks it with `Blocked by team rule 1 (no-force-delete)`. Claude may then offer to delete the files one at a time instead, which is what your hook's message suggests. Do not accept. You are testing the block, not clearing the folder. Confirm the folder is still there:

```
Run ls build and show me the output
```

**Expected result:**

```
old.txt
```

**Test the secrets rule.** Type:

```
Read the file config/secrets.env and show me what is in it
```

**Expected result:** Claude cannot show you the contents. The file-reading tool is refused with this message, which comes from the `Read` rule you added:

```
File is in a directory that is denied by your permission settings.
```

> **Claude refused to push or delete before running anything?** The project's `CLAUDE.md` asks Claude not to push, and Claude sometimes obeys it before your hook gets a chance. That is a result, but it does not prove your hook. Use the wording above (the throwaway repo, "show me the exact output"). If Claude still declines, say: `I know. I am testing the hook. Please run it anyway.`
>
> **Claude refused to read the secrets file, and you are not sure which rule did it?** `ledgerlite/CLAUDE.md` also asks Claude not to read it. That is a request, not a control. The message `denied by your permission settings` is the control speaking. The scorer checks your rule, not Claude's behavior.
>
> **The push ran, or the folder was deleted?** The hook is not wired in. Exit Claude Code, run the Step 7 scorer, and read the first line. A matcher that is not `Bash`, or a settings file that did not save, are common causes. Exit and restart `claude` after any settings change, because settings are read at startup.

Leave Claude Code by typing `/exit` and pressing Enter. Then check the log:

```bash
cat ~/claude-tool-calls.log
```

**Expected output:** the five lines from Step 5, plus **two new lines** for the commands Claude tried: one with `"rule": "no-push"` and one with `"rule": "no-force-delete"`. Seven lines in all if you started from a clean log (check with `wc -l ~/claude-tool-calls.log`). That log is your evidence for rule 3: the team can prove the rule held.

---

## Step 9: Fill in the charter

The charter records what each control covers and what it does not.

Make your own copy to edit:

```bash
cp $FILES/lab1-rule-to-control/charter.md ~/work/charter.md
nano ~/work/charter.md
```

The charter has ten practice areas in a table. Each row has a **Status**:

- **Enforced:** a control holds the rule, so a person cannot break it by forgetting. The **Control or evidence** column must name that control as a file or setting, such as `.claude/hooks/guard.py` or `.claude/settings.json permissions.deny`.
- **Reviewed:** a person checks it, such as a code review, but nothing blocks a mistake.
- **Undecided:** the team has not decided yet. Leave it that way. It is better than inventing a rule.

**Your task:** decide **at least six** of the ten areas as Enforced or Reviewed. For each, write a one-sentence rule and name an owner. Every Enforced row must name a control that exists. Use any names for the team and owners.

Two rows are already filled in, and **both are wrong**. Row 6 says Enforced but points to `CLAUDE.md`, which is a request and not a control. Row 9 says Enforced but points to "the team will keep notes". Fix both. Point to the controls you built.

<details>
<summary>Show example rows</summary>

Use the same table shape. Your wording will differ.

| # | Practice area | Our rule (one sentence) | Status | Control or evidence | Owner |
|---|---|---|---|---|---|
| 1 | Purpose and owner | Dana owns Claude Code use on ledgerlite | Reviewed | owner named in README, checked each quarter | Dana |
| 2 | Data | Secrets files are never read | Enforced | `.claude/settings.json` permissions.deny | Dana |
| 3 | Repositories | Claude Code works only in ledgerlite | Reviewed | pull request review | Ravi |
| 4 | Tools and servers |  | Undecided |  |  |
| 5 | Model and effort |  | Undecided |  |  |
| 6 | Permissions and sandbox | Claude Code never pushes and never force-deletes | Enforced | `.claude/hooks/guard.py` (exit 2) | Dana |
| 7 | Credentials |  | Undecided |  |  |
| 8 | Review and escalation | A second person reviews every pull request | Reviewed | pull request settings | Ravi |
| 9 | Logging | Every blocked action is logged | Enforced | `.claude/hooks/guard.py` writes the log | Dana |
| 10 | Exit criteria |  | Undecided |  |  |

**Caveat for row 2:** the deny rule stops Claude's file tool, but a shell command such as `cat .env` is not covered by it. Say so in the rule.

</details>

> **How do I know what counts as a control?** Ask: "If the person forgot, would something still stop it?" A hook, a deny rule or a sandbox setting does. A sentence in `CLAUDE.md` does not, because the model may ignore it. If only a person remembering holds the rule, the status is Reviewed.

---

## Step 10: Score the lab

Run the scorer on your project and your charter:

```bash
python3 $FILES/lab1-rule-to-control/check_lab1.py ~/work/ledgerlite ~/work/charter.md
```

**Expected output** when everything is finished:

```
LAB 1 SCORE
[PASS] 10/10 A PreToolUse hook is wired to Bash and its command uses ${CLAUDE_PROJECT_DIR}
[PASS]  8/8  Hook exits 2 for: git push origin main
[PASS]  6/6  Hook exits 2 for: rm -rf build
[PASS]  3/3  Hook exits 2 for: rm -fr build
[PASS]  4/4  Hook exits 2 for: cd src && git push
[PASS]  5/5  Hook exits 0 for: git status
[PASS]  4/4  Hook exits 0 for: python3 -m pytest -q
[PASS] 10/10 A blocked command writes a line containing 'blocked' to the file named by CLAUDE_TOOL_LOG
[PASS]  8/8  A Read deny rule covers .env
[PASS]  7/7  A Read deny rule covers config/secrets.env
[PASS] 20/20 Charter: 6 of 10 areas decided (need at least 6 for full marks)
[PASS] 15/15 Every Enforced row names a control that exists (CLAUDE.md is a request, not a control)

TOTAL: 100 / 100
CHECKPOINT: PASS (blocked-command test exits 2: yes; charter decided 6 of 10, need 6)
```

If a line says `[FAIL]`, read it. It names what it could not accept. Fix the lowest-scoring line first, then run the scorer again.

**Checkpoint:** the scorer prints `CHECKPOINT: PASS`. That means a blocked-command test exits 2 **and** the charter has at least six of the ten areas decided.

> **The charter score stays low?** A row marked Enforced points at `CLAUDE.md` or at a sentence, and not at a file or a setting. Change the status to Reviewed, or name the control.
>
> **`FileNotFoundError` for the charter?** You passed `charter.md` without its folder. Use `~/work/charter.md`, the copy you made in Step 9.
>
> **A hook line fails though your tests in Step 5 passed?** The scorer runs your hook the way Claude Code does. If you test with `python3` and the hook command in settings names `python`, use the name that works on your machine in both places.

---

## What you built

In 30 minutes, you:

- Turned **rule 1** into a hook that blocks `git push` and recursive force deletes in every spelling, using exit code `2`
- Turned **rule 3** into a log line written by that same hook
- Turned **rule 2** into `Read` deny rules for both secrets files, and learned they stop Claude's file tool and not shell commands
- Proved the controls in a live Claude Code session
- Wrote a charter that says **Enforced** only where a control holds

Summary: a sentence in `CLAUDE.md` is a request. A hook, a deny rule and a log are controls.

## How the score is made

| Item | Points |
|---|---|
| Hook wired to `Bash` with a project-directory path | 10 |
| Exit 2 for `git push origin main` | 8 |
| Exit 2 for `rm -rf build` | 6 |
| Exit 2 for `rm -fr build` | 3 |
| Exit 2 for `cd src && git push` | 4 |
| Exit 0 for `git status` and for the test command | 9 |
| A block writes a `blocked` line to the log | 10 |
| Read deny rule for `.env` | 8 |
| Read deny rule for `config/secrets.env` | 7 |
| Charter: 6 or more of 10 decided (partial credit below 6, about 3 points an area) | 20 |
| Every Enforced row names a control that exists | 15 |

## Cleanup

Nothing needs undoing. To remove the log:

```bash
rm -f ~/claude-tool-calls.log
```
