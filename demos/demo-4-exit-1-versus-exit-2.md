# Demo 4: Exit 1 Versus Exit 2

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 10 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

A hook is a script that Claude Code runs before a tool. Its exit code is its answer. You run a hook that prints a good message and exits with `1`, and watch Claude Code delete a folder anyway. You change one number to `2` and watch the same command get blocked.

## Prerequisites

- [ ] `claude auth status` shows you are signed in (see [`SETUP.md`](../SETUP.md))
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Read the hook and its wiring

Open a terminal (the **Terminal Emulator** icon on the desktop). Go to the demo's project folder:

```bash
cd $FILES/demo4-exit-codes/project
```

A hook script receives the tool call as JSON on standard input. Its exit code tells Claude Code what to do:

| Exit code | What Claude Code does |
|---|---|
| `0` | Lets the tool call run |
| `2` | **Blocks** the tool call and sends the text on standard error back to Claude |
| anything else, such as `1` | Shows a notice but **lets the tool call run anyway** |

Find the two lines that matter. The first shows which tool the hook guards. The second shows the hook's exit codes:

```bash
grep -n matcher .claude/settings.json
grep -n 'sys.exit' .claude/hooks/block_rm.py
```

**Expected output:**

```
5:        "matcher": "Bash",
16:    sys.exit(1)
17:sys.exit(0)
```

The matcher is `Bash`, so the hook runs before every shell command. Line 16 is the exit code for a dangerous command. It is `1`.

---

## Step 2: Run the hook by hand

You do not need Claude Code to test a hook. The test script pipes a dangerous command and a safe command into the hook and prints the exit codes. Run it from the demo folder:

```bash
cd ..
bash test_exit_codes.sh
```

**Expected output:**

```
--- dangerous command
Blocked: recursive force delete is not allowed here. Delete files one at a time, or ask the user.
exit code: 1   (2 blocks, 1 does not)
--- safe command
exit code: 0   (0 lets it run)
```

The hook prints the right message, then exits with `1`. A block needs `2`.

---

## Step 3: Watch the delete go through

Start Claude Code in the project folder:

```bash
cd project
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to move to **Yes, I trust this folder**, then press **Enter**. The bottom of the screen shows `auto mode on`. Leave it.

Type this prompt and press Enter:

```
Delete the build folder with rm -rf build
```

**Expected result:** a notice appears about the hook, and the folder is deleted anyway. Claude reports that it ran the command.

Leave Claude Code by typing `/exit` and pressing Enter. Confirm the folder is gone:

```bash
ls
```

**Expected output:** no `build` entry in the list.

> **Claude declined to delete the folder, or asked you to confirm?** Claude sometimes pauses on a recursive delete. Start `claude` again and type: `This is a scratch folder. Run rm -rf build and show me the exact output.`
>
> **The folder is still there?** Claude did not run the command. Run the prompt above again until Claude runs it. The demo needs the delete to go through once.

---

## Step 4: Restore the folder

Recreate the throwaway file so you can run the delete again:

```bash
mkdir -p build && echo "stale build output (fictional)" > build/old-output.txt
ls build
```

**Expected output:**

```
old-output.txt
```

---

## Step 5: Fix the hook

The fix is one number: `sys.exit(1)` becomes `sys.exit(2)`. The demo keeps a fixed copy of the hook so you do not edit code. Swap it in:

```bash
bash ../fix_hook.sh fixed
```

**Expected output:**

```
Hook is now the fixed version.
```

Claude Code reads the hook script on every call, so you do not need to restart anything. Run the test script again:

```bash
bash ../test_exit_codes.sh
```

**Expected output:**

```
--- dangerous command
Blocked: recursive force delete is not allowed here. Delete files one at a time, or ask the user.
exit code: 2   (2 blocks, 1 does not)
--- safe command
exit code: 0   (0 lets it run)
```

The message is the same. The exit code is now `2`.

---

## Step 6: Watch the delete get blocked

Start a session and ask the same question:

```bash
claude
```

```
Delete the build folder with rm -rf build
```

**Expected result:** the command does not run. Claude reports the reason from standard error: `Blocked: recursive force delete is not allowed here. Delete files one at a time, or ask the user.` Claude may then offer to delete the files one at a time. Do not accept. You are testing the block.

Leave Claude Code by typing `/exit` and pressing Enter. Confirm the folder survived:

```bash
ls build
```

**Expected output:**

```
old-output.txt
```

> **The folder was deleted again?** The fixed hook is not in place. Run `bash ../test_exit_codes.sh` and check it reports `exit code: 2`. If it reports `1`, run `bash ../fix_hook.sh fixed` again.
>
> **Claude declined before the hook ran?** Say: `This is a scratch folder. Run rm -rf build and show me the exact output.` Then the hook has to do the blocking.

---

## Step 7: Write down the rule

Write the three-line rule in a notes file. Create the folder and open the file in `nano`:

```bash
mkdir -p ~/work
nano ~/work/demo4-notes.md
```

Type three lines, one for each exit code, in your own words. Press **Ctrl+O**, then **Enter**, to save. Press **Ctrl+X** to exit.

<details>
<summary>Show the three lines</summary>

```
Exit 0: the tool call is allowed.
Exit 2: the tool call is blocked and the message goes back to Claude.
Any other exit code: a warning only. The tool call still runs.
```

</details>

---

## Step 8: Put the broken hook back

Swap the broken version in, so the demo can be run again:

```bash
bash ../fix_hook.sh broken
```

**Expected output:**

```
Hook is now the broken version.
```

---

## What you saw

- With exit 1 the command ran and the folder was gone. The hook printed a message, and nothing was stopped.
- With exit 2 the command did not run and the folder stayed. Claude read the reason and explained the block.

The most common hook bug is an exit code of 1. The author sees the message, believes the rule works, and ships it. The rule never held. This is why every rule needs a test that proves it.

## Cleanup

Step 8 put the demo back as you found it. To remove your notes:

```bash
rm -f ~/work/demo4-notes.md
```
