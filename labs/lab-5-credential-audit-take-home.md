# Lab 5: Credential Audit (take-home)

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** Take-home, no set time

> Part of **[AI Champions Training: Labs](README.md)**.

## What you will do

You audit a fictional company, Harbor Example Co (`harbor-org`). It has three repositories, a managed settings file and three inventories: credentials, CI secrets and departures. The audit date is **2026-10-12**. Every secret is a placeholder. Report the pattern, not the value.

You write one file, `findings.md`, with five parts:

| Part of `findings.md` | What it holds |
|---|---|
| `## Finding N` blocks | One block per real problem |
| `## Not a finding` | What you checked and found sound |
| `## Priority order` | Your findings ranked, with a reason for each position |
| `## Rotation and ownership plan` | A table row for every credential in the inventory |
| `## Credential options for automation` | One paragraph comparing three options |

A format checker confirms the structure. Your facilitator scores the content against an answer key.

**Background you need for Steps 4 and 9:**

- A key helper (`apiKeyHelper`) returns a key from a script. It is meant for dynamic or rotating credentials.
- `claude setup-token` prints a one-year token. You set it as `CLAUDE_CODE_OAUTH_TOKEN`. It works for model requests only.
- Claude Code picks a credential in this order: cloud provider variables, an auth token, `ANTHROPIC_API_KEY`, a key helper, the token variable, then your sign-in.
- On Linux, your sign-in credentials are in `~/.claude/.credentials.json` with mode `0600`.

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md)
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

This lab needs almost no model use. Step 10 has an optional `claude` prompt.

---

## Step 1: Copy the sample and the template

Open a terminal (the **Terminal Emulator** icon on the desktop) and run:

```bash
mkdir -p ~/work && cp -r $FILES/lab5-audit ~/work/lab5-audit && cd ~/work/lab5-audit && cp findings-template.md findings.md && ls
```

**Expected output:**

```
check_findings_format.py  findings-template.md  findings.md  harbor-org
```

`findings.md` is your working copy of the template. Keep `findings-template.md` as it is.

Keep rough notes in a second file, `notes.md`. The checker ignores it:

```bash
nano notes.md
```

In `nano`, type to edit. **Ctrl+O**, then **Enter**, saves. **Ctrl+X** exits. To use a graphical editor, open the file in **Visual Studio Code** from the desktop.

> **`No such file or directory`?** `$FILES` is empty. Set it with the tip in Prerequisites and run the command again.

---

## Step 2: Read the layout and the policy

List every file in the sample:

```bash
find harbor-org -type f | sort
```

**Expected output:**

```
harbor-org/README.md
harbor-org/org/ci_secrets_inventory.csv
harbor-org/org/credentials_inventory.csv
harbor-org/org/hr_departures.csv
harbor-org/org/managed-settings.json
harbor-org/repos/billing-service/.claude/settings.json
harbor-org/repos/billing-service/.github/workflows/claude-review.yml
harbor-org/repos/inventory-service/.claude/get_key.sh
harbor-org/repos/inventory-service/.claude/settings.json
harbor-org/repos/inventory-service/.env
harbor-org/repos/inventory-service/.github/workflows/claude-review.yml
harbor-org/repos/payments-gateway/.claude/settings.json
harbor-org/repos/payments-gateway/.github/workflows/claude-review.yml
```

The order may differ. Read the README, which states Harbor's policy:

```bash
cat harbor-org/README.md
```

The policy has three rules. You audit against them:

- Every credential has a named owner. A credential owned by a person is re-issued to a team when that person changes role or leaves.
- Every credential is rotated **at least every 180 days**, and on the day its owner leaves. A credential whose `last_rotated` is `never` is measured from its `created` date.
- CI secrets are scoped to a single repository.

Work out the oldest date a credential may have been last rotated and still pass on the audit date:

```bash
date -d "2026-10-12 - 180 days" +%F
```

**Expected output:**

```
2026-04-15
```

A credential last rotated before this date breaks the 180-day rule.

---

## Step 3: Read the inventories

The three inventories describe the same credentials from different sides. Print each as an aligned table. If the lines wrap, widen the terminal window first:

