# Lab 2: Build a Plugin With a Hook

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 75 minutes

> Part of **[AI Champions Training: Labs](README.md)**.

## What you will do

A **plugin** is a folder that adds commands, agents and hooks to Claude Code. You get a half-built plugin called `relnotes`. It drafts `RELEASE_NOTES.md` from the git log, and a hook checks the file's format after Claude writes it. You will fix what is broken, package the plugin in a marketplace, and test its behavior with an eval suite.

| Part of the plugin | What you do |
|---|---|
| `hooks/hooks.json` | Fix the hook so it runs on any machine |
| `commands/release-notes.md` | Write the command body |
| `agents/changelog-auditor.md` | Make the checking agent read-only |
| A marketplace folder | Package the plugin so others can install it |
| `evals/` | Run six test cases and save the results as evidence |

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md): `claude --version` prints a version and `claude auth status` shows you are signed in
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`
- [ ] Git is version 2.31 or later. Run `git --version`
- [ ] You know Step 8 uses model requests on your own seat. You set a cost cap there

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Copy the plugin and list what is wrong

Make your own copy of the starter plugin. Open a terminal (the **Terminal Emulator** icon on the desktop) and run:

```bash
mkdir -p ~/plugins && cp -r $FILES/lab2-plugin/relnotes-starter ~/plugins/relnotes
```

Run the free local check. `plugin_lint.py` reads the plugin's files and costs nothing. It does not test behavior:

```bash
python3 $FILES/tools/plugin_lint.py ~/plugins/relnotes --marketplace $FILES/lab2-plugin/marketplace-template
```

**Expected output:**

```
[WARN] plugin.json still names the template author. Put the owner of the plugin in `author`, so a team can tell who to ask about it.
[ok  ] Manifest name is 'relnotes'
[FAIL] hooks/hooks.json contains a fixed absolute path. Use ${CLAUDE_PLUGIN_ROOT}.
[FAIL] Hook command does not use ${CLAUDE_PLUGIN_ROOT}: python3 /home/student/plugins/relnotes/scripts/lint_notes.py
[WARN] changelog-auditor.md: 'permissionMode' may be ignored in a plugin agent (unconfirmed). Do not rely on it for a control.
[FAIL] changelog-auditor.md: a checking agent has write-capable tools: Bash, Edit, Write
[WARN] release-notes.md: description is only 20 characters. A vague description can stop the command from being chosen.
[FAIL] release-notes.md: still contains a TODO line of its own. Naming TODO as text the format hook rejects is fine; leaving 'TODO: write ...' is not.
[WARN] A CLAUDE.md at the plugin root is not loaded as project context (claude plugin validate says so too). Put rules that must apply into a command or skill, where you can test them with an eval.
[ok  ] Every eval case has at least one grader (6 cases)
[WARN] marketplace.json still names the template owner. Put your team in `owner`.
[FAIL] No marketplace entry named 'relnotes' (entries: ['release-notes']). Entry name and manifest name must match.
[FAIL] Entry 'release-notes': source path ./plugins/relnotes does not exist under the marketplace

6 FAIL, 5 WARN. Now run: claude plugin validate /home/<you>/plugins/relnotes
```

Every `[FAIL]` and `[WARN]` is something to fix or understand. Now run Claude Code's own checker:

```bash
claude plugin validate ~/plugins/relnotes
```

**Expected output:** the command prints in two halves.

```
Validating plugin manifest: /home/<you>/plugins/relnotes/.claude-plugin/plugin.json

Validating plugin: /home/<you>/plugins/relnotes/CLAUDE.md

⚠ Found 1 warning:

  ❯ root: CLAUDE.md at the plugin root is not loaded as project context. To ship context with your plugin, use a skill (skills/<name>/SKILL.md) instead.

Plugin directory checks for /home/<you>/plugins/relnotes. The plugin directory is the catalog that plugins are submitted to; this is a subset of what it runs.

✘ Found 2 problems the plugin directory refuses a submission for:

  ❯ README.md: README missing (README_MISSING). ...
