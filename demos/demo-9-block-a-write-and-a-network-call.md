# Demo 9: Block a Write and a Network Call

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Demos](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** See an operating-system sandbox block a write outside the working directory and a call to a domain that is not allowed, and see what fail-closed means. Time: about 12 minutes.

**Files:** `$FILES/demo9-sandbox`: `configs/`, `apply.sh`, `project/probe.sh`. Environment check: `$FILES/setup/check_env.sh`.

**Context:** The sandbox covers shell commands and their child processes. Claude's file tools, MCP servers and hooks run outside it. On Linux and WSL2 it needs `bubblewrap` and `socat`. **On Ubuntu 24.04 and later the AppArmor profile `bwrap-userns-restrict` is loaded and enforcing by default, and it blocks bubblewrap.** `sandbox.failIfUnavailable: true` makes an unavailable sandbox a hard failure; by default Claude Code runs commands unsandboxed instead. **Where that failure surfaces depends on why the sandbox is unavailable:** with `bubblewrap` missing the startup check fails and Claude Code exits at startup, which is what step 5 shows. With `bubblewrap` installed but AppArmor blocking it, the startup check passes, the session starts normally, and every shell command is refused at run time with `apply-seccomp: ... Permission denied` instead.

**Steps:**

1. Run `bash $FILES/setup/check_env.sh`. Read the `bubblewrap` and `socat` lines and the sandbox line. **On Ubuntu 24.04 and later the sandbox line says the profile is blocking. Fix that first:** run `bash $FILES/setup/classroom-sandbox.sh --check`, then `--on` (it needs sudo and is machine-wide), then `--check` again. Both controls must read clear (profile clear, sysctl 0). Run `--off` when you finish, but only if you ran `--on`. If the first `--check` already reads clear, skip `--on` and `--off`.
2. Sandbox off: `cd $FILES/demo9-sandbox && bash apply.sh off`, then `cd project && claude`. Ask: `Run bash probe.sh`. Probes 1, 2 and 3 report SUCCEEDED, and probe 4 gets a response.
3. Sandbox on: exit, run `bash ../apply.sh on`, and restart `claude`. Open `/sandbox` to show the panel. Ask for the probe again. Probes 1, 2 and 3 report BLOCKED. Probe 4 (an allowed domain) still gets a response. If a command fails with `apply-seccomp: ... Permission denied`, the sandbox never started: go back to step 1.
4. Learn the one-line check you will use on any machine: ask Claude to run `touch ~/sandbox-probe`. With the sandbox working it fails with "Read-only file system".
5. Fail closed, without removing any package: build a PATH that has no `bwrap`, and start Claude with it. Once: `mkdir -p ~/nobwrap && for f in /usr/bin/*; do [ "${f##*/}" != bwrap ] && ln -sf "$f" ~/nobwrap/; done`. Then from `project`, with `bash ../apply.sh on`, run `env PATH=$HOME/nobwrap /usr/bin/claude` and ask for any shell command: Claude warns `Sandbox disabled ... Commands will run WITHOUT sandboxing` and runs it (the default). With `bash ../apply.sh fail-closed`, the same start refuses: `sandbox.failIfUnavailable is set, refusing to start without a working sandbox`. Remove `~/nobwrap` afterwards.
6. Note what the sandbox does not cover: hooks, MCP servers and plugin processes, and Claude's own file tools.

**Expected result:** The probes flip from SUCCEEDED to BLOCKED when the sandbox is on, the allowed domain still answers, and a missing sandbox is a hard failure only when `failIfUnavailable` is true.

**Why this matters:** A sandbox is the layer that still holds when a rule is missing or the model is persuaded. Fail-closed turns a quiet loss of protection into a loud stop. Knowing what the sandbox does not cover is what keeps the team from over-trusting it.