```bash
column -s, -t harbor-org/org/credentials_inventory.csv
column -s, -t harbor-org/org/ci_secrets_inventory.csv
column -s, -t harbor-org/org/hr_departures.csv
```

**Expected output:**

```
credential_id  kind                 owner                      used_by                                        created     expires     last_used   last_rotated
cred-101       service account key  p.nakamura@example.org     CI for billing-service and inventory-service   2025-11-03  none        2026-10-09  never
cred-102       service account key  platform-team@example.org  CI for payments-gateway                        2026-08-20  2027-02-20  2026-10-11  2026-08-20
cred-103       service account key  platform-team@example.org  nightly report job                             2026-05-02  2026-11-02  2026-10-12  2026-05-02
cred-104       personal API key     j.alvarez@example.org      local developer sessions on inventory-service  2025-12-01  none        2026-10-05  never
secret_name             scope         repositories                         backing_credential  last_rotated
SHARED_CLAUDE_CI_KEY    organization  "billing-service;inventory-service"  cred-101            never
CLAUDE_CI_KEY_PAYMENTS  repository    payments-gateway                     cred-102            2026-08-20
email                   name         last_day
p.nakamura@example.org  P. Nakamura  2026-06-30
j.alvarez@example.org   J. Alvarez   2026-03-15
```

**Your task:** join the three tables. For each credential, write in `notes.md`:

- who owns it, and whether that person is still there
- what uses it
- whether it breaks the 180-day rule or the one-repository rule

The join is the core of the audit. A credential's age and file location are symptoms. Its owner and what depends on it are the finding.

<details>
<summary>Show a command that joins the inventory with the departures</summary>

```bash
for o in $(cut -d, -f3 harbor-org/org/credentials_inventory.csv | tail -n +2 | sort -u); do if grep -q "$o" harbor-org/org/hr_departures.csv; then echo "$o  LEFT (last day $(grep "$o" harbor-org/org/hr_departures.csv | cut -d, -f3))"; else echo "$o  still employed"; fi; done
```

**Expected output:**

```
j.alvarez@example.org  LEFT (last day 2026-03-15)
p.nakamura@example.org  LEFT (last day 2026-06-30)
platform-team@example.org  still employed
```

The loop takes each distinct owner from the credentials file and looks for that email in the departures file.

</details>

> **`column: command not found`?** Use `cat harbor-org/org/credentials_inventory.csv` instead. The fields are separated by commas.

---

## Step 4: Read each repository

Each repository has a `.claude/` folder and a CI workflow. Two of them also hold a `.env` file or a key helper. Print files with line numbers, so you can cite a file and line in your findings:

```bash
cat -n harbor-org/org/managed-settings.json
```

**Expected output:**

```
     1	{
     2	  "permissions": {
     3	    "disableBypassPermissionsMode": "disable"
     4	  }
     5	}
```

Now read every file in the three repositories the same way. Start with one repository:

```bash
cd harbor-org/repos/billing-service
cat -n .claude/settings.json .github/workflows/claude-review.yml
cd ~/work/lab5-audit
```

Repeat for `inventory-service` and `payments-gateway`. Include `.env` and `.claude/get_key.sh` where they exist. Add `ls -a` in each repository to see hidden files.

Ask these questions of every file:

- Is a key or password written into it?
- Does a script only echo a value, with no lookup or rotation behind it?
- Which secret does the workflow use, and which repositories share it?
- Does the `.claude/` folder deny reading the secrets files? Does the rule also cover shell commands, or only Claude's file tool?
- Is a personal key sitting in a project folder?

One repository is clean. Compare its settings with the other two before you decide which.

Write what you find in `notes.md`.

<details>
<summary>Show a command that finds placeholder secrets with line numbers</summary>

```bash
grep -rn "FAKE" harbor-org/repos | sort
```

**Expected output:**

```
harbor-org/repos/billing-service/.claude/settings.json:3:    "ANTHROPIC_API_KEY": "FAKE-KEY-DO-NOT-USE-0001",
harbor-org/repos/inventory-service/.claude/get_key.sh:3:echo "FAKE-KEY-DO-NOT-USE-0002"
harbor-org/repos/inventory-service/.env:1:INVENTORY_DB_PASSWORD=FAKE-PASSWORD-DO-NOT-USE
harbor-org/repos/inventory-service/.env:2:WAREHOUSE_API_TOKEN=FAKE-TOKEN-DO-NOT-USE
harbor-org/repos/inventory-service/.env:3:ANTHROPIC_API_KEY=FAKE-KEY-DO-NOT-USE-0004
```

