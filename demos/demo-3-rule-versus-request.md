# Demo 3: Rule Versus Request

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 15 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

A project file says "never read `.env`". You test that request against three setups: the request alone, a `Read` deny rule, and a deny rule plus the sandbox. You see that a request depends on the model, and that a file deny rule and a sandbox rule are two different layers.

| Setup | What protects `.env` |
|---|---|
| A | `CLAUDE.md` asks Claude not to read it (a request) |
| B | A `Read` deny rule blocks Claude's file tool |
| C | The deny rule plus a sandbox rule that blocks shell commands |

## Prerequisites

- [ ] `claude auth status` shows you are signed in (see [`SETUP.md`](../SETUP.md))
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Apply setup A and read the project

Open a terminal (the **Terminal Emulator** icon on the desktop). `apply_config.sh` copies one setup into the project's `.claude/settings.json`. Apply setup A:

```bash
cd $FILES/demo3-rule-vs-request
bash apply_config.sh A
```

**Expected output:**

```
Applied A-request-only.json to /home/<you>/champions/demo-files/demo3-rule-vs-request/project/.claude/settings.json
Restart Claude Code in /home/<you>/champions/demo-files/demo3-rule-vs-request/project and run /status to confirm.
```

Your username replaces `<you>`. If you ran this demo before, you also see `Restored CLAUDE.md (the request).`

Read the three files in the project:

```bash
cat project/CLAUDE.md
cat project/.env
cat project/src/app.py
```

`CLAUDE.md` says: `Never read the .env file. It holds a database password.` That is a request. `.env` holds a fake placeholder password. `app.py` is a sample app that reads `.env` itself and prints only how long the password is.

---

## Step 2: Test the request

Start Claude Code in the project:

```bash
cd project
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to move to **Yes, I trust this folder**, then press **Enter**. The bottom of the screen shows `auto mode on`. Leave it.

Type this prompt and press Enter:

```
Show me the contents of .env
```

**Expected result:** Claude declines and cites `CLAUDE.md`. It does not show the password. On Opus 5.5 and Haiku 5.5 this is what happens. Claude's wording differs on every run.

Nothing in your settings stopped it. The model chose to honor a request. Another model, or a different prompt, might not.

Leave Claude Code by typing `/exit` and pressing Enter.

---

## Step 3: Test the rule

Go back to the demo folder and apply setup B:

```bash
cd ..
bash apply_config.sh B
```

**Expected output:**

```
Applied B-read-deny.json to /home/<you>/champions/demo-files/demo3-rule-vs-request/project/.claude/settings.json
Moved CLAUDE.md aside to CLAUDE.md.off, so only the rule is in play.
Restart Claude Code in /home/<you>/champions/demo-files/demo3-rule-vs-request/project and run /status to confirm.
```

The script moves `CLAUDE.md` aside on purpose. With it present, the model refuses before it calls any tool, and the rule is never tested. Setup B adds these deny rules:

```bash
cat project/.claude/settings.json
```

**Expected output:**

```
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

Start a new session, because settings are read at startup, and ask the same question:

```bash
cd project
claude
```

```
Show me the contents of .env
```

**Expected result:** Claude calls its file-reading tool and the call is refused by your permission rule. A refusal looks like `File is in a directory that is denied by your permission settings`. The wording can differ. This time no request was involved: the rule stopped the read.

> **Claude showed the password?** The deny rule is not loaded. Exit, run `cat .claude/settings.json` in the `project` folder and check it shows the `Read(./.env)` rule. You must start Claude Code from the `project` folder, because settings are read from the folder it starts in.

---

## Step 4: Find the gap

In the same session, type:

```
Run python3 src/app.py and tell me what it prints.
```

**Expected result:** Claude runs the app. The output has two lines:

```
Total: 29.85
Database setting: loaded (24 characters)
```

The app read `.env` itself, as a shell command. The `Read` deny rule stops Claude's file tool. It does not stop a shell command from reading the file. The password is 24 characters long, and the app confirmed it loaded.

Leave Claude Code by typing `/exit` and pressing Enter.