```

> **Read the two halves separately.** The first half is the plugin's own result. A broken plugin prints `Found N errors` there. The second half, headed `Plugin directory checks for ...`, is about submitting to the public plugin catalog. It reports a missing `README.md`, `LICENSE` and icon with a `✘`. **Those are not part of this lab.** The finished answer key reports them too, and the tool ends that half with "These plugin directory checks do not change the result below." The exit status is `0` either way, so do not read success from it.

Write down what you found. Create a notes file and list each `[FAIL]` and `[WARN]` with one sentence on why it matters:

```bash
mkdir -p ~/work && nano ~/work/lab2-notes.md
```

Type your list. **Ctrl+O**, then **Enter**, saves. **Ctrl+X** exits. To record the review in a structured form, you can also copy `$FILES/templates/plugin-review.md` and fill it in.

<details>
<summary>Show why each finding matters</summary>

| Finding | Why it matters |
|---|---|
| Fixed path `/home/student/...` in `hooks.json` | The path exists only on one person's machine. On any other machine the hook never runs. |
| Agent has `Bash`, `Edit`, `Write` | A checking agent that can write can change the file it is checking. A checker should only read. |
| `permissionMode` in the agent | A plugin agent may ignore it. Do not use it as a control. |
| `TODO` in the command | The command has no body, so Claude has no instructions. |
| 20-character command description | Claude picks a command by its description. A vague one may never be chosen. |
| `CLAUDE.md` at the plugin root | Claude Code does not load it as project context. Rules that must apply belong in the command, where an eval can test them. |
| Template author and owner | A team needs to know whom to ask about a plugin it installs. |
| Marketplace entry `release-notes` and manifest `relnotes` | The two names must match, or the install cannot find the plugin. |
| `source` path does not exist | The marketplace has no plugin folder at that path yet. |

</details>

> **`python3: can't open file`?** The path is wrong. Check that `~/plugins/relnotes` exists with `ls ~/plugins/relnotes`.
>
> **`cp: cannot stat`?** `$FILES` is empty. Fix it with the tip in Prerequisites and run the `cp` command again.

---

## Step 2: Read the plugin

List the plugin's files, leaving out the `evals` folder for now:

```bash
cd ~/plugins/relnotes && find . -path ./evals -prune -o -type f -print | sort
```

**Expected output:**

```
./.claude-plugin/plugin.json
./CLAUDE.md
./agents/changelog-auditor.md
./commands/release-notes.md
./hooks/hooks.json
./scripts/lint_notes.py
```

What each part does:

- **`.claude-plugin/plugin.json`** is the manifest: the plugin's name, version and author.
- **`commands/release-notes.md`** is the slash command. Claude Code shows it as `/relnotes:release-notes`. Components are namespaced `plugin:component`.
- **`agents/changelog-auditor.md`** is a subagent Claude can hand work to.
- **`hooks/hooks.json`** names scripts Claude Code runs on events.
- **`scripts/lint_notes.py`** checks the format of `RELEASE_NOTES.md`.
- **`evals/`** holds six test cases. Each has a prompt and graders.

Print the hook file:

```bash
cat hooks/hooks.json
```

It runs `lint_notes.py` on the `PostToolUse` event, after Claude uses `Write` or `Edit`. The script reads the event as JSON on standard input. If the notes break a rule, it exits `2` and prints a message on standard error.

> **A `PostToolUse` hook cannot block the write.** The file is already written when the hook runs. The hook's message still reaches Claude, and that is the point of this plugin. The checker cannot stop a bad `RELEASE_NOTES.md` from being saved, but it tells Claude what is wrong so Claude rewrites it. If you expect the write to be blocked, that is the misunderstanding to correct.

Also read the six eval prompts. They are the specification for the command you write in Step 5:

```bash
cat evals/*/prompt.md
```

---

## Step 3: Test the checker script by hand

The script `lint_notes.py` is correct. The problem is the path in `hooks.json`. First prove the script works. Define a helper that sends a fake `PostToolUse` event to it:

```bash
lint() { echo "{\"tool_name\":\"Write\",\"tool_input\":{\"file_path\":\"$1\"}}" | python3 ~/plugins/relnotes/scripts/lint_notes.py; echo "exit=$?"; }
```

Create a bad notes file and test it:

```bash
mkdir -p ~/work/notes-test && printf 'TODO write this later\n' > ~/work/notes-test/RELEASE_NOTES.md
lint ~/work/notes-test/RELEASE_NOTES.md
```

**Expected output:**

```
RELNOTES-LINT: RELEASE_NOTES.md breaks the format:
- The first line must start with "# Release notes".
- Line 1: placeholder text (TODO write this later).
exit=2
```

Now a good file:

```bash
printf '# Release notes: v1.1.0 (since v1.0.0)\n\n## Features\n- Add fuzzy matching to the search box (#41) (a1b2c3d)\n' > ~/work/notes-test/RELEASE_NOTES.md
lint ~/work/notes-test/RELEASE_NOTES.md
```

**Expected output:**

```
exit=0
```

A bullet without a commit hash fails, and a file with any other name is ignored:

```bash
printf '# Release notes: v1.1.0 (since v1.0.0)\n\n## Features\n- Add fuzzy matching to the search box (#41)\n' > ~/work/notes-test/RELEASE_NOTES.md
lint ~/work/notes-test/RELEASE_NOTES.md
echo x > ~/work/notes-test/other.txt
lint ~/work/notes-test/other.txt
```

**Expected output:**

