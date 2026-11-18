# Demo 8: Evaluate a Plugin With a Test Suite

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 12 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

You test a plugin's behavior with an eval suite, read its always-on cost, and say what a passing score does not prove.

`claude plugin validate` checks files for syntax and schema errors. It does not test behavior. `claude plugin eval` runs cases, each a prompt plus graders, in isolated sessions with only the plugin loaded. By default it also runs without the plugin as a baseline. It uses model credits and needs Git 2.31 or later. The plugin, `branch-guard`, has three cases: the hook blocks a force push, the command is chosen for a status question, and the plugin stays out of the way on an unrelated question.

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md): `claude --version` prints a version and `claude auth status` shows you are signed in
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`
- [ ] `git --version` prints 2.31 or later

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Copy the plugin and run the free checks

The eval writes result files inside the plugin folder, so you work on a copy. Open a terminal (the **Terminal Emulator** icon on the desktop) and run:

```bash
mkdir -p ~/work && rm -rf ~/work/demo8 && cp -r $FILES/demo7-marketplace/champions-tools ~/work/demo8
P=$HOME/work/demo8/plugins/branch-guard
```

`P` is a shell variable that holds the plugin's path. It lasts only in this terminal window. If you open a new window, run the second line again.

Run the lint check. It reads files, calls no model and costs nothing:

```bash
python3 $FILES/tools/plugin_lint.py $P --marketplace ~/work/demo8
```

**Expected output:**

```
[ok  ] Manifest name is 'branch-guard'
[FAIL] No hook runs after a write. A format checker for a file Claude just wrote belongs on PostToolUse with no matcher or a matcher that matches Write and Edit; score_lab2.py gives the wiring and behavior points only to a hook on that event. Found: PreToolUse Bash
[ok  ] Every eval case has at least one grader (3 cases)
[ok  ] Marketplace entry name matches the manifest name

1 FAIL, 0 WARN. Now run: claude plugin validate /home/<you>/work/demo8/plugins/branch-guard
```

The command exits with code 1. **That one FAIL is expected, and there is nothing to fix.** The lint applies a rule written for the Lab 2 plugin, which has a format checker that must run after a write. `branch-guard` has no such checker. It blocks a command before it runs.

Now run the official check:

```bash
claude plugin validate $P
```

**Expected output:**

```
Validating plugin manifest: /home/<you>/work/demo8/plugins/branch-guard/.claude-plugin/plugin.json

Plugin directory checks for /home/<you>/work/demo8/plugins/branch-guard. The plugin directory is the catalog that plugins are submitted to; this is a subset of what it runs.

✘ Found 1 problem the plugin directory refuses a submission for:

  ❯ LICENSE: License missing (LICENSE_MISSING). This plugin has no LICENSE file and plugin.json has no `license`. The directory requires one of them.
    Fix: Add a LICENSE file to the plugin folder, or set `license` (an SPDX id) in plugin.json. A LICENSE at the repository root also counts for a plugin in a sub-folder.

⚠ Found 1 plugin directory warning:

  ❯ .claude-plugin/plugin.json icon: No icon (ICON_MISSING). No icon found in the plugin. The validator looked for `icon` in plugin.json and for a file at .claude-plugin/icon.png or .svg, assets/icon.png or .svg, or a similar path.
```

Read this in two halves. The first line is the result for the plugin's own files. It has no `Found N errors` line, so the plugin's files are valid. Everything after it is the `Plugin directory checks`, which apply to submitting a plugin to the public plugin directory. A missing LICENSE and icon do not matter for this demo. The command exits with code 0 either way, so read the text, not the exit code.

---

## Step 2: Read the always-on cost

List what the plugin contains and what it costs:

```bash
claude --plugin-dir $P plugin details branch-guard
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

The always-on figure is the plugin's name and description. They sit in your context window every turn. The hook is marked harness-only, so it adds nothing there, but it still runs code on your machine.

---

## Step 3: Read the eval case

A case is a folder with a prompt and graders. Print the prompt and the two graders of the first case:

```bash
cat $P/evals/blocks-force-push/prompt.md
cat $P/evals/blocks-force-push/graders/*.md
```

