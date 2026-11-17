# Setup: before Lab 1

About 10 minutes. You need a Linux machine, a terminal, and your own Claude Code
sign-in. Nothing in this course needs an organization, an administrator console, or a
shared account.

---

## 1. Run the environment check first

```bash
bash $FILES/setup/check_env.sh
```

It reads your machine and changes nothing. It lists anything missing and prints the
install command for it. Fix what it reports, then run it again until it exits clean.

What the labs need:

| Requirement | Needed by |
|---|---|
| Linux with `bash` | all labs |
| Python 3.11 or later | every scoring script |
| `git` 2.31 or later | Labs 1, 2 and 6 |
| `jq` | the logging work in Lab 1 |
| `bubblewrap` and `socat` | Lab 3's sandbox, and Lab 4's sandbox configuration |
| `claude`, signed in | Labs 2, 3 and 4 |

If `jq` is missing: `sudo apt-get install jq` on Debian and Ubuntu, or
`sudo dnf install jq` on Fedora and RHEL.

## 2. Check whether Claude Code is already installed

**On a classroom machine it usually is. Check before you install anything:**

```bash
claude --version
which claude
```

If that prints a version, **you are done with this section** — go to step 3 and sign in.

A classroom image generally installs Claude Code from the apt package, so `which claude`
says `/usr/bin/claude`, **not** `~/.local/bin/claude`. That directory does not exist on
such a machine and nothing is wrong if it is missing.

Running the installer on top of an existing install leaves two copies on the machine and
a `PATH` that decides which one you get. Do not do it.

On your own machine, or where `claude --version` printed nothing:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Then follow the `PATH` instruction the installer prints. The native installer puts the
launcher at `~/.local/bin/claude`, which is why that is the directory you add:

```bash
grep -q '.local/bin' ~/.bashrc || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Use `~/.zshrc` instead if your shell is zsh — check with `echo $SHELL`.

## 3. Sign in

```bash
claude
```

It opens a browser on first launch. If the browser does not open, press `c` to copy the
login URL and paste it into one yourself. Confirm with:

```bash
claude auth status
```

**Sign in with your own seat.** Everything in this course is scored on your own machine,
so you never need anyone else's account.

## 4. One thing that will cost you money if you skip it

If `ANTHROPIC_API_KEY` is set in your shell, Claude Code uses it **in preference to your
sign-in**, and the labs bill against that key instead of your seat. Check:

```bash
echo $ANTHROPIC_API_KEY
```

If it prints anything, run `unset ANTHROPIC_API_KEY` in the shell you use for the labs,
or open a new terminal.

---

## Usage cost

Labs 2 and 4 spend model requests on your seat, and each says where to cap them. **Use
the caps.** Labs 1, 5 and 6 need almost no model use, and Lab 3's scoring is a static
checker that costs nothing.

## If something will not work

Each lab has a **Common problems** section listing what actually goes wrong in that lab
and what it looks like. Check there first — most failures in these labs are a wrong exit
code, a relative path, or a typo in a deny rule, and the lab tells you which.