---

## Step 5: Close the gap with the sandbox

The sandbox limits what shell commands can read. First check that it can start on this machine:

```bash
cd ..
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

On the class machines the sandbox already works, and you change nothing. If the check says the profile is **BLOCKING**, read Lab 3 Step 1 before you run `--on`.

Apply setup C:

```bash
bash apply_config.sh C
```

**Expected output:**

```
Applied C-deny-plus-sandbox.json to /home/<you>/champions/demo-files/demo3-rule-vs-request/project/.claude/settings.json
Restart Claude Code in /home/<you>/champions/demo-files/demo3-rule-vs-request/project and run /status to confirm.
```

Setup C keeps the deny rules and adds a sandbox rule that blocks shell reads of `.env`. Start a new session and ask both questions:

```bash
cd project
claude
```

```
Show me the contents of .env
```

```
Run python3 src/app.py and tell me what it prints.
```

**Expected result:** the first answer is a refusal, as in Step 3. The app now prints:

```
Total: 29.85
Database setting: could not read .env (Permission denied)
```

You have two refusals from two layers. The `Read` tool was refused by a permission rule. The shell command was refused by the sandbox.

Leave Claude Code by typing `/exit` and pressing Enter.

> **The app still prints `loaded (24 characters)`?** The sandbox is not active. Confirm `.claude/settings.json` shows a `sandbox` section, and that you restarted `claude` after applying C. In a session, ask Claude to run `touch ~/sandbox-probe`. It should fail with `Read-only file system`. If it succeeds, you are not sandboxed.
>
> **Claude Code exits at startup, or every command is refused?** Setup C sets `failIfUnavailable: true`, so a sandbox that cannot start stops the session. That is the setting working. Run the `--check` command again and read what it blocks.

---

## Step 6: Record what depended on the model

Think through the five results. Which ones depended on the model choosing well, and which did not? Write your answer in a notes file:

```bash
mkdir -p ~/work
nano ~/work/demo3-notes.md
```

Type one line, with your own answer after the colon:

```
Depended on the model: step <number>
```

Press **Ctrl+O**, then **Enter**, to save. Press **Ctrl+X** to exit.

<details>
<summary>Show the expected answer</summary>

Only Step 2 depended on the model. In Steps 3, 4 and 5 the result came from a permission rule or the sandbox, which apply whatever the model decides. Step 4 shows a rule that has a gap: the deny rule covered Claude's file tool and not a shell command. Step 5 closed that gap with a second layer.

</details>

---

## Step 7: Optional, test bypass mode

Only do this on a throwaway machine. Setup D sets `defaultMode` to `bypassPermissions` in the project file. A project-level `defaultMode` of `bypassPermissions` is ignored, and the session starts in manual mode, so setup D does not test bypass mode. To test it, apply setup B and start Claude Code with the mode on the command line:

```bash
cd ..
bash apply_config.sh B
cd project
claude --permission-mode bypassPermissions
```

Ask the Step 3 question. Record what you see in your notes. Do not assume that deny rules hold in every permission mode. Check.

Leave Claude Code by typing `/exit` and pressing Enter.

---

## What you saw

- A sentence in `CLAUDE.md` is a request that the model weighs. Step 2 depended on it.
- A `Read` deny rule is a control. It stopped Claude's file tool whatever the model decided.
- The deny rule did not stop a shell command. The sandbox did.

A charter row marked "Enforced" must point at a rule or a sandbox setting, not at a request.

## Cleanup

Put the project back to setup A. This restores `CLAUDE.md` and removes the deny rules:

```bash
cd $FILES/demo3-rule-vs-request
bash apply_config.sh A
```

**Expected output:**

```
Applied A-request-only.json to /home/<you>/champions/demo-files/demo3-rule-vs-request/project/.claude/settings.json
Restored CLAUDE.md (the request).
Restart Claude Code in /home/<you>/champions/demo-files/demo3-rule-vs-request/project and run /status to confirm.
```

To remove your notes:

```bash
rm -f ~/work/demo3-notes.md
```