This finds written-in keys only. It does not find a shared secret, a missing deny rule or a former owner. Those come from reading the files and joining the inventories.

</details>

---

## Step 5: Write the findings

A finding is a real credential or secret hygiene problem. Open `findings.md`:

```bash
nano findings.md
```

Write one `## Finding N` block for each problem. Every block has seven fields. Keep the headings and the bold labels exactly as the template has them. The checker reads them.

**Done when** each block has:

- **File and line:** where the problem is. A finding that spans files lists each location.
- **What is wrong**
- **Risk**
- **Severity:** `high`, `medium` or `low`
- **Fix**
- **Rotation step**
- **Owner**

Severity means:

- **High:** the credential is already exposed, or is live and unaccountable.
- **Medium:** exposure is possible but needs something further to happen, and nothing shows it has.
- **Low:** hygiene that does not expose a credential on its own.

If a credential is not in the inventory and has no owner, write `unassigned - not in the inventory` and say who should own it.

Here is one finished block from a different company, so you can see the level of detail. It is not part of `harbor-org`:

```
## Finding 1

- **File and line:** `acme-web/deploy/Dockerfile:14`; `acme-web/.github/workflows/build.yml:22`
- **What is wrong:** The registry token is written into the Dockerfile as the default value of a build argument, and the workflow passes it again in clear text.
- **Risk:** Anyone who can read the repository, or pull an image built from it, can push images as the build service.
- **Severity:** high
- **Fix:** Remove the default value. Pass the token at build time from the CI secret store.
- **Rotation step:** Revoke the exposed token in the registry, issue a new one, and store it only in the CI secret store.
- **Owner:** build-team@acme.example, owner of the registry service account
```

**Look for** these kinds of problem:

- keys written into files
- scripts that only echo a value
- credentials shared across repositories
- credentials owned by someone who left
- personal keys in a project folder
- a missing deny rule next to a secrets file, and a deny rule that protects the file tool but not shell commands

A personal key and a service account key fail in different ways. Say which is which.

> **Unsure whether two findings are the same problem?** A shared secret and the person who owns its backing key are two different findings.
>
> **Your finding describes the symptom?** "No expiry, never rotated" and "it sits in `.env`" are symptoms. The finding is who owns the credential and whether that person is still there. You only know that once you join the inventory with `hr_departures.csv`.
>
> **You proposed to move the key to another file in the repository?** That fixes nothing. Name where the key should live, such as a secret store, and how it is rotated.
>
> **You pasted a secret value?** Remove it. Report the pattern.

---

## Step 6: List what is sound

In `findings.md`, under `## Not a finding`, list each item you checked and found sound. Give a reason for each. Use a `-` bullet per item.

Check any item you are unsure about against the policy in Step 2.

> **You listed the clean repository as a finding?** Check its settings against the others before you decide. Reporting it costs 8 points.

---

## Step 7: Rank the findings

Under `## Priority order`, write a numbered list. Every line names a finding and gives a short reason for its position.

**Done when** every numbered line has a reason after the finding's name. These work:

```
1. Finding 1, because it is a live credential owned by a former employee
1. Finding 1 - live credential of a former employee
```

These do not. They restate the rank or the name, and the checker reads them as no reason:

```
1. Finding 1 - highest
1. Finding 1: the shared CI key
```

A live credential tied to someone who has left, and a secret with the widest reach, usually come first.

---

## Step 8: Plan rotation and ownership

Under `## Rotation and ownership plan`, fill the table. It needs **a row for every credential in the inventory**. List the credential ids:

```bash
cut -d, -f1 harbor-org/org/credentials_inventory.csv | tail -n +2
```

**Expected output:**

```
cred-101
cred-102
cred-103
cred-104
```

For each credential, give the owner, its lifetime, where it is used, how it is rotated, and what happens when its owner leaves. Say who owns a credential after it is replaced. A credential owned by a person becomes a problem on the day that person leaves.

A row from the different company in Step 5 looks like this:

