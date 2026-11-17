# Demo 4: Exit 1 Versus Exit 2

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Demos](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** See that a hook that exits 1 does not block and a hook that exits 2 does, and send the block reason back to Claude. Time: about 10 minutes.

**Files:** `$FILES/demo4-exit-codes`: `project/.claude/hooks/block_rm.py`, `project/.claude/settings.json`, `hooks-source/block_rm_broken.py`, `hooks-source/block_rm_fixed.py`, `fix_hook.sh`, `test_exit_codes.sh`.

**Context:** A hook script reads the tool call as JSON on standard input. Exit code 0 means success. Exit code 2 is a blocking error: on a PreToolUse hook the tool call is blocked and the text on standard error is the reason. Any other exit code is a non-blocking error: the action proceeds. The starter hook prints a good message and then exits 1.

**Steps:**

1. Open `project/.claude/hooks/block_rm.py`. Find `sys.exit(1)` and the matcher `Bash` in `settings.json`.
2. Run the hook by hand, no model needed: `bash test_exit_codes.sh`. The dangerous command prints the message and reports exit code 1.
3. Start `claude` in `project` and ask: `Delete the build folder with rm -rf build`. A notice appears, and the folder is deleted anyway. Check with `ls`.
4. Restore the file: `echo "stale build output" > build/old-output.txt` (create `build` first if needed with `mkdir -p build`).
5. Fix the hook: `bash ../fix_hook.sh fixed`. The script is read on each call, so no restart is needed. Run `bash ../test_exit_codes.sh` again. It now reports exit code 2.
6. Ask the same question again. The call is blocked, and Claude reports the reason from standard error.
7. Write down the three-line rule: 0 allows, 2 blocks, anything else only warns.
8. Switch back to the broken version so you can repeat the demo: `bash ../fix_hook.sh broken`.

**Expected result:** With exit 1 the command runs and the folder is gone. With exit 2 the command does not run, the folder stays, and Claude explains the block.

**Why this matters:** The most common hook bug is an exit code of 1. The author sees the message, believes the rule works, and ships it. The rule never held. This is why every rule needs a test that proves it.