```
RELNOTES-LINT: RELEASE_NOTES.md breaks the format:
- Line 4: a bullet must end with the short commit hash in parentheses, for example (a1b2c3d).
exit=2
exit=0
```

The script exits `2` on bad notes and `0` on good notes and other files. The script is fine. Next you fix how Claude Code finds it.

> **`python3: can't open file`?** The plugin is not at `~/plugins/relnotes`. Run Step 1's copy command again.
>
> **Every case prints `exit=0`, including the bad file?** The file path in the event does not exist. Check that the `printf` command ran and that you passed the full path to `lint`.

---

## Step 4: Fix the hook

**Your task:** edit `hooks/hooks.json` so that:

- the hook stays on `PostToolUse` with a matcher that matches `Write` and `Edit`
- the command locates the script with `${CLAUDE_PLUGIN_ROOT}`, with no path fixed to one machine
- the path it names is a file that exists in the plugin

Claude Code sets `${CLAUDE_PLUGIN_ROOT}` to the folder where the plugin is installed. A plugin can be installed anywhere, so a hook must never hard-code a path. Quote the variable in the command. `$CLAUDE_PLUGIN_ROOT` without braces is the same variable and also works.

```bash
nano ~/plugins/relnotes/hooks/hooks.json
```

Try it yourself first. If you get stuck, open the block below.

<details>
<summary>Show the fixed hooks.json</summary>

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/lint_notes.py\""
          }
        ]
      }
    ]
  }
}
```

**What changed:** the starter named `/home/student/plugins/relnotes/scripts/lint_notes.py`. That path does not exist on your machine, so the hook never ran. `${CLAUDE_PLUGIN_ROOT}/scripts/lint_notes.py` finds the script wherever the plugin is installed.

**The event and the path both matter.** A working script wired to `SessionStart`, or behind a matcher that does not match a write, never runs on a write. The path must name a file that is in the plugin: `${CLAUDE_PLUGIN_ROOT}/hooks/checkers/lint_notes.py` fails while the script sits in `scripts/`. You may write the path another way, such as `cd "${CLAUDE_PLUGIN_ROOT}" && python3 scripts/lint_notes.py`.

</details>

Check that the file is valid JSON:

```bash
python3 -m json.tool ~/plugins/relnotes/hooks/hooks.json > /dev/null && echo "valid JSON"
```

**Expected output:**

```
valid JSON
```

Run the linter again:

```bash
python3 $FILES/tools/plugin_lint.py ~/plugins/relnotes --marketplace $FILES/lab2-plugin/marketplace-template
```

**Expected output:** the two hook lines now pass, and the count drops from `6 FAIL` to `4 FAIL`.

```
[WARN] plugin.json still names the template author. Put the owner of the plugin in `author`, so a team can tell who to ask about it.
[ok  ] Manifest name is 'relnotes'
[ok  ] Hook commands use the plugin path variable and point at real files
[WARN] changelog-auditor.md: 'permissionMode' may be ignored in a plugin agent (unconfirmed). Do not rely on it for a control.
[FAIL] changelog-auditor.md: a checking agent has write-capable tools: Bash, Edit, Write
[WARN] release-notes.md: description is only 20 characters. A vague description can stop the command from being chosen.
[FAIL] release-notes.md: still contains a TODO line of its own. Naming TODO as text the format hook rejects is fine; leaving 'TODO: write ...' is not.
[WARN] A CLAUDE.md at the plugin root is not loaded as project context (claude plugin validate says so too). Put rules that must apply into a command or skill, where you can test them with an eval.
[ok  ] Every eval case has at least one grader (6 cases)
[WARN] marketplace.json still names the template owner. Put your team in `owner`.
[FAIL] No marketplace entry named 'relnotes' (entries: ['release-notes']). Entry name and manifest name must match.
[FAIL] Entry 'release-notes': source path ./plugins/relnotes does not exist under the marketplace

