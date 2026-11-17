# Lab 5: Credential Audit (take-home)

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Labs](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** Audit a small fictional deployment for credential problems, rank what you find, and write a rotation and ownership plan that covers personal keys and service account keys. Time: take-home, no set time.

**Files:** `$FILES/lab5-audit`: `harbor-org/` (the sample), `findings-template.md`, `check_findings_format.py`.

**Context:** `harbor-org` is a fictional company with three repositories, a managed settings file and three inventories in `org/`: credentials, CI secrets and departures. The audit date is 2026-10-12. Some of what you read is clean on purpose: one of the three repositories is clean, and reporting it as a defect costs the 8 points in the rubric below. Report the pattern and not the value. Every secret is a placeholder. A key helper (`apiKeyHelper`) returns a key from a script, and is meant for dynamic or rotating credentials. `claude setup-token` prints a one-year token that you set as `CLAUDE_CODE_OAUTH_TOKEN`, and it is for model requests only. Credentials are chosen by precedence, with cloud provider variables first, then an auth token, then `ANTHROPIC_API_KEY`, then a key helper, then the token variable, and then your sign-in. Credentials on Linux are in `~/.claude/.credentials.json` with mode 0600.

**Steps:**

1. **Read (take your time).** Goal: know the layout before you judge it.
   - Read `harbor-org/README.md`, the three CSV files, the managed settings file, and each repository's `.claude/` folder, workflow and any `.env` or helper script.
   - Hints: join the inventories. Ask which person owns each credential, whether that person is still there, and what each credential is used by.

2. **Write the findings.** Goal: one block per real problem, in `findings.md` copied from the template.
   - Acceptance criteria: each finding has a file and line, what is wrong, the risk, a severity, a fix, a rotation step and an owner. A "Not a finding" section lists what you checked and found sound, with a reason.
   - Hints: look at keys written into files, scripts that only echo a value, credentials shared across repositories, credentials owned by someone who left, personal keys sitting in a project folder, missing deny rules next to a secrets file, and whether a deny rule protects shell commands too. One repository is clean. A personal key and a service account key fail in different ways: say which is which.

3. **Rank them.** Goal: a priority order with a reason for every position.
   - Acceptance criteria: every numbered line names a finding and then says why it sits there, in a short clause. "1. Finding 1, because it is a live credential owned by a former employee" and "1. Finding 1 - live credential of a former employee" both work. "1. Finding 1 - highest" and "1. Finding 1: the shared CI key" do not: they restate the rank and the name, which the format checker and the rubric both read as no reason.
   - Hints: a live credential tied to someone who has left, and a secret with the widest reach, usually come first.

4. **Plan rotation and ownership.** Goal: a table with a row for every credential in the inventory.
   - Acceptance criteria: for each credential, the owner, its lifetime, where it is used, how it is rotated, and what happens when its owner leaves.
   - Hints: a credential owned by a person becomes a problem on the day that person leaves. Say who owns a credential after it is replaced.

5. **Compare three options in a paragraph.** Goal: what you would use for automation, and why. Write it in the template's `## Credential options for automation` section.
   - Acceptance criteria: a personal token, a shared key and a federated or service identity, each with one strength and one weakness. Mark anything you could not confirm from the course materials as unconfirmed.
   - This step is discussion: it carries no rubric points and the format checker does not look at it, but your facilitator reads it and will push back on anything asserted without a source.

6. **Check the format.** Run `python3 check_findings_format.py findings.md harbor-org/org/credentials_inventory.csv`.

**Checkpoint:** The format checker prints "Format is complete." Your facilitator scores the content.

**Common problems:**

- You list the clean repository as a finding: check its settings against the others before you decide.
- You list the same problem twice: a shared secret and the person who owns its backing key are two different findings.
- You report a credential's hygiene instead of its owner: "no expiry, never rotated" and "it sits in `.env`" describe the symptom. The finding is who owns that credential and whether that person is still there, which you only know once you join the inventory with `org/hr_departures.csv`. The rubric scores the join, not the rotation advice.
- Your priority list restates the finding names: "1. Finding 1 - highest" is a rank, not a reason. Say what makes it worse than the one below it.
- Your rotation table is missing a credential: the format checker names it.
- You paste a secret value into your report: remove it. Report the pattern.
- You propose to "move the key to another file in the repository": that fixes nothing.

**Scoring rubric (100 points):**

| Item | Points |
|---|---|
| Six planted problems, each worth 12 (identified 6, location 3, fix 3) | 72 |
| The clean repository is not reported as defective | 8 |
| Findings are prioritized with a stated reason | 8 |
| Rotation and ownership plan covers every credential | 12 |
