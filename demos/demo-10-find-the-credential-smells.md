# Demo 10: Find the Credential Smells

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 10 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

You read a small project, name the credential smells in it, run a scanner, and say what the scanner cannot see. A **credential smell** is a pattern that points to a credential problem: a key written into a file, a key with no expiry, a secret nobody owns.

The project is fictional. Every value in it is a placeholder, such as `FAKE-TOKEN-DO-NOT-USE`. Nothing in it connects to a real service.

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md): `claude --version` prints a version and `claude auth status` shows you are signed in
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Read the project's files

Open a terminal (the **Terminal Emulator** icon on the desktop). Go to the project and print its six relevant files in one command. The `tail -n +1` command prints each file under a header with its name:

```bash
cd $FILES/demo10-credential-smells/lakeside-api
tail -n +1 .claude/settings.json .claude/token.sh .env .github/workflows/summary.yml scripts/nightly.sh ops/credentials.csv
```

**Expected output:**

```
==> .claude/settings.json <==
{
  "apiKeyHelper": ".claude/token.sh",
  "env": {
    "LAKESIDE_ENV": "prod",
    "LAKESIDE_REPORT_TOKEN": "FAKE-TOKEN-DO-NOT-USE"
  }
}

==> .claude/token.sh <==
#!/bin/sh
echo "FAKE-KEY-DO-NOT-USE-1001"

==> .env <==
LAKESIDE_DB_PASSWORD=FAKE-PASSWORD-DO-NOT-USE

==> .github/workflows/summary.yml <==
name: summary
on: [workflow_dispatch]
jobs:
  summarize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Summarize
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ORG_WIDE_CLAUDE_KEY }}
        run: claude -p "Summarize open issues" --output-format json

==> scripts/nightly.sh <==
#!/bin/sh
# Nightly summary job.
export CLAUDE_CODE_OAUTH_TOKEN=FAKE-TOKEN-DO-NOT-USE
claude -p "Summarize yesterday's failed builds" > nightly-summary.txt

==> ops/credentials.csv <==
credential,owner,expires,last_rotated,used_by
ORG_WIDE_CLAUDE_KEY,t.brandt@example.org,none,never,every repository in the organization
nightly OAuth token,s.ito@example.org,2027-09-01,2026-09-01,scripts/nightly.sh
```

Do not scroll back for the answers yet. Name the smell in each file first. Open a notes file:

```bash
mkdir -p ~/work && nano ~/work/demo10-notes.md
```

Write one line per file, with the file name and the smell you see. Save with **Ctrl+O**, then **Enter**. Exit with **Ctrl+X**. Give yourself three minutes.

<details>
<summary>Show the smells</summary>

| File | Smell |
|---|---|
| `.claude/settings.json` | A token value is written into a settings file that gets committed |
| `.claude/token.sh` | The key helper only echoes a fixed value, so the key never changes and is not fetched from anywhere |
| `.env` | A secrets file exists and no `Read` deny rule protects it |
| `.github/workflows/summary.yml` | The secret `ORG_WIDE_CLAUDE_KEY` has a shared name: it belongs to everybody and nobody |
| `scripts/nightly.sh` | A token variable is set in a script |
| `ops/credentials.csv` | The key has no expiry and was never rotated, and the nightly token is tied to one person |

</details>

---

## Step 2: Run the scanner

The scanner reads the files and looks for five patterns. It runs nothing and sends nothing. Go up one folder and scan the project:

```bash
cd $FILES/demo10-credential-smells
python3 smell_scan.py lakeside-api
```

**Expected output:**

```
smell 1  .claude/settings.json:5  key or token value written into a file
smell 2  .claude/token.sh:1  helper script only echoes a fixed value: echo "FAKE-KEY-DO-NOT-USE-1001"
smell 3  .env  an .env file exists and no Read deny rule covers it
smell 4  .github/workflows/summary.yml:10  shared-sounding secret name: ORG_WIDE_CLAUDE_KEY
smell 4  ops/credentials.csv:2  inventory row with no expiry: ORG_WIDE_CLAUDE_KEY
smell 4  ops/credentials.csv:2  shared-sounding secret name: ORG_WIDE_CLAUDE_KEY
smell 5  scripts/nightly.sh:3  credential variable set in a file: CLAUDE_CODE_OAUTH_TOKEN

7 finding(s) across 5 smell type(s).
```

