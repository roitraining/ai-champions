# Lab 1: Rule to Control

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Labs](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** Turn three written team rules into controls that work, prove each with a test, and record the team's real position in a charter. Time: 30 minutes.

**Files:** `$FILES/lab1-rule-to-control`: `rules.md`, `ledgerlite/` (the sample project), `charter.md`, `check_lab1.py`. Templates: `$FILES/templates/team-practices-charter.md`.

**Context:** `rules.md` holds three rules that nothing enforces: no pushes and no forced deletes, secrets stay unread, and blocked means logged. The sample project has a starter hook, a settings file and a `CLAUDE.md` that only asks nicely. A hook script reads the tool call as JSON on standard input. Exit code 2 blocks a PreToolUse call and sends standard error back to Claude. Exit code 1 does not block. A `Read` deny rule blocks Claude's file tools. The charter has ten practice areas and a status column: Enforced (a control holds it), Reviewed (a person checks it) and Undecided. The charter and the checklist are generic templates, and your team replaces them with its own.

**Steps:**

1. **Set up (about 3 minutes).** Goal: the project on your machine and the starter behavior seen.
   - Copy `ledgerlite` to `~/work/ledgerlite`, run `git init`, and read `.claude/settings.json` and `.claude/hooks/guard.py`.
   - Pipe a sample call into the hook and read the exit code: `echo '{"tool_name":"Bash","tool_input":{"command":"git push origin main"}}' | python3 .claude/hooks/guard.py; echo $?`.

2. **Fix the hook (about 10 minutes).** Goal: `guard.py` blocks rule 1 in every form a person would type, and logs each block for rule 3.
   - Acceptance criteria:
     - It exits 2 for `git push` in any position of a command line, and for a recursive force delete however the flags are written.
     - It exits 0 for harmless commands such as `git status` and `python3 -m pytest -q`.
     - When it blocks, it appends one JSON line containing `"blocked"` to the file named by the `CLAUDE_TOOL_LOG` environment variable, or to `~/claude-tool-calls.log` if it is not set.
     - It reads only `tool_name` and `tool_input` from the input.
   - Hints: Try the hook by hand with at least six different commands before you touch the settings. Ask what a pattern anchored to the start of the line misses. Ask which spellings of `rm` with `-r` and `-f` the starter pattern misses. Check the exit code the starter uses.

3. **Wire it and protect the files (about 8 minutes).** Goal: the hook runs for Claude's shell commands from any working directory, and secrets files are protected from Claude's file tools.
   - Acceptance criteria:
     - `.claude/settings.json` runs the hook before the `Bash` tool, and the command locates the script from the project directory and not from the current directory.
     - `permissions.deny` has `Read` rules that cover `.env` and `config/secrets.env`.
   - Hints: Check which tool the matcher names. A hook command that starts with a relative path breaks when Claude Code is started from a subfolder.

   > **Start Claude Code at the project root.** Confirmed on the class image, 2026-11-15: Claude Code reads project settings from **the folder it starts in, not the git root**. Started in `ledgerlite/src`, the root `.claude/settings.json` is never read at all, so the hook does not fire *and* the deny rules do not apply, and a recursive force delete **can** run. (Do not use `Registered 0 hooks` as your evidence — that line is about plugin hooks and appears from the project root too.) In one run the delete went through; in another Claude Code's own approval check happened to stop it. **Do not count on that** — it is not the control this lab is teaching. `${CLAUDE_PROJECT_DIR}` does not rescue this: if the settings are loaded another way it resolves to `src/`, the hook path breaks, `python3` exits 2, and then *every* Bash call is blocked by accident. There is no team-wide fix — only a personal `settings.local.json` using `git rev-parse --show-toplevel` works from a subfolder. So: start at the root, and know why. The docs use a project directory variable for this — `${CLAUDE_PROJECT_DIR}` and `$CLAUDE_PROJECT_DIR` both work, and the scorer accepts either. Check the spelling of every path in a deny rule. A deny rule on the Read tool is not the same as protecting a file from shell commands. Write that down for the charter.

4. **Fill in the charter (about 6 minutes).** If you ask Claude to edit `charter.md` from inside `ledgerlite`, Claude Code asks permission to read outside the working directory. Allow it once, or copy `charter.md` into the project first. Goal: a charter that tells the truth about where your team stands.
   - Acceptance criteria:
     - At least 6 of the 10 practice areas are decided (Enforced or Reviewed), each with a one-sentence rule and an owner.
     - Every row marked Enforced names a control that exists, as a file or a settings key, in the Control column.
   - Hints: `CLAUDE.md` is a request, so it can never be the control for an Enforced row. If the only thing holding a rule is a person remembering it, the honest status is Reviewed or Undecided. Leave an area Undecided rather than invent a rule.

5. **Score it (about 3 minutes).** Run `python3 check_lab1.py ~/work/ledgerlite charter.md`. Fix the lowest line and run it again.

**Checkpoint:** A blocked-command test that exits 2 (the first hook check in the score output), and a charter with at least 6 of the 10 areas decided. The scorer prints `CHECKPOINT: PASS` when both hold.

**Common problems:**

- The hook prints your message and the command still runs: the exit code is 1, not 2.
- The hook works when you test it by hand and never fires in Claude Code: the matcher names a tool other than `Bash`, or the command path is relative and Claude Code was started from a subfolder.
- Python is `python` and not `python3` on your machine: use the name that works for you in the hook command.
- A Read deny rule that never matches: a typo in the path. Compare `./.env` with `./env`.
- The charter score stays low: a row marked Enforced points at `CLAUDE.md` or at a sentence and not at a file or a setting.
- You tested only the blocked case: check that harmless commands still exit 0.

**Scoring rubric (100 points):**

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
