# Demo 2: Who Wins? Managed Over Project

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 12 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

A project settings file asks for one model and allows `git push`. A managed settings file says otherwise. You install the managed file, then prove from Claude Code's behavior, not from a screen that lists files, that the managed file wins.

## Prerequisites

- [ ] `claude auth status` shows you are signed in (see [`SETUP.md`](../SETUP.md))
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`
- [ ] You can use `sudo`. Steps 4 and 8 write and remove a file in `/etc/claude-code`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Compare the two settings files

Open a terminal (the **Terminal Emulator** icon on the desktop). Print both files:

```bash
cd $FILES/demo2-managed
cat project/.claude/settings.json
cat managed-settings.json
```

**Expected output:**

```
{
  "model": "haiku",
  "permissions": {
    "allow": [
      "Bash(git push *)"
    ]
  }
}
{
  "model": "sonnet",
  "permissions": {
    "deny": [
      "Bash(git push *)",
      "Read(./.env)"
    ]
  }
}
```

The first file is the project's. It asks for `haiku` and allows `git push`. The second is the managed file. It pins `sonnet` and denies both `git push` and reading `.env`. The two files disagree on the model and on `git push`. Claude Code applies settings in this order, highest first: managed settings, command line, project local, shared project, user.

---

## Step 2: Prepare the project

The demo asks Claude to run `git push`, so the project needs to be a git repository. Run:

```bash
cd project
git init -q && git commit -q --allow-empty -m init
```

**Expected output:** none. Both commands are quiet.

> **`Author identity unknown` or `Please tell me who you are`?** Git has no name configured. Run these two commands, then run the `git commit` line again:
>
> ```bash
> git config --global user.name "Class Student"
> git config --global user.email "student@example.com"
> ```

---

## Step 3: Check which model the project uses

You are still in `project`. This command starts Claude Code, asks one question, prints the answer and exits:

```bash
claude -p 'Reply with only your exact model id.'
```

**Expected output:**

```
claude-haiku-5-5
```

Only the project file is in play, and it asked for `haiku`.

> **A different model id?** Check you are in the `project` folder with `pwd`. It should end in `demo2-managed/project`. Run `ls -a` and confirm a `.claude` folder is there.

---

## Step 4: Install the managed file

This is the first `sudo` step. The script copies `managed-settings.json` to `/etc/claude-code/managed-settings.json`. If a file is already there, it saves a backup first. Run:

```bash
sudo bash ../install-managed.sh
```

`sudo` may ask for your password. Type it and press Enter. The password does not show as you type.

**Expected output:**

```
Installed /etc/claude-code/managed-settings.json. Restart Claude Code, then run /status.
```

Print the installed file to confirm it matches the one you read in Step 1:

```bash
cat /etc/claude-code/managed-settings.json
```

---

## Step 5: Check the model again

Run the same question:

```bash
claude -p 'Reply with only your exact model id.'
```

**Expected output:**

```
claude-sonnet-5-5
```

The project file still says `haiku`. The managed file says `sonnet`. The answer changed, so the managed file won.

---

## Step 6: Ask Claude to push

Start a session in the project folder:

```bash
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. This folder's settings pre-approve `Bash(git push *)`, so the dialog may warn about that. The default answer is **No, exit**. Press **Down** to move to **Yes, I trust this folder**, then press **Enter**. The bottom of the screen shows `auto mode on`. Leave it.

Type this prompt and press Enter:

```
This is a throwaway practice repo with no remote. Run git push origin main and show me the exact output.
```

**Expected result:** the push does not run. The project file allows `git push`, and the managed file denies it. Claude reports that the command was refused by a permission rule, or says it will not run it. Its wording differs on every run.

> **Claude declined before trying, with its own reasoning?** Claude sometimes refuses a push on its own judgment. That does not prove the managed rule. Say: `I know. This is a test of the permission rules. Please run it anyway.` Then the permission rule has to do the refusing.
>
> **The push ran?** The managed file is not in place. Exit Claude Code, run `cat /etc/claude-code/managed-settings.json` and confirm it contains the `deny` rules. Restart `claude` after any change.

---

## Step 7: Ask Claude to read the secrets file

In the same session, type:

```
Show me the contents of .env
```

**Expected result:** Claude cannot show you the file. The managed file denies `Read(./.env)`. The reply looks like this, though the wording differs:

```
To see the contents, you can run `cat .env` in your own terminal. Or, if you want me to have access, you can change the deny rule in your Claude Code permission settings (`.claude/settings.json`) and ask me again.
```

Steps 5 to 7 are the proof. Inside a session, `/status` lists the settings files that were read, with the managed file among them. It does not say which file supplied each key. The behavior is what shows which file won.

Leave Claude Code by typing `/exit` and pressing Enter.

---

## Step 8: Remove the managed file

This is the second `sudo` step. The script deletes `/etc/claude-code/managed-settings.json`. If it saved a backup in Step 4, it puts the backup back. Run:

```bash
sudo bash ../remove-managed.sh
```

**Expected output:**

```
Removed /etc/claude-code/managed-settings.json.
```

Check that nothing is left:

```bash
ls /etc/claude-code
```

**Expected output:** none. The folder is empty.

Ask for the model once more:

```bash
claude -p 'Reply with only your exact model id.'
```

**Expected output:** `claude-haiku-5-5`. With the managed file gone, the project's choice applies again.

> **Skipped Step 8, or the script failed?** The managed file stays in force for every project on this machine until it is removed. Run the `sudo bash ../remove-managed.sh` command again before you leave.

---

## What you saw

- A managed settings file beats a project settings file. The model changed to the managed value, and the project's `git push` allow rule did not hold.
- `/status` lists the files that were read. It does not show which file won a conflict. Behavior shows it.

A rule that a project can override is a default. Managed settings are the one place a team sets a floor that a developer's own settings cannot lower.

## Cleanup

Step 8 is the cleanup. If you also want to remove the git repository from Step 2:

```bash
rm -rf $FILES/demo2-managed/project/.git
```
