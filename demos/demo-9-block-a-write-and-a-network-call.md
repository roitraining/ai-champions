# Demo 9: Block a Write and a Network Call

**Course:** AI Champions Training: Claude Code for Engineering Teams | **Duration:** 12 minutes

> Part of **[AI Champions Training: Demos](README.md)**.

## What you will do

You run four probes with the sandbox off, then on. You see the sandbox block a write outside the working directory and a call to a domain that is not allowed. Then you see what **fail closed** means.

The sandbox is an operating-system layer that limits shell commands and their child processes. Claude's own file tools, MCP servers and hooks run outside it. On Linux it needs `bubblewrap` and `socat`. By default, when the sandbox cannot start, Claude Code runs your commands without it. The setting `sandbox.failIfUnavailable: true` turns that into a hard stop.

## Prerequisites

- [ ] You completed [`SETUP.md`](../SETUP.md): `claude --version` prints a version and `claude auth status` shows you are signed in
- [ ] `$FILES` is set. Run `echo $FILES`. It should print a path ending in `/demo-files`

> **`echo $FILES` printed nothing?** Run `export FILES=~/champions/demo-files` and try again. Do this in every new terminal window unless you added it to `~/.bashrc` as `SETUP.md` shows.

---

## Step 1: Check that the sandbox can start

Open a terminal (the **Terminal Emulator** icon on the desktop) and run the environment check. Read the `bubblewrap`, `socat` and sandbox lines:

```bash
bash $FILES/setup/check_env.sh
```

Then ask the sandbox script whether the operating system is blocking the sandbox. This command changes nothing:

```bash
bash $FILES/setup/classroom-sandbox.sh --check
```

**Expected output** on the class image:

```
  AppArmor profile bwrap-userns-restrict : clear
  kernel.apparmor_restrict_unprivileged_userns : 0
[ OK ] Nothing is blocking the sandbox - both controls are clear.
       Confirm it for real inside a session: ask Claude to run 'touch ~/sandbox-probe'.
       It should fail with 'Read-only file system'. If it succeeds, you are NOT sandboxed.
       Nothing to switch on. Leave the machine as it is: run --off only if YOU ran --on.
```

Both controls read `clear`, so the sandbox can start. Go on to Step 2.

> **The output says the profile is `BLOCKING`, or says the sandbox cannot start?** On Ubuntu 24.04 and later an AppArmor profile can stop `bubblewrap`. Run `bash $FILES/setup/classroom-sandbox.sh --on`. It needs `sudo` and changes the whole machine, not only Claude Code. Then run `--check` again. Both controls must read `clear`. When you finish the demo, run `--off` to put the machine back. If the first `--check` already read `clear`, do not run `--on` or `--off`.

---

## Step 2: Copy the project and turn the sandbox off

You work on a copy, so the course files stay unchanged:

```bash
mkdir -p ~/work && rm -rf ~/work/demo9-sandbox && cp -r $FILES/demo9-sandbox ~/work/demo9-sandbox && cd ~/work/demo9-sandbox && bash apply.sh off
```

**Expected output:**

```
Applied sandbox-off.json. Restart Claude Code in /home/<you>/work/demo9-sandbox/project, or run /sandbox to check the panel.
```

`apply.sh` copies one of three configurations into `project/.claude/settings.json`. Look at the one it applied:

```bash
cat project/.claude/settings.json
```

**Expected output:**

```
{}
```

An empty settings file means no sandbox.

---

## Step 3: Run the probes with the sandbox off

Start Claude Code in the project folder:

```bash
cd project
claude
```

The first time you start Claude Code in a folder, it asks whether you trust it. The default answer is **No, exit**. Press **Down** to select **Yes, I trust this folder**, then press **Enter**. The bottom of the screen shows `auto mode on`. Leave it.

Type this prompt:

```
Run bash probe.sh
```

`probe.sh` makes four attempts: a write outside the project folder, a write to your home folder, a call to a domain that is not allowed, and a call to a domain that is allowed. It cleans up after itself.

**Expected output:** Claude shows the script's output, probably with its own comments around it:

```
1 write outside the working directory (../outside-probe.txt):
   SUCCEEDED
2 write to the home folder (~/sandbox-probe):
   SUCCEEDED
3 call a domain that is NOT on the allowed list (example.com):
   SUCCEEDED (HTTP 200)
4 call a domain that IS on the allowed list (pypi.org), for contrast:
   HTTP status: 200
```

With no sandbox, probes 1, 2 and 3 all succeed.

