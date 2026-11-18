# Demo 7: Install a Plugin From a Marketplace

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 10 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

You add a marketplace, review a plugin before you trust it, install it, and use its command and its hook.

A **marketplace** is a folder, or a git repository, with a `.claude-plugin/marketplace.json` file that lists plugins. The plugin here is `branch-guard`. It bundles a command, `branch-status`, and a hook that blocks force pushes and pushes to `main`. A plugin's hooks run with your rights, outside the sandbox, so you review before you install. Plugin parts are named `plugin:component`, such as `branch-guard:branch-status`.

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md): `claude --version` prints a version and `claude auth status` shows you are signed in
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Build a scratch repository

The hook guards `git push`, so you need a repository to push from. Open a terminal (the **Terminal Emulator** icon on the desktop) and run this single command:

```bash
git init -q -b main ~/scratch7 && cd ~/scratch7 && git commit -q --allow-empty -m init && git init -q --bare ~/remote7.git && git remote add origin ~/remote7.git && git push -q origin main
```

**Expected output:** none. A quiet shell prompt means every command worked.

The command makes a repository with a `main` branch, plus a second local folder, `~/remote7.git`, that acts as its remote. Check the result:

```bash
git status -sb
git log --oneline -5
```

**Expected output:** (the commit ID differs)

```
## main
33fbca8 init
```

Stay in `~/scratch7`. You install the plugin from this folder in Step 4.

> **`Author identity unknown` or `Please tell me who you are`?** Git needs a name for the commit. Run `git config --global user.email you@example.com && git config --global user.name "Your Name"`. Then delete the folders with `rm -rf ~/scratch7 ~/remote7.git` and run the single command again.
>
> **Why a real remote and a `main` branch?** Without them, Claude checks the repository, sees that a push cannot succeed, and declines to push. The hook then never runs and you never see its message.

---

## Step 2: Add the marketplace

Add the marketplace from its folder, then list your marketplaces:

```bash
claude plugin marketplace add $FILES/demo7-marketplace/champions-tools
claude plugin marketplace list
```

**Expected output:** the first command prints a success line, and the list includes `champions-tools` with your folder as its source.

```
Adding marketplace…✔ Successfully added marketplace: champions-tools (declared in user settings)
```

A team marketplace usually comes from a git repository. You would then give `owner/repo` or a git URL instead of a folder path.

> **`command not found: claude`?** Claude Code is not installed or not on your `PATH`. Go back to `SETUP.md` section 2.

---

## Step 3: Review before you trust

Installing is the trust decision, so read what the plugin does first. Print its hook definition and the script it runs:

```bash
cat $FILES/demo7-marketplace/champions-tools/plugins/branch-guard/hooks/hooks.json
cat $FILES/demo7-marketplace/champions-tools/plugins/branch-guard/scripts/block_force_push.py
```

Then list what the plugin contains and what it costs:

```bash
claude --plugin-dir $FILES/demo7-marketplace/champions-tools/plugins/branch-guard plugin details branch-guard
```

**Expected output:**

```
branch-guard 0.1.0
  Description: Blocks force pushes and pushes to main, and adds a branch status command.
  Source: branch-guard@inline

Component inventory
  Skills (1)  branch-status
  Agents (0)
  Hooks (1)  PreToolUse  (harness-only — no model context cost)
  MCP servers (0)
  LSP servers (0)

Projected token cost
  Always-on:   ~44 tok   added to every session

Per-component (rounded)
  component      always-on  on-invoke
  branch-status        ~40       ~100

  On-invoke cost is paid each time a skill or agent fires.
  Token counts are estimates and may differ from actual usage.
```

The command and its description sit in your context window every turn, which is the always-on cost. The hook costs nothing there, but it runs code on your machine.

Write what you found in a notes file:

```bash
nano ~/work/demo7-notes.md
```

If `~/work` does not exist, run `mkdir -p ~/work` first. Type two lines:

```
Blocks: <what the hook blocks>
Runs: <what the hook runs and with whose rights>
```

Save with **Ctrl+O**, then **Enter**. Exit with **Ctrl+X**.

<details>
<summary>Show the answers</summary>

