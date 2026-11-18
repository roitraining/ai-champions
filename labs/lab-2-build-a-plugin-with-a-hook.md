# Lab 2: Build a Plugin With a Hook

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Labs](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** Take a half-built plugin to a working one: fix its hook, write its command, make its checking agent read-only, package it in a marketplace, and test its behavior with an eval suite. Time: 75 minutes.

**Files:** `$FILES/lab2-plugin`: `relnotes-starter/` (the plugin, with an `evals/` folder of six cases), `marketplace-template/`, `score_lab2.py`. Tools: `$FILES/tools/plugin_lint.py`. Review aid: `$FILES/templates/plugin-review.md`.

**Context:** A plugin is a folder with `.claude-plugin/plugin.json` and components at its root: `commands/`, `agents/`, `hooks/hooks.json`. Components are namespaced `plugin:component`. A hook in a plugin names its script with `${CLAUDE_PLUGIN_ROOT}`, because the plugin can be installed anywhere. `claude --plugin-dir <path>` loads a plugin for one session. `claude plugin validate <path>` checks the files. `claude plugin details <name>` lists the contents and the projected token cost. `claude plugin eval` runs the cases in `evals/` and uses model requests. The plugin, `relnotes`, drafts `RELEASE_NOTES.md` from the git log, and a PostToolUse hook checks the file against a format checker. `plugin_lint.py` is a cheap local check that costs nothing. It does not replace `claude plugin validate`, and it tests no behavior.

**Steps:**

1. **Inspect (about 10 minutes).** Goal: a list of what is wrong, before you change anything.
   - Copy `relnotes-starter` to `~/plugins/relnotes`. Run `python3 $FILES/tools/plugin_lint.py ~/plugins/relnotes --marketplace $FILES/lab2-plugin/marketplace-template`, then `claude plugin validate ~/plugins/relnotes`.

   > **Read `validate` output in two halves — everyone hits this.** It prints the
   > plugin's own result first, then a section headed `Plugin directory checks for ...`
   > about submitting to the public plugin catalog. That second half reports a missing
   > `README.md`, a missing `LICENSE` and a missing icon as
   > `Found 2 problems the plugin directory refuses a submission for`, with a `✘`.
   >
   > **Those are not this lab.** The finished answer key reports them too. The tool says
   > so itself at the end of that section: *"These plugin directory checks do not change
   > the result below."* What matters for Step 1 is the first half — a correct plugin
   > prints no `Found N errors` there, a broken one does. Note the exit status is `0`
   > either way, so do not read success from it. (Confirmed against Claude Code 2.1.322, and re-confirmed on the class image's 2.1.311, 2026-11-15.)
   - Acceptance criteria: a list of each FAIL and WARN, with one sentence on why each matters.
   - Hints: read the hook file, the command, the agent and the root `CLAUDE.md`. Compare the plugin name in the manifest with the marketplace entry.

2. **Fix the hook (about 12 minutes).** Goal: the hook script runs wherever the plugin is installed, and you can show it blocks bad notes and passes good ones.
   - Acceptance criteria: the hook is on `PostToolUse` with a matcher that matches `Write` and `Edit`, so it runs after the file is written; `hooks/hooks.json` uses `${CLAUDE_PLUGIN_ROOT}` and no fixed path; the path it names is a file that is really in the plugin; piping a bad `RELEASE_NOTES.md` event into `scripts/lint_notes.py` exits 2 with a message; a good file exits 0.
   - Hints: the starter points at a path on one person's machine. Quote the variable in the command (`${CLAUDE_PLUGIN_ROOT}` and `$CLAUDE_PLUGIN_ROOT` are the same variable, and both tools accept either). The event matters as much as the path: a working script wired to `SessionStart`, or to a matcher that does not match a write, never runs on a write, and both tools score it as no hook at all. The path matters too: both tools read the path the hook names, so `${CLAUDE_PLUGIN_ROOT}/hooks/checkers/lint_notes.py` fails while the script sits in `scripts/`, even though a file of that name exists somewhere in the plugin. You may still write the path another way (`cd "${CLAUDE_PLUGIN_ROOT}" && python3 scripts/lint_notes.py`), and a second, unrelated hook on another event costs nothing. Test the script by hand with a JSON event before you test it in Claude Code. The event the scorer pipes in is a full PostToolUse payload: `hook_event_name`, `session_id`, `transcript_path`, `cwd`, `tool_name`, `tool_input` (with `file_path` and `content`) and `tool_response`, so a script that checks those fields is safe.

3. **Write the command and tighten the agent (about 18 minutes).** Goal: `/relnotes:release-notes` does the job the evals expect, and the checking agent cannot change anything.
   - Acceptance criteria: the command has a specific description; it **names the git invocation** that works out the commit range and reads the log (`git log --no-merges <from>..<to>`, not "read the git log"); groups entries into the four sections in the order the format checker enforces; ends every bullet with a short commit hash; hands the draft and the log text to the `changelog-auditor` agent before finishing; never invents an entry; and changes nothing except `RELEASE_NOTES.md`. The agent has only read tools, either by listing only read tools or by denying every write tool. No TODO line of its own remains (naming TODO as text the format checker rejects is fine, and the command is a good place to say so).
   - Hints: the evals are the specification, so read all six prompts and graders first. The scorer grades the component the plugin declares, not the best file it can find: the 20 command points come from `commands/release-notes.md` and the 10 agent points from the agent whose frontmatter `name` is `changelog-auditor`, wherever that file sits. Other files in `commands/` and `agents/` are neither graded nor penalised, so a scratch file cannot earn the points for a component you have not written yet. The agent has no shell, so ask what it needs to be given. Rules that must apply belong in the command or a skill, where an eval can test them. A `CLAUDE.md` at the plugin root is not loaded as project context, so do not rely on it. A vague description can stop the command from being chosen.

4. **Package it (about 10 minutes).** Goal: your plugin installable from a marketplace of your own.
   - Acceptance criteria: a marketplace folder with `.claude-plugin/marketplace.json`, the plugin at `plugins/relnotes`, an entry whose name matches the manifest name and whose `source` path exists, and `claude plugin validate` passes on both the plugin and the marketplace.
   - Hints: start from `marketplace-template`. Add it with `claude plugin marketplace add <folder>`. Compare the template's entry name with your manifest name. The two copies drift: the scorer checks that the plugin under the entry's `source` is the same plugin it just graded, so copy your fixed plugin over it (or point `source` at the folder you have been editing) every time you change it.

5. **Evaluate (about 20 minutes).** Goal: evidence that the behavior holds, within a cost cap.
   - Acceptance criteria: a run of the suite with the number of runs and a cost cap that you chose; the result files or summary saved; and a short note on any case that failed and what you changed because of it.
   - Before you run it, check the sandbox: `bash $FILES/setup/classroom-sandbox.sh --check`. Measured on the class image, when the sandbox cannot start the evals fail at random (a different one or two of six cases each run, each with `RELEASE_NOTES.md does not exist`) because every shell command inside the run is refused; the same suite scored 6 of 6 after `--on`. Read Lab 3 Step 1 first: `--on` is machine-wide, so it is a decision, and you run `--off` afterwards. If the check already says nothing is blocking the sandbox, as it does on the current class image, you need neither.
   - Hints: `claude plugin eval ~/plugins/relnotes --runs 1 --ablation none --max-cost-usd <your cap> --allow-tools Write Bash --scaffold --trust-plugin --no-publish` keeps the first run small. **Every one of those flags earns its place**, and all four were found by running it: `--allow-tools` because Write and Bash are gated at the runner on top of each case's `allowed_tools` (1.00 with the grant, 0.00 without); `--scaffold` because four of the six cases build a git repository to read, and without it they run in an empty workspace and score about 0.33; `--trust-plugin` because a non-interactive run otherwise stops to ask you to trust the directory; and `--no-publish` because **`plugin eval` publishes its HTML report to claude.ai by default** — decide whether you want that before you run it, not after. **The `--allow-tools` grant is not optional.** `Write`, `Bash` and `Edit` are gated at the runner, on top of the `allowed_tools` line in each case, so without it the cases that draft `RELEASE_NOTES.md` cannot create the file and every grader that reads it fails. Measured on 2026-11-14 with Claude Code 2.1.322 on Windows, and re-confirmed on the class image's 2.1.311: `hook-lints-bad-notes` scores **1.00 with the grant and 0.00 without it**, and the only difference is the flag. A case that checks the format hook (`hook-lints-bad-notes`) tests whether Claude sees the hook's message. **Confirmed 2026-11-14 against the hooks reference.** The per-event table reads: `| PostToolUse | No | Shows stderr to Claude; the tool already ran |`. So a PostToolUse hook that exits 2 **cannot block** — the write has already happened — but its stderr **does reach Claude**, which is exactly what this plugin needs: the linter cannot stop a bad `RELEASE_NOTES.md` being written, it tells Claude what is wrong so Claude rewrites it. If a student expects the write to be blocked, that is the misunderstanding to correct. The `ignores-unrelated` case tests whether your command triggers on the wrong prompts. Shortening a description can stop a command being chosen, so rerun the cases after you edit one.

6. **Collect the evidence (about 5 minutes).** Goal: one `EVIDENCE.md` you can hand in.
   - Acceptance criteria: it holds the output of `claude plugin validate`, the output of `claude --plugin-dir ~/plugins/relnotes plugin details relnotes` including the token cost, and the eval summary.
   - Paste the real output, each paste under the command line that produced it. Each row reads **only** the block under its own `claude plugin ...` line and nothing else in the file: the validate block has to report success (`0 errors`, `passed`, `is valid`), the details block has to carry the always-on token figure as a number, and the eval block has to carry the case results plus the run settings you chose (`--runs`, `--max-cost-usd`, a threshold, or the `aggregate-result` or report path). There is no fallback to the rest of the file, so a summary sentence with no command line above it scores zero, and so does a block that says the command was not run. A case that failed is fine to report; a suite that never ran is not.
   - Then run `python3 $FILES/lab2-plugin/score_lab2.py ~/plugins/relnotes --marketplace <your marketplace> --evidence EVIDENCE.md`.

**Checkpoint:** `score_lab2.py` reports at least 80 **and all three evidence rows score**, the hook exits 2 on bad notes and 0 on good notes, and the plugin validates. The file work of Steps 1-4 alone tops out at 80 of the 100, so a run with no evidence can meet the number without Steps 5 and 6: the evidence rows are what those steps pay for.

**Common problems:**

- `Hook command does not use ${CLAUDE_PLUGIN_ROOT}`: the starter's fixed path is still there.
- `Hook points at <path>, which does not exist in the plugin` / `The after-a-write hook points at a script that exists inside the plugin` fails: the hook names a path the plugin does not have. Both tools read the path you wrote, not the file name, so a `lint_notes.py` sitting in `scripts/` does not satisfy a hook that asks for `hooks/checkers/lint_notes.py`.
- `No hook runs after a write` / `hooks.json defines a command hook that runs after a write` fails: the linter is on the wrong event or behind a matcher that does not match a write. Put it on `PostToolUse` with no matcher or `Write|Edit`.
- The hook never fires in a session: the plugin is not loaded. Start with `claude --plugin-dir ~/plugins/relnotes`, or run `/reload-plugins` after an install.
- The marketplace install says it cannot find the plugin: the entry name does not match the manifest name, or `source` points at the wrong folder.
- Every eval case fails, or several score about 0.33: **first check you passed `--allow-tools Write Bash --scaffold`** — without `--scaffold` the cases that read a git log run in an empty workspace, and without the tool grant they cannot write the file - without it the cases cannot write `RELEASE_NOTES.md` and every grader that reads the file fails, which looks exactly like a broken plugin. Then check that Git is 2.31 or later and that you are signed in. Check the run with `--runs 1 --case <one-case>` first.
- The suite is too slow or too costly: lower the number of runs, skip the baseline with `--ablation none`, and set `--max-cost-usd`.
- The command is not chosen in `groups-by-type`: its description is too vague, or it does not say when to use it.
- `Marketplace entry matches the manifest and its source holds the graded plugin` fails after you edited the plugin: the copy inside the marketplace is now the old one. Copy it over again, or keep one copy and point `source` at it.
- An evidence row fails on output you really did paste: the row reads only what sits under its own `claude plugin ...` line, so paste the command line with its output. The validate block has to show the run succeeding, the details block needs the token number, and the eval block needs the case results with the run settings. Paste the whole block, not a sentence about it.
- A command row fails on a file you did write: the scorer grades `commands/release-notes.md` and the agent named `changelog-auditor`. If your work is in another file, rename it (or set the agent's frontmatter `name`); the scorer says which file it graded.

**Scoring rubric (100 points, from `score_lab2.py`):**

| Item | Points |
|---|---|
| Manifest with a kebab-case name | 5 |
| `hooks.json` defines a hook that runs after a write (`PostToolUse`, matching `Write`/`Edit`), uses `${CLAUDE_PLUGIN_ROOT}`, and points at a script that is really there | 20 |
| Hook behavior: exit 2 on bad notes, 0 on good notes, ignores other files | 15 |
| Command (`commands/release-notes.md`): no leftover TODO, specific description, names the file and the agent, names the git invocation that works out the commit range and reads the log, names the four sections and puts them in order, never invents and changes nothing else | 20 |
| Checking agent has read-only tools | 10 |
| Marketplace entry matches the manifest and its source holds the plugin | 10 |
| Evidence: validate output, token cost, eval summary | 20 |

The scorer checks the files and the pasted evidence. The 20 evidence points are a plausibility check on text: they cannot prove the commands ran, so the facilitator checks a screen or a result file for the eval run. Where a row splits (the four sections, the two safety rules), each half carries its own points, so one phrasing choice does not cost a whole row.
