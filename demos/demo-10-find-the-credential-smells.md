# Demo 10: Find the Credential Smells

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Demos](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** Spot the common credential smells in a small project, and say for each who owns it, how long it lives and how it is rotated. Time: about 10 minutes.

**Files:** `$FILES/demo10-credential-smells`: `lakeside-api/` (a fictional project), `smell_scan.py`.

**Context:** The project holds a key in a settings file, a key helper that only echoes a fixed value, an `.env` file with no deny rule, a shared-sounding CI secret, an inventory row with no expiry, and a token set in a script. All values are placeholders. A scan finds patterns, and it cannot tell you who owns a credential.

**Steps:**

1. Open `lakeside-api/.claude/settings.json`, `.claude/token.sh`, `.github/workflows/summary.yml`, `scripts/nightly.sh` and `ops/credentials.csv`. Spend 3 minutes naming each smell as you open a file.
2. Run the scan: `python3 smell_scan.py lakeside-api`. Compare its list with yours.
3. Ask what the scan cannot see. (Who owns `ORG_WIDE_CLAUDE_KEY`, whether `t.brandt` still works here, whether anything was ever rotated.)
4. For the top two smells, write down the fix and the rotation step.
5. Show where your own login is stored without opening it. On Linux: `ls -l ~/.claude/.credentials.json` (mode `-rw-------`). Run `/status` to see which credential is active.
6. Close with the three kinds of credential for automation: a personal token (tied to a person), a shared key (tied to nobody and everybody), and a federated or service identity (tied to a role the team owns).

**Expected result:** You find most smells by eye. The scan finds the patterns and misses the ownership problems, which only a person reading the inventory can see.

**Why this matters:** Credentials are where most real incidents start. A named owner, a lifetime and a rotation step turn a secret into something a team manages. Without them, it is a leak that has not been found yet.