```
| cred-901 | build-team@acme.example | 90 days | acme-web CI | Revoke in the registry, issue a new token, update the CI secret store | Re-assigned to build-team before the owner's last day |
```

> **The checker names a missing credential?** Add a row whose first cell contains that id, such as `cred-103`.

---

## Step 9: Compare three options

Under `## Credential options for automation`, write one paragraph. Compare a **personal token**, a **shared key** and a **federated or service identity**. Give one strength and one weakness for each. Then say which you would use for automation and why.

Mark anything you could not confirm from the course materials as `unconfirmed`. Your facilitator reads this paragraph. It carries no points and the checker does not look at it. Expect questions about anything you assert without a source.

<details>
<summary>Show an outline for the paragraph</summary>

```
A personal token ... (strength) ... (weakness). A shared key ... (strength) ... (weakness).
A federated or service identity ... (strength) ... (weakness). For automation I would use ...
because ... . I could not confirm ... from the course materials: unconfirmed.
```

</details>

---

## Step 10: Check the format

Run the checker on your file and the credentials inventory:

```bash
cd ~/work/lab5-audit
python3 check_findings_format.py findings.md harbor-org/org/credentials_inventory.csv
```

The checker tests structure only. It does not judge whether your findings are right.

**Expected output on the blank template** (what you see if you run it before you write anything):

```
  finding 1: empty fields: File and line, What is wrong, Risk, Fix, Rotation step, Owner
  finding 2: empty fields: File and line, What is wrong, Risk, Severity, Fix, Rotation step, Owner
[MISSING] 0 complete finding blocks (need at least 4)
[MISSING] 'Not a finding' section has an item
[MISSING] priority list has 0 items, 0 with a reason (need 4+, all with a reason)
[MISSING] rotation table covers every credential in the inventory (missing: cred-101, cred-102, cred-103, cred-104)

Fix the MISSING items, then hand the file to your facilitator.
```

**Expected output when the file is complete:**

```
[ok] 4 complete finding blocks (need at least 4)
[ok] 'Not a finding' section has an item
[ok] priority list has 4 items, 4 with a reason (need 4+, all with a reason)
[ok] rotation table covers every credential in the inventory

Format is complete.
```

The first number depends on how many findings you wrote. Fix every `[MISSING]` line and run the checker again.

**Checkpoint:** the checker prints `Format is complete.` Give `~/work/lab5-audit/findings.md` to your facilitator, who scores the content.

To get a second opinion before you hand it in, start Claude Code in the folder with `claude`. At the trust question press **Down**, then **Enter**. Then type the prompt in the block below. Judge the reply yourself: Claude can be wrong.

<details>
<summary>Show a prompt for a second opinion</summary>

```
Read findings.md and the files under harbor-org. For each finding I wrote, say whether the file and line are correct and whether the severity fits the definitions in the template. Do not add findings of your own.
```

Type `/exit` when you finish.

</details>

> **The checker says a priority line has no reason?** Name what makes it worse than the one below it. A rank word such as "highest" or "critical" is not a reason.
>
> **`no ## Finding N headings found`?** Check the spelling: `## Finding 1`, one heading per finding, a space after the hashes.
>
> **A field shows as empty though you wrote it?** Write the text on the same line as its label, after `**Risk:**`. The checker reads one line per field.
>
> **`python3: can't open file`?** You are not in `~/work/lab5-audit`. Run `cd ~/work/lab5-audit`.

---

## What you built

You:

- Joined three inventories to find who owns each credential and whether that person is still there
- Wrote findings with a file, a risk, a severity, a fix, a rotation step and an owner
- Separated real problems from what is sound, including one clean repository
- Ranked the findings, with a reason for every position
- Planned rotation and ownership for every credential, including what happens when an owner leaves

## How the score is made

Your facilitator scores the content with this rubric:

| Item | Points |
|---|---|
| Six planted problems, each worth 12 (identified 6, location 3, fix 3) | 72 |
| The clean repository is not reported as defective | 8 |
| Findings are prioritized with a stated reason | 8 |
| Rotation and ownership plan covers every credential | 12 |

## Cleanup

Nothing needs undoing. Every secret in this lab is a placeholder. Keep `~/work/lab5-audit` until your facilitator has scored it.