Compare the scanner's list with your notes. The scanner reports seven findings in five types. Add any smell you missed to your notes file.

> **`python3: can't open file 'smell_scan.py'`?** You are in the wrong folder. Run `cd $FILES/demo10-credential-smells` and try again.

---

## Step 3: Name what the scanner cannot see

A scan finds patterns. It does not know people. Add one line to your notes file:

```bash
nano ~/work/demo10-notes.md
```

```
Scan cannot see: <two things about these credentials a scan cannot tell you>
```

<details>
<summary>Show example answers</summary>

- Who owns `ORG_WIDE_CLAUDE_KEY`. The inventory names `t.brandt@example.org`, but a scan cannot tell whether that person still works here.
- Whether anything was ever rotated. The inventory says `never`, and only a person can check whether that is true.
- Which repositories use the key. The inventory says "every repository in the organization", and a scan cannot confirm it.

</details>

---

## Step 4: Fix the top two smells

Pick the two smells you rate highest. In your notes file, write the fix and the rotation step for each:

```bash
nano ~/work/demo10-notes.md
```

```
Fix 1: <the smell, the fix, and the rotation step>
Fix 2: <the smell, the fix, and the rotation step>
```

<details>
<summary>Show example answers</summary>

```
Fix 1: ORG_WIDE_CLAUDE_KEY is shared and never expires. Replace it with a credential tied to one named owner with an expiry date. Rotation: create the new credential, update the workflow secret, revoke the old key, record the new owner and date in ops/credentials.csv.
Fix 2: .env has no deny rule. Add Read(./.env) to permissions.deny in .claude/settings.json. Rotation: treat the password as exposed if it was ever committed, change it, and keep only the new value outside the repository.
```

</details>

---

## Step 5: See where your own login is stored

Your own Claude Code login is a credential too. Check where it is stored without opening it:

```bash
ls -l ~/.claude/.credentials.json
```

**Expected output:** one line starting with `-rw-------`. Only your user can read and write the file. A line starting differently would mean other users on the machine can read it.

Now see which credential Claude Code uses. Start a session from your work folder, not from the project folder. Starting Claude Code inside `lakeside-api` would run its `apiKeyHelper` script and load its settings.

```bash
cd ~/work
claude
```

If the trust dialog appears, press **Down** to select **Yes, I trust this folder**, then press **Enter**. Type `/status` and press Enter. The status screen shows the active login. Leave Claude Code by typing `/exit` and pressing Enter.

> **`No such file or directory`?** Your login may be stored elsewhere on this machine. Skip the `ls` command and go on with `/status`.

---

## Step 6: Match the three kinds of credential

Automation uses one of three kinds of credential:

- A **personal token** is tied to one person.
- A **shared key** is tied to nobody and everybody.
- A **federated or service identity** is tied to a role the team owns.

Add one line to your notes file that classifies the first two credentials in this project and says what the third kind would add:

```bash
nano ~/work/demo10-notes.md
```

```
Kinds: ORG_WIDE_CLAUDE_KEY is <kind>. The nightly OAuth token is <kind>. A <kind> identity would <what it adds>.
```

<details>
<summary>Show the answer</summary>

```
Kinds: ORG_WIDE_CLAUDE_KEY is a shared key. The nightly OAuth token is a personal token (it belongs to s.ito@example.org). A federated or service identity would be owned by the team and survive a person leaving.
```

A shared key has no owner to ask. A personal token stops working when its person leaves. A service identity is owned by a role, so the team can name an owner, set a lifetime and rotate it.

</details>

---

## What you learned

- You find most credential smells by reading. A scanner finds the patterns and misses the ownership problems.
- Every credential needs a named owner, a lifetime and a rotation step. Without them, a secret is a leak that has not been found yet.
- Your own login is stored in a file only you can read, and `/status` shows which credential is active.