4 FAIL, 5 WARN. Now run: claude plugin validate /home/<you>/plugins/relnotes
```

> **`Hook command does not use ${CLAUDE_PLUGIN_ROOT}` still shows?** The old path is still in the file. Open it again and check that `/home/student/...` is gone.
>
> **`Hook points at <path>, which does not exist in the plugin`?** The script path is wrong. The script is `scripts/lint_notes.py`. Both the linter and the scorer read the path you wrote, not the file name.
>
> **`Expecting ',' delimiter` from `json.tool`?** It prints the line and column. Common causes: a missing comma, a trailing comma after the last item, or a missing closing brace.

---

## Step 5: Write the command, tighten the agent, fix the manifest

Three files need work. Read the six eval prompts from Step 2 again. They tell you what the command must do.

**Your task, part 1: the command.** Edit `commands/release-notes.md` so that it:

- has a specific `description` that says what the command does and when to use it
- **names the git command** that works out the commit range and reads the log, such as `git log --no-merges <from>..<to>`. Do not write "read the git log"
- groups entries into the four sections **in the order the format checker enforces**: Breaking changes, Features, Fixes, Other changes
- ends every bullet with the short commit hash in parentheses
- hands the draft and the log text to the `changelog-auditor` agent before finishing
- never invents an entry
- changes nothing except `RELEASE_NOTES.md`

```bash
nano ~/plugins/relnotes/commands/release-notes.md
```

<details>
<summary>Show the finished command</summary>

Replace the whole file with:

````markdown
---
description: Draft RELEASE_NOTES.md from the git log between two refs, grouped by change type. Use when asked for release notes or a changelog for a range of commits.
---

Write release notes for a range of commits and save them as `RELEASE_NOTES.md` in the repository root.

1. Pick the range. If the user names a starting tag or ref, use it. Otherwise use the latest tag (`git describe --tags --abbrev=0`). The end is the ref the user names, or HEAD.
2. Read the log for the range, including message bodies: `git log --no-merges --format='%h %s%n%b%n--' <from>..<to>`.
3. Sort each commit into exactly one section:
   - Breaking changes: a type marked with `!` (for example `feat(api)!:`) or a `BREAKING CHANGE:` footer
   - Features: `feat`
   - Fixes: `fix`
   - Other changes: everything else (`docs`, `chore`, `perf`, `refactor`, and so on)
4. Write the file in this exact shape, with sections in this order, and leave out a section that has no entries:

```
# Release notes: <to> (since <from>)