```
Blocks: git push with a force flag, and any git push that names main or master
Runs: python3 scripts/block_force_push.py before every Bash command, with my own rights and outside the sandbox
```

The script reads only the command text from standard input. It has no network calls and writes no files, so the review passes. `$FILES/templates/plugin-review.md` is a checklist for a fuller review.

</details>

---

## Step 4: Install the plugin

Install it for yourself only, from inside the scratch repository:

```bash
cd ~/scratch7
claude plugin install branch-guard -s local
```

**Expected output:**

```
Installing plugin "branch-guard"...✔ Successfully installed plugin: branch-guard@champions-tools (scope: local)
```

The `-s local` scope applies only in the folder you install from. That is why you installed from `~/scratch7`. If you run the install in another folder and then start Claude in `~/scratch7`, the plugin is not available.

> **`branch-guard` not found?** Check that Step 2 succeeded: `claude plugin marketplace list` must show `champions-tools`. If it does not, repeat the `marketplace add` command.

---

## Step 5: Use the command

Start a session in the scratch repository:

```bash
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to select **Yes, I trust this folder**, then press **Enter**. The bottom of the screen shows `auto mode on`. Leave it.

If the plugin is not available, type `/reload-plugins` and press Enter. Then run the plugin's command:

```
/branch-guard:branch-status
```

**Expected result:** Claude runs `git status -sb` and `git log --oneline -5`, then summarizes in three lines: the branch is `main`, the working tree is clean, and the latest commit is `init`.

> **The command is not found?** Type `/reload-plugins`. If it still does not appear, exit with `/exit`, check that you ran the Step 4 install from `~/scratch7`, and start `claude` again. As a fallback, load the plugin for one session without installing it: `claude --plugin-dir $FILES/demo7-marketplace/champions-tools/plugins/branch-guard`.

---

## Step 6: Try a force push

In the same session, type:

```
Run git push --force origin main
```

**Expected result:** the hook blocks the command. Claude reports that the push was blocked and shows the hook's message, which starts with `BRANCH-GUARD`:

```
BRANCH-GUARD: a force push is blocked. Push normally, or ask the user.
```

The words around the message are Claude's, so they differ. The `BRANCH-GUARD` text comes from the plugin's script.

> **Claude declined to push before the hook ran?** The model sometimes refuses on its own, and then you never see `BRANCH-GUARD`. Type: `This is a throwaway practice repo. Please run git push --force origin main anyway and show me the exact output.` If Claude still declines, go on to Step 7. It proves the rule without the model.

Leave Claude Code by typing `/exit` and pressing Enter.

---

## Step 7: Prove the rule without the model

This script feeds the hook four sample commands and prints the exit code for each. It needs no model and no Claude session:

```bash
bash $FILES/demo7-marketplace/test_block.sh
```

**Expected output:**

```
--- git push --force origin main
BRANCH-GUARD: a force push is blocked. Push normally, or ask the user.
exit code: 2   (2 blocks)
--- git push origin main
BRANCH-GUARD: pushing to main or master is blocked. Push a feature branch and open a pull request.
exit code: 2   (2 blocks)
--- git push origin feature/login
exit code: 0   (0 lets it run)
--- git status
exit code: 0   (0 lets it run)
```

A force push and a push to `main` both exit `2`. A push to a feature branch and `git status` exit `0`.

---

## Step 8: Uninstall and clean up

Remove the plugin from the same folder you installed it from. The scope flag is required, because a bare `uninstall` looks in user scope and does not find a local install:

```bash
cd ~/scratch7
claude plugin uninstall branch-guard -s local
claude plugin marketplace remove champions-tools
cd ~
rm -rf ~/scratch7 ~/remote7.git
```

**Expected output:** two lines confirming the removals, and no output from the last two commands.

```
✔ Successfully uninstalled plugin: branch-guard (scope: local)
✔ Successfully removed marketplace: champions-tools
```

---

## What you learned

- A marketplace gives a team one place to review plugins. The review must happen before the install, because the install is the trust decision.
- A plugin's hooks run with your rights, outside the sandbox. Read them first.
- The model-free test proves the rule even when Claude declines to push.