> **Probe 3 says `BLOCKED` with the sandbox off?** This machine may have no internet. Exit Claude Code and run `curl -sS -m 6 -o /dev/null -w '%{http_code}\n' https://example.com` in a normal terminal. If that does not print `200`, probe 3 is blocked for the wrong reason.

---

## Step 4: Turn the sandbox on and run the probes again

Leave Claude Code by typing `/exit` and pressing Enter. Then apply the sandbox configuration and restart:

```bash
bash ../apply.sh on
claude
```

Claude Code reads settings at startup, so you must restart it after each change. Look at the configuration you applied:

```bash
cat .claude/settings.json
```

**Expected output:**

```
{
  "sandbox": {
    "enabled": true,
    "network": {
      "allowedDomains": ["pypi.org"]
    }
  }
}
```

Inside `claude`, type `/sandbox` and press Enter to open the sandbox panel. Close it with **Esc**. Then ask for the probes again:

```
Run bash probe.sh
```

**Expected output:** probes 1, 2 and 3 are blocked, and probe 4 still gets an answer:

```
1 write outside the working directory (../outside-probe.txt):
   BLOCKED
2 write to the home folder (~/sandbox-probe):
   BLOCKED
3 call a domain that is NOT on the allowed list (example.com):
   BLOCKED (no HTTP 200; got '...')
4 call a domain that IS on the allowed list (pypi.org), for contrast:
   HTTP status: 200
```

The code after `got` in probe 3 varies. Probe 4 reaches `pypi.org` because the configuration allows that domain.

> **A command fails with `apply-seccomp: ... Permission denied`?** The sandbox never started, and `/sandbox` shows no warning. Go back to Step 1 and check both controls read `clear`.

---

## Step 5: Learn the one-line check

On any machine, you can test whether the sandbox works. Ask Claude:

```
Run touch ~/sandbox-probe
```

**Expected output:**

```
touch: cannot touch '/home/<you>/sandbox-probe': Read-only file system
```

Writes outside the project folder fail. If instead the command succeeds, you are not sandboxed. Delete the file with `rm ~/sandbox-probe` and go back to Step 1.

Leave Claude Code with `/exit`.

---

## Step 6: See fail closed

By default, a missing sandbox is not an error. Claude Code runs unsandboxed. You can test this without uninstalling anything. Build a folder of links to every program in `/usr/bin` except `bwrap`, then start Claude with that folder as its `PATH`.

Build the folder once:

```bash
mkdir -p ~/nobwrap && for f in /usr/bin/*; do [ "${f##*/}" != bwrap ] && ln -sf "$f" ~/nobwrap/; done
```

**Expected output:** none.

Start Claude with the sandbox on, but without `bwrap`:

```bash
cd ~/work/demo9-sandbox/project
bash ../apply.sh on
env PATH=$HOME/nobwrap "$(command -v claude)"
```

Ask for any shell command, for example `Run ls`.

**Expected result:** Claude warns `Sandbox disabled ... Commands will run WITHOUT sandboxing` and runs the command. That is the default behavior. Nothing protected you, and the only sign was one warning.

Leave Claude Code with `/exit`. Now switch to the fail-closed configuration and start the same way:

```bash
bash ../apply.sh fail-closed
env PATH=$HOME/nobwrap "$(command -v claude)"
```

**Expected result:** Claude Code refuses to start:

```
sandbox.failIfUnavailable is set, refusing to start without a working sandbox
```

`fail-closed` is the same configuration plus `"failIfUnavailable": true`. A quiet loss of protection becomes a loud stop.

---

## Step 7: Name what the sandbox does not cover

Write your answer in a notes file:

```bash
mkdir -p ~/work && nano ~/work/demo9-notes.md
```

Type one line, listing at least three things:

```
Not covered: <three things the sandbox does not limit>
```

Save with **Ctrl+O**, then **Enter**. Exit with **Ctrl+X**.

<details>
<summary>Show the answer</summary>

```
Not covered: hooks, MCP servers, plugin processes, and Claude's own file tools
```

The sandbox limits shell commands and their child processes. Hooks, MCP servers and plugin processes run outside it, so you must review them yourself. Claude's file tools are covered by permission rules, not by the sandbox.

</details>

---

## What you learned

- A sandbox still holds when a rule is missing or the model is persuaded. Test it with one command: `touch ~/sandbox-probe` must fail.
- Fail closed (`failIfUnavailable: true`) turns a silent loss of protection into a stop.
- The sandbox does not cover everything. Know what is outside it so you do not over-trust it.

## Cleanup

```bash
rm -rf ~/nobwrap ~/work/demo9-sandbox
```

If you ran `classroom-sandbox.sh --on` in Step 1, put the machine back:

```bash
bash $FILES/setup/classroom-sandbox.sh --off
```