## Breaking changes
- Plain-language description (#PR) (a1b2c3d)

## Features
- ...
```

   Every bullet is one sentence of plain language, then the pull request number if the subject has one, then the short commit hash in parentheses, at the end of the line.
5. Before you tell the user the notes are done, run the `changelog-auditor` agent. Give it the log text from step 2 and the path of the draft. Fix every problem it reports, then run it again if you changed anything.
6. Never invent an entry. If the user asks for a line about something the log does not contain, leave it out and say so in your reply.
7. Change nothing except `RELEASE_NOTES.md`. Do not tag, commit or push.
````

**Why it is written this way:**

- The evals are the specification. `groups-by-type` needs sections and hashes. `flags-breaking-change` needs the breaking change first. `no-invented-entries` needs step 6. `uses-auditor` needs step 5.
- Rules that must apply belong in the command. A `CLAUDE.md` at the plugin root is not loaded, so an eval cannot rely on it.
- The description is what Claude reads to decide whether to use the command. A vague description can stop it from being chosen, so shortening it later can break the `groups-by-type` case.
- The agent has no shell, so the command gives it the log text.

</details>

**Your task, part 2: the agent.** Edit `agents/changelog-auditor.md` so it has only read tools. Either list only read tools in `tools:` or deny every write tool with `disallowedTools:`. Remove the `permissionMode` line, which a plugin agent may ignore.

```bash
nano ~/plugins/relnotes/agents/changelog-auditor.md
```

<details>
<summary>Show the read-only agent</summary>

Replace the whole file with:

```markdown
---
name: changelog-auditor
description: Checks a drafted RELEASE_NOTES.md against the git log. Use after release notes are drafted, to find missing commits, invented entries and unflagged breaking changes.
model: sonnet
tools: Read, Grep, Glob
---

You audit a release notes draft. The caller gives you the git log text for the range and the path of the draft. You have no shell, so work only from what you were given and from the draft file.

Compare them. Report, as a short list:

- commits in the log that are missing from the draft
- draft entries that no commit supports
- breaking changes (a `!` after the type, or a `BREAKING CHANGE:` footer) that are not under "Breaking changes"

Fix nothing yourself. Reply with the list, or the single line "No problems found."
```

**Why:** an agent that checks a file must not be able to change it. `tools: Read, Grep, Glob` gives it read access only. Because it has no shell, the command passes it the git log text in step 5.

</details>

**Your task, part 3: the manifest and `CLAUDE.md`.** In `.claude-plugin/plugin.json`, change `"name": "Your Name"` under `author` to your team's name. Then delete `CLAUDE.md`. Its rules now live in the command:

```bash
nano ~/plugins/relnotes/.claude-plugin/plugin.json
rm ~/plugins/relnotes/CLAUDE.md
```

Prefer to have Claude do all three? Start Claude Code in the plugin folder with `cd ~/plugins/relnotes && claude`. At the trust question press **Down**, then **Enter**. Type the prompt below. When Claude finishes, type `/exit`.

<details>
<summary>Show a prompt you can give Claude</summary>

```
This is a half-built Claude Code plugin called relnotes. Read evals/ first (all six cases are the spec), then: write commands/release-notes.md with a specific description that names the git log --no-merges <from>..<to> invocation, groups entries into the four sections in the order the checker enforces, ends each bullet with a short hash, passes the draft and log to the changelog-auditor agent, never invents entries, and changes only RELEASE_NOTES.md. Make agents/changelog-auditor.md read-only and remove its TODO and permissionMode. Set the plugin.json author to my team name. Delete CLAUDE.md. Then run python3 $FILES/tools/plugin_lint.py . and report.
```

Either way, run the check below yourself. Claude's own report is not your evidence.

</details>

Run the linter:

```bash
python3 $FILES/tools/plugin_lint.py ~/plugins/relnotes --marketplace $FILES/lab2-plugin/marketplace-template
```

**Expected output:** every plugin line passes. Only the marketplace lines are left, and you fix those in Step 7.

```
[ok  ] Manifest name is 'relnotes'
[ok  ] Hook commands use the plugin path variable and point at real files
[ok  ] Every eval case has at least one grader (6 cases)
[WARN] marketplace.json still names the template owner. Put your team in `owner`.
[FAIL] No marketplace entry named 'relnotes' (entries: ['release-notes']). Entry name and manifest name must match.
[FAIL] Entry 'release-notes': source path ./plugins/relnotes does not exist under the marketplace

2 FAIL, 1 WARN. Now run: claude plugin validate /home/<you>/plugins/relnotes
```

> **`still contains a TODO line of its own`?** The command file still has the starter's `TODO: write the command body` line. Naming TODO as text the format hook rejects is fine. Leaving the starter line is not.
>
> **`a checking agent has write-capable tools`?** The agent file lists `Bash`, `Edit` or `Write`, or has no `tools:` line. Set `tools: Read, Grep, Glob`.
>
> **`description is only N characters`?** The command's `description:` line is too short. Say what it does and when to use it.
>
> **A `permissionMode` warning?** The agent file still has a `permissionMode:` line. A plugin agent may ignore it, so delete the line.
>
> **The `CLAUDE.md` warning is still there?** The file is still in the plugin root. Delete it with `rm ~/plugins/relnotes/CLAUDE.md`.

---

## Step 6: Try the command

Test the command yourself before you package it. The evals build a small git repository with a tag, a breaking change and a mix of commit types. Build the same one:

```bash
mkdir -p ~/work/relnotes-demo && cd ~/work/relnotes-demo && bash ~/plugins/relnotes/evals/groups-by-type/scaffold.sh && git log --oneline
```

**Expected output:** six commits, newest first. The hashes on your machine differ. The labels in parentheses are shown on a terminal.

```
9bcbb77 (HEAD -> main) perf(report): cache the monthly rollup (#46)
8b816ea docs: update the install guide (#45)
2f45627 feat(api)!: drop the legacy /v1/token endpoint (#44)
3125d45 fix(login): stop the session timer resetting on refresh (#43)
c150d37 feat(search): add fuzzy matching to the search box (#41)
3d12638 (tag: v1.0.0) chore: initial import
```

The commit `feat(api)!` is a breaking change. The tag `v1.0.0` marks the first commit. Start Claude Code with your plugin loaded for this one session:

```bash
claude --plugin-dir ~/plugins/relnotes
```

At the trust question press **Down**, then **Enter**. The bottom of the screen shows `auto mode on`. Leave it. Type:

```
/relnotes:release-notes v1.0.0
```

**Expected result:** Claude reads the log, writes `RELEASE_NOTES.md`, runs the `changelog-auditor` agent, and tells you the notes are done. The notes have the sections `Breaking changes`, `Features`, `Fixes` and `Other changes`, in that order. Every bullet ends with a short commit hash, and the breaking change names `/v1/token`. When Claude writes the file, your hook runs. If the format is wrong, Claude sees the `RELNOTES-LINT` message and rewrites the file.

Type `/exit`, then read the file:

```bash
cat RELEASE_NOTES.md
```

> **`/relnotes:release-notes` is not found?** The plugin did not load. Start with `claude --plugin-dir ~/plugins/relnotes` from any folder, and check that `.claude-plugin/plugin.json` exists in the plugin. After an install, run `/reload-plugins`.
>
> **Claude wrote the notes without calling the auditor?** The command's step 5 is missing or vague. The `uses-auditor` eval tests this.
>
> **A bullet has no hash, or a section is out of order?** Read the `RELNOTES-LINT` message in the Claude session. It says which line breaks which rule. Fix the command's output template in `release-notes.md`.

---

## Step 7: Package the plugin in a marketplace

A **marketplace** is a folder with a catalog file that lists plugins. Anyone who adds the marketplace can install the plugin.

Start from the template. Copy it, create its `plugins` folder, and copy your plugin into it:

```bash
cp -r $FILES/lab2-plugin/marketplace-template ~/marketplace
mkdir -p ~/marketplace/plugins && cp -r ~/plugins/relnotes ~/marketplace/plugins/relnotes
```

**Your task:** edit `~/marketplace/.claude-plugin/marketplace.json` so that:

- the plugin entry's `name` matches the manifest name, `relnotes`
- the entry's `source` path points at the plugin folder you copied
- `owner` names your team

```bash
nano ~/marketplace/.claude-plugin/marketplace.json
```

<details>
<summary>Show the fixed marketplace.json</summary>

```json
{
  "name": "team-tools",
  "description": "Developer tools for a git-based workflow",
  "owner": {
    "name": "ROI Training class example"
  },
  "plugins": [
    {
      "name": "relnotes",
      "source": "./plugins/relnotes",
      "description": "Draft and check release notes from the git log"
    }
  ]
}
```

Use your own team name for `owner`. Any name except `Your Name` passes the check. The template entry was called `release-notes`, but the plugin's manifest name is `relnotes`. The two must match.

</details>

Run the linter with the real marketplace, then validate both folders:

```bash
python3 $FILES/tools/plugin_lint.py ~/plugins/relnotes --marketplace ~/marketplace
claude plugin validate ~/plugins/relnotes
claude plugin validate ~/marketplace
```

**Expected output** from the linter:

```
[ok  ] Manifest name is 'relnotes'
[ok  ] Hook commands use the plugin path variable and point at real files
[ok  ] Every eval case has at least one grader (6 cases)
[ok  ] Marketplace entry name matches the manifest name

0 FAIL, 0 WARN. Now run: claude plugin validate /home/<you>/plugins/relnotes
```

For `validate`, read the first half of each output. It must not print `Found N errors`. Then add the marketplace and confirm Claude Code sees it:

```bash
claude plugin marketplace add ~/marketplace
claude plugin marketplace list
```

**Expected output:** `validate` ends with `Validation passed`. The `add` command prints a success line, and the list shows `team-tools` with your folder as its source. You remove it in Cleanup.

```
✔ Successfully added marketplace: team-tools (declared in user settings)
    Source: Folder (/home/<you>/marketplace)

Configured marketplaces:

  ❯ anthropic-plugin-directory
    Source: Built in (Anthropic Directory)

  ❯ claude-plugins-official
    Source: GitHub (anthropics/claude-plugins-official)

  ❯ team-tools
    Source: Folder (/home/<you>/marketplace)
```

The other two marketplaces are already configured on class machines.

Run the scorer. It checks the files and has no evidence yet:

```bash
python3 $FILES/lab2-plugin/score_lab2.py ~/plugins/relnotes --marketplace ~/marketplace
```

**Expected output:** 80 of 100. The 20 points that are missing are the three evidence rows.

```
LAB 2 SCORE (local checks)
[PASS]  5/5  Manifest has a kebab-case name
[PASS]  5/5  hooks/hooks.json defines a command hook that runs after a write
[PASS]  8/8  Hook command uses $CLAUDE_PLUGIN_ROOT and no path fixed to one machine
[PASS]  7/7  The after-a-write hook points at a script that exists inside the plugin
         ..  hook behavior tested with scripts/lint_notes.py, from the PostToolUse Write|Edit hook
[PASS]  7/7  Bad notes: the hook exits 2 with a message on stderr
[PASS]  5/5  Good notes: the hook exits 0
[PASS]  3/3  Other files are ignored: exit 0
         ..  command graded: commands/release-notes.md
[PASS]  3/3  Command has no leftover TODO
[PASS]  3/3  Command description is specific (40+ characters)
[PASS]  3/3  Command names RELEASE_NOTES.md and the changelog-auditor agent
[PASS]  3/3  Command says how to work out the commit range and read the git log
[PASS]  2/2  Command names all four sections
[PASS]  2/2  The four sections are in the order the format checker enforces
[PASS]  2/2  Command forbids inventing entries
[PASS]  2/2  Command limits changes to RELEASE_NOTES.md
         ..  agent graded: agents/changelog-auditor.md
[PASS] 10/10 The checking agent has read-only tools
[PASS] 10/10 Marketplace entry matches the manifest and its source holds the graded plugin
[FAIL]  0/8  Evidence: validate output pasted and it reports success  -> ...
[FAIL]  0/6  Evidence: plugin details output with the projected token cost pasted  -> ...
[FAIL]  0/6  Evidence: eval run summary pasted, with the case results and the run settings  -> ...

TOTAL: 80 / 100
```

The hint text after each arrow is longer than shown.

> **`Marketplace entry matches the manifest and its source holds the graded plugin` fails?** Two usual causes. The entry name is not `relnotes`, or the copy inside `~/marketplace/plugins/relnotes` is old. The scorer checks that the plugin under `source` is the same plugin it graded. **Copy your plugin over again after every change:** `rm -rf ~/marketplace/plugins/relnotes && cp -r ~/plugins/relnotes ~/marketplace/plugins/relnotes`.
>
> **`claude plugin marketplace add` says it cannot find the plugin?** The entry `name` does not match the manifest name, or `source` points at the wrong folder.

---

## Step 8: Run the evals

`claude plugin validate` checks files. It does not test behavior. `claude plugin eval` runs the six cases in `evals/`. Each case gives Claude a prompt in a clean workspace and grades the result. This step uses model requests on your seat, so you set a cost cap.

First check the sandbox:

```bash
bash $FILES/setup/classroom-sandbox.sh --check
```

**Expected output:**

```
  AppArmor profile bwrap-userns-restrict : clear
  kernel.apparmor_restrict_unprivileged_userns : 0
[ OK ] Nothing is blocking the sandbox - both controls are clear.
       Confirm it for real inside a session: ask Claude to run 'touch ~/sandbox-probe'.
       It should fail with 'Read-only file system'. If it succeeds, you are NOT sandboxed.
       Nothing to switch on. Leave the machine as it is: run --off only if YOU ran --on.
```

If it says `[ OK ]`, continue to the eval. If it says the sandbox is blocked, the evals fail at random: a different one or two of six cases each run, each with `RELEASE_NOTES.md does not exist`, because every shell command inside the run is refused. Read the `--on` note in Lab 3 Step 1 before you change anything. `--on` is machine-wide.

Run the eval with a cap of two dollars. Run it once. The `tee` part saves the output to a file as well as showing it on screen. You use that file in Step 9:

```bash
claude plugin eval ~/plugins/relnotes --runs 1 --ablation none --max-cost-usd 2 --allow-tools Write Bash --scaffold --trust-plugin --no-publish 2>&1 | tee ~/eval-output.txt
```

It takes one to two minutes. Each flag has a reason:

| Flag | Why |
|---|---|
| `--runs 1` | One run per case keeps the cost small |
| `--ablation none` | Skips the baseline run without your plugin |
| `--max-cost-usd 2` | The cost cap. Choose your own |
| `--allow-tools Write Bash` | `Write` and `Bash` are gated at the runner on top of each case's own list. Without this the cases cannot create `RELEASE_NOTES.md` and every grader that reads it fails. `hook-lints-bad-notes` scores 1.00 with it and 0.00 without |
| `--scaffold` | Four of the six cases build a git repository to read. Without this they run in an empty workspace and score about 0.33 |
| `--trust-plugin` | A non-interactive run otherwise stops to ask you to trust the folder |
| `--no-publish` | `plugin eval` publishes its HTML report to claude.ai by default. This keeps the report on your machine |

**Expected output:** a result line for each case, then a summary table.

```
CASE                   SCORE  PASS%  RUNS  COST   NOTES
flags-breaking-change  1.00   100%   1     $0.14
groups-by-type         1.00   100%   1     $0.13
hook-lints-bad-notes   1.00   100%   1     $0.09
ignores-unrelated      1.00   100%   1     $0.07
no-invented-entries    1.00   100%   1     $0.14
uses-auditor           1.00   100%   1     $0.14

6 case(s) · 93s · $0.71
Report: /home/<you>/plugins/relnotes/evals/results/<timestamp>/report.html
```

Your time and costs differ. A score below 1.00 on a case is a result to report. Read the case's grader and your command, and decide what to change.

> **Every case fails, or several score about 0.33?** Check you passed `--allow-tools Write Bash --scaffold`. Without `--scaffold` the cases that read a git log run in an empty workspace. Without the tool grant they cannot write the file. Both look exactly like a broken plugin. Then check that Git is 2.31 or later and that you are signed in. Rerun one case first with `--case groups-by-type`.
>
> **`groups-by-type` fails and the command is not chosen?** The command's description is too vague, or it does not say when to use it. Shortening a description can stop a command from being chosen, so rerun the cases after you edit one.
>
> **`hook-lints-bad-notes` fails?** That case checks that Claude sees the hook's message. Check that `hooks.json` is on `PostToolUse` with `Write|Edit`, and that the path names `scripts/lint_notes.py`.
>
> **The suite is too slow or too costly?** Lower `--runs`, keep `--ablation none`, and lower `--max-cost-usd`.

---

## Step 9: Collect the evidence and score

The scorer reads one file, `EVIDENCE.md`, that holds three command lines and the real output under each. Build it from the commands themselves. Each command line goes in first, and the output goes after it.

```bash
echo '$ claude plugin validate ~/plugins/relnotes' > ~/EVIDENCE.md && claude plugin validate ~/plugins/relnotes >> ~/EVIDENCE.md 2>&1
```

```bash
echo '$ claude --plugin-dir ~/plugins/relnotes plugin details relnotes' >> ~/EVIDENCE.md && claude --plugin-dir ~/plugins/relnotes plugin details relnotes >> ~/EVIDENCE.md 2>&1
```

For the third block, add the eval command line, then the output you saved in Step 8. This does not run the eval again:

```bash
echo '$ claude plugin eval ~/plugins/relnotes --runs 1 --ablation none --max-cost-usd 2 --allow-tools Write Bash --scaffold --trust-plugin --no-publish' >> ~/EVIDENCE.md && cat ~/eval-output.txt >> ~/EVIDENCE.md
```

Look at the middle block. The `details` output has a token cost section:

```bash
grep -n -A4 'Projected token cost' ~/EVIDENCE.md
```

**Expected output:** a block like this, with a different number for your plugin. Other lines are omitted.

```
Projected token cost
  Always-on:  ~210 tok   added to every session
  ...
  Token counts are estimates and may differ from actual usage.
```

The always-on figure is the cost of having this plugin installed. The command and agent descriptions are in the context window on every turn. Hooks and servers are not counted there.

Run the scorer with your evidence:

```bash
python3 $FILES/lab2-plugin/score_lab2.py ~/plugins/relnotes --marketplace ~/marketplace --evidence ~/EVIDENCE.md
```

**Expected output:** the three evidence rows now score, and the total is 100.

```
[PASS]  8/8  Evidence: validate output pasted and it reports success
[PASS]  6/6  Evidence: plugin details output with the projected token cost pasted
[PASS]  6/6  Evidence: eval run summary pasted, with the case results and the run settings

TOTAL: 100 / 100
The 20 evidence points are a plausibility check on pasted text, not proof. The facilitator confirms the eval run from a screen or a result file.
```

**Checkpoint:** the scorer reports at least 80 **and all three evidence rows score**. The hook exits 2 on bad notes and 0 on good notes. The plugin validates. The file work in Steps 1 to 7 tops out at 80 of the 100, so a run with no evidence can meet the number without Steps 8 and 9. The evidence rows are what those steps pay for.

> **An evidence row scores 0 on output you did paste?** Each row reads only the block under its own `claude plugin ...` line. There is no fallback to the rest of the file. A summary sentence with no command line above it scores zero, and so does a block that says the command was not run. A case that failed is fine to report. A suite that never ran is not.
>
> **The validate row fails?** The first half of the `validate` output must not say `Found N errors`. Fix the plugin and rebuild the file. The second half, `Plugin directory checks`, does not count.
>
> **The details row fails?** The block needs the always-on token figure as a number. Rebuild the file with the second command above.
>
> **The eval row fails?** The block needs the case results and the run settings: `--runs`, `--max-cost-usd`, or the report path.

---

## What you built

In 75 minutes, you:

- Fixed a plugin hook so it finds its script wherever the plugin is installed
- Wrote a command that drafts release notes in the format the checker enforces
- Made the checking agent read-only
- Packaged the plugin in a marketplace and checked it with `validate` and the linter
- Tested the behavior with six eval cases and a cost cap, and saved the evidence

The difference to remember: `validate` checks that the files are well formed. The evals check that the plugin does its job.

## How the score is made

| Item | Points |
|---|---|
| Manifest with a kebab-case name | 5 |
| `hooks.json` defines a hook that runs after a write (`PostToolUse`, matching `Write`/`Edit`), uses `${CLAUDE_PLUGIN_ROOT}`, and points at a script that is in the plugin | 20 |
| Hook behavior: exit 2 on bad notes, 0 on good notes, ignores other files | 15 |
| Command (`commands/release-notes.md`): no leftover TODO, specific description, names the file and the agent, names the git command that works out the commit range and reads the log, names the four sections and puts them in order, never invents and changes nothing else | 20 |
| Checking agent has read-only tools | 10 |
| Marketplace entry matches the manifest and its source holds the plugin | 10 |
| Evidence: validate output, token cost, eval summary | 20 |

The scorer grades `commands/release-notes.md` and the agent whose `name` is `changelog-auditor`. Other files in `commands/` and `agents/` are not graded, so a scratch file cannot earn the points for a component you have not written. The 20 evidence points check the pasted text and cannot prove the commands ran. Your facilitator confirms the eval run from a screen or a result file.

## Cleanup

Remove the marketplace from Claude Code, and the test files you made:

```bash
claude plugin marketplace remove team-tools
rm -rf ~/work/notes-test ~/work/relnotes-demo
```

Keep `~/plugins/relnotes`, `~/marketplace` and `~/EVIDENCE.md` until your facilitator has seen them.
