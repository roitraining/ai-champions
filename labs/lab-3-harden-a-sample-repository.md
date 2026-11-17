# Lab 3: Harden a Sample Repository

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Labs](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** Harden a deliberately weak project with a sandbox, network and file rules, deny rules and a fixed MCP list, then prove it with an attack script, and say what a sandbox does not cover. Time: 90 minutes.

**Files:** `$FILES/lab3-harden`: `report-archiver/` (the project, with `attack_simulation.py`), `check_settings.py`. Environment check: `$FILES/setup/check_env.sh`. Sandbox check and switch: `$FILES/setup/classroom-sandbox.sh`.

**Context:** The sandbox limits shell commands and their child processes. It needs `bubblewrap` and `socat` on Linux, and Ubuntu 24.04 and later may need an AppArmor change. `sandbox.failIfUnavailable: true` makes a missing sandbox a hard failure, where the default is to run unsandboxed. A `Read` deny rule blocks Claude's file tools, and `sandbox.filesystem.denyRead` covers shell commands, so you use both. Hooks, MCP servers and plugin processes run outside the sandbox. `report-archiver` is a tiny tool with a command injection in `app.py`. Its settings are wide open, a hook reports every tool call to an outside address, and `.mcp.json` declares a server nobody approved. `check_settings.py` scores the files (60 points). `attack_simulation.py` makes four harmless attempts and scores the outcomes (40 points). Both run on your machine.

**Steps:**

1. **Make the sandbox work (about 15 minutes).** Goal: a sandbox that really blocks a write, shown by the probe.
   - Run `bash $FILES/setup/check_env.sh`. Install `bubblewrap` and `socat` if it says so.
   - Then check whether the operating system is blocking the sandbox:
     `bash $FILES/setup/classroom-sandbox.sh --check`. On Ubuntu 24.04 and later an
     AppArmor profile usually is. If it says the profile is active, read the note below
     before you run `--on`.
   - Copy `report-archiver` to `~/work/report-archiver`. Run `python3 attack_simulation.py --baseline` in a normal terminal outside Claude Code, and check it says REACHABLE.
   - Acceptance criteria: inside a Claude Code session in the project, with the sandbox on, `touch ~/sandbox-probe` fails. On the Linux class image the message is "Read-only file system"; any refusal to write outside the project counts, the wording varies by platform. Then take a baseline: with the sandbox off, run `python3 attack_simulation.py` from the Bash tool and note the score.
   - Hints: Restart Claude Code after installing the dependencies, because the check runs at startup. The `/sandbox` panel has a Dependencies tab. If the probe file appears, delete it and fix the sandbox before you go on.

   > **About `--on`, because it is this lab's first real security decision.** On Ubuntu
   > 24.04 and later, the AppArmor profile `bwrap-userns-restrict` stops unprivileged
   > processes from creating nested user namespaces, which is exactly what the sandbox is
   > built on. `--on` disables that profile. It does **not** grant the permission to
   > Claude Code alone: the profile is machine-wide, so every process on the machine gains
   > what it lifts.
   >
   > Narrower options exist and neither works. Relaxing
   > `kernel.apparmor_restrict_unprivileged_userns` does nothing, because the profile stays
   > loaded and carries `audit deny capability`, and an AppArmor deny beats any allow. A
   > profile naming the `claude` binary does not work either, because the denial is raised
   > inside `unpriv_bwrap`, the profile that `/usr/bin/bwrap` transitions *into* —
   > confining the caller does not change what its child transitions to. Both were tested
   > on a class image and both failed.
   >
   > So the honest summary is: you are weakening a host control to switch on an application
   > sandbox. That is defensible on a disposable class machine holding nothing but
   > placeholders, and it is usually the wrong answer on a laptop or a build server. Run
   > `--off` when you finish the lab, and be ready to say in Step 6 what you would have
   > needed before doing this somewhere real.
   >
   > **If you cannot or choose not to run `--on`, the lab still works** — see the fallback
   > scoring under the rubric. You do not lose the lab, you lose the live half of Part B.

2. **Static baseline (about 5 minutes).** Goal: a table of what `check_settings.py` finds.
   - Run `python3 check_settings.py ~/work/report-archiver`. Acceptance criteria: every FAIL with one sentence on the risk.
   - Point the checker at the copy you are hardening. It judges `allowWrite` and `denyRead` by
     where each entry resolves against that path, so the path you pass has to be the project the
     settings file belongs to.

3. **Harden the settings (about 30 minutes).** Goal: Part A scores 60 of 60, and the project still works for its job.
   - Acceptance criteria:
     - The sandbox is on and a missing sandbox is a hard failure.
     - Nothing is excluded from the sandbox on purpose.
     - Network access is limited to a short list of approved domains: `pypi.org` and `files.pythonhosted.org`.
     - Writes are limited to the project, and `.claude` and `.mcp.json` cannot be written by shell commands.
     - The secrets file and `~/.ssh` are protected from reads by shell commands, and the secrets file and `.env` are also protected from Claude's file tools.
     - `curl` and `wget` are denied, and there is no blanket Bash allow.
     - Only the two approved servers (`docs-search`, `ticket-bridge`) remain in `.mcp.json`.
     - No hook command and no hook script sends data to the network, and every hook that stays points at a script that is still there to read, still has code in it, and shows that code in the file rather than building it at run time with `exec` or `eval`.
     - `python3 app.py q3.txt` still runs and still prints a checksum.
   - Hints: Read the settings file top to bottom and ask of each line what it grants. A wildcard in a domain list defeats the list, in any shape: `*` and `*.com` are both wildcards. A command in `excludedCommands` is a hole in the wall. A hook is code that runs outside the sandbox, so reading it matters more than sandboxing it. `.env` needs its own `Read` deny rule: one for `secrets.env` does not cover it. Run the checker after each change and not once at the end.

4. **Fix the code (about 10 minutes).** Goal: the command injection is closed in `app.py`.
   - Acceptance criteria: a report name such as `q3.txt ; echo injected > INJECTED_MARKER` is rejected or treated as a plain file name, and `python3 app.py q3.txt` still prints a checksum.
   - Hints: a sandbox does not stop a command that runs inside the working directory. Where does the name reach a shell? Prefer fixing the call over cleaning the text.

5. **Prove it (about 20 minutes).** Goal: Part B at 40 of 40, observed live.
   - Start `claude` in the project with the sandbox on. Ask Claude to run `python3 attack_simulation.py`. Save the output.
   - Acceptance criteria: the sandbox probe line says the sandbox looks active; attempts 1, 2 and 3 are BLOCKED; attempt 4 is BLOCKED by your code fix; the score is 40.
   - Hints: if attempt 2 reads BLOCKED with the sandbox off, the machine has no internet. Use the baseline. **With the sandbox on, attempt 2 reports a DNS failure — that counts as blocked.** The network proxy refuses the name before any connection is made, so a resolution error is the expected shape of the block, not a separate problem (measured 2026-11-15). If attempt 3 is not blocked, check the sandbox `denyRead` entry, not just the Read deny rule. Restart Claude Code after each settings change.

   > **If the session refuses every command**, including the attack script, with
   > `apply-seccomp: ... Permission denied`, then your configuration is correct and this
   > machine has no working sandbox. `failIfUnavailable: true` is doing its job. You cannot
   > produce the table from inside the session: run `python3 attack_simulation.py` in your
   > own terminal instead, record attempt 4 from that, and take attempts 1 to 3 from the
   > checker's predictions under the fallback scoring. That is the expected path on a
   > machine without the sandbox, not a mistake on your part.

6. **Write what it does not cover (about 10 minutes).** Goal: five sentences, in a file called `GAPS.md`.
   - Acceptance criteria: it names at least three things the sandbox does not limit (for example hooks, MCP servers, plugin processes and Claude's file tools), says which of your controls covers each one, and says what the code fix did that the sandbox could not.
   - If you ran `classroom-sandbox.sh --on` in Step 1, add one line: you turned off a
     host control to turn on an application sandbox. What would you have needed — approval,
     compensating controls, a different machine — before doing that somewhere that
     mattered?

**Checkpoint:** Part A is 60, and `GAPS.md` exists. With a working sandbox, the attack
script also reports at least three BLOCKED attempts. Without one, the checker predicts
attempts 1 to 3 blocked from your configuration and attempt 4 is BLOCKED live in your own
terminal.

**Common problems:**

- The probe write succeeds: the sandbox is not running. A missing dependency, an AppArmor restriction on Ubuntu 24.04 and later, or a container that blocks user namespaces. The default behavior is to run unsandboxed when it cannot start, which is why `failIfUnavailable` matters.
- Claude Code exits at startup after you set `failIfUnavailable`: the sandbox cannot start on this machine. Fix the dependency. That is the setting working.
- You blocked everything and the tool no longer runs: `allowWrite` must still allow the project folder, and `python3` must still run.
- Attempt 3 still succeeds: only the `Read` deny rule is set. It covers Claude's file tools and not a script run by the shell.
- `allowWrite` is marked too broad: the checker expands `~` and `$HOME` and then asks whether the entry lands inside the project you passed on the command line. `.` and `~/work/report-archiver` both pass; your home folder passes nothing, however it is spelled.
- Part A stays below 60 after you fixed a line: read the FAIL line, it names the entry it could not accept. `denyRead` needs `~/.ssh` plus either the secrets file or the folder holding it, and `permissions.deny` needs a `Read` rule whose file name is `.env`.
- The hook check still fails after you commented the sending lines out: the checker reads the code, not the prose, so a commented-out `urlopen` is not counted as a network call — but the hook entry is still wired to a script with nothing left to run, and that fails the same way a hook pointing at a deleted script does. Remove the hook entry as well. Same answer for a script that hides its body in `exec("...")`: a hook nobody can read cannot be signed off.
- A server stays in `.mcp.json`: check the name against the approved list.

**Scoring rubric (100 points):**

| Item | Points |
|---|---|
| Part A: `check_settings.py` (twelve checks, 60 points) | 60 |
| Part B: each attack BLOCKED live is 10 points (write outside, disallowed domain, secrets read, injection) | 40 |

A missing `GAPS.md` or a Part B result with no saved output caps the total at 90. Zeroing the Claude-facing features to pass, for example deleting `app.py`, the report it reads or the secrets file the deny rules are meant to protect, scores 0 for the lab.

**Fallback scoring, when the sandbox cannot start on your machine.** Part A is 60 and
works everywhere — it reads files and runs nothing. Attempts 1 to 3 need the sandbox, so
they are scored 5 each from the outcomes `check_settings.py` **predicts** from your
configuration. Attempt 4 is always scored live, because a command injection inside the
working directory needs no sandbox to demonstrate: run `python3 attack_simulation.py` in
your own terminal for it. **The maximum is 85.** A sandbox that will not start on your
machine is a known platform limit, not a failure, and your instructor will say before the
lab which scoring applies.

> Read the predictions rather than assuming them. An attempt is worth 5 only where the
> checker predicts it blocked — on an unhardened configuration it predicts none of them.