Look at what each grader checks. One is a regex over the session trace. The other is a judgment made by a model. Write your answers in a notes file:

```bash
nano ~/work/demo8-notes.md
```

Type two lines:

```
Regex grader: <what text it looks for>
Model grader: <what the reply must say to pass>
```

Save with **Ctrl+O**, then **Enter**. Exit with **Ctrl+X**.

<details>
<summary>Show the answers</summary>

```
Regex grader: BRANCH-GUARD, the text the hook prints, anywhere in the trace
Model grader: the reply says the push was blocked (by a guard, a hook or a rule) and gives the reason
```

The regex proves the hook's message reached Claude. The model grader proves Claude told you about it. Both must pass.

</details>

---

## Step 4: Run one case

Run the force-push case once, without the baseline, so it stays short and cheap:

```bash
claude plugin eval $P/evals/blocks-force-push/case.yaml --runs 1 --ablation none --max-cost-usd 2 --allow-tools Bash --no-publish
```

The flags:

- `--runs 1` runs the case once.
- `--ablation none` skips the baseline run without the plugin.
- `--max-cost-usd 2` stops the run if it costs more than $2. One case costs about $0.09, so the cap is a safety margin.
- `--allow-tools Bash` is required. The force push needs a shell. On the class image this case scores 0.00 without the flag and 1.00 with it.
- `--no-publish` keeps the HTML report on this machine. Without it, `plugin eval` publishes the report to claude.ai.

**Expected output** (the last lines):

```
  blocks-force-push run 1/1: score 1.00  $0.09
    ✓ hook-message-reached-claude (weight 1): matched BRANCH-GUARD
    ✓ reply-reports-the-block (weight 1): judge votes: PASS PASS PASS
✓ blocks-force-push  score 1.00  (1 run)  $0.09

CASE               SCORE PASS% RUNS COST    NOTES
blocks-force-push  1.00  100%  1    $0.09

1 case(s) · 9s · $0.09
Report: /home/<you>/work/demo8/plugins/branch-guard/evals/results/<timestamp>/report.html
```

The output also warns that the case's scaffold script is not run without `--scaffold`. This case does not need it, and it still scores 1.00. The two lines under the run are the two graders from Step 3: the regex found `BRANCH-GUARD`, and three model votes agreed the reply reported the block.

> **It stops and asks whether to trust the plugin folder?** Answer yes, or add `--trust-plugin` to the command and run it again.
>
> **The score is 0.00?** Check that the command includes `--allow-tools Bash`.
>
> **An error about Git?** The eval needs Git 2.31 or later. Run `git --version`.

---

## Step 5: Read the result

Check the exit code of that run before you run anything else:

```bash
echo $?
```

The exit codes: `0` means every case passed, `1` means a case scored below the threshold or failed, and `2` means a partial run. Then list the result files:

```bash
ls $P/evals/results/*/
```

**Expected result:** a folder named with the run time, holding `report.html` and `aggregate-result.json`, plus the per-case files. Open the report in a browser on the desktop. In Firefox, press **Ctrl+O** and type the path to `report.html`.

---

## Step 6: Say what a pass does not prove

The case passed. In the same notes file, add two things the suite does not test:

```bash
nano ~/work/demo8-notes.md
```

```
Not tested 1: <something the suite does not cover>
Not tested 2: <something the suite does not cover>
```

<details>
<summary>Show example answers</summary>

- A command that triggers too eagerly. The `ignores-unrelated` case tests this. You did not run it.
- A hook that blocks too much. No case runs a feature-branch push through the hook.
- A second model. The case ran on one model.
- Behavior after the plugin changes. A pass tests today's files.

</details>

---

## What you learned

- A plugin that validates can still trigger on the wrong prompts or fail to fire on the right one. An eval suite is the test for behavior.
- Read the always-on cost before you ship a plugin. Descriptions are in context every turn.
- A pass is evidence for the cases you wrote, and only for those.

## Cleanup

Delete your copy, which includes the result files:

```bash
rm -rf ~/work/demo8
```
