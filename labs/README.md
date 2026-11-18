# AI Champions Training: Claude Code for Engineering Teams. Labs

**Course:** AI Champions Training: Claude Code for Engineering Teams (Governance, Hooks, Plugins, and Secure Environments), two days, ROI Training
**Contents:** Four timed hands-on labs and two take-home labs.

---

## About this guide

These labs give a goal, acceptance criteria and hints, not click-by-click steps. Each hides planted traps, and each is scored. You work alone, on your own Linux class machine, with your own Claude Code sign-in. You do not depend on another student, and no lab needs access to any organization or administrator console. Every score comes from a script you run on your own machine.

In this guide `$FILES` is the `demo-files` folder your instructor gives you. Everything runs on local files. Every name, company and value is fictional. Every planted secret is an obvious placeholder, such as `FAKE-TOKEN-DO-NOT-USE`. No file holds a real secret, and you must never put a real one in any lab file.

Claude Code can word things differently each time. Check your result against the acceptance criteria and not against exact text.

**Before Lab 1:** Linux with bash, Python 3.11 or later, `git` 2.31 or later, `jq`, and `claude` signed in with your own seat. Run `bash $FILES/setup/check_env.sh`. It lists anything missing and prints the install command. If `jq` is missing: `sudo apt-get install jq` (Debian and Ubuntu) or `sudo dnf install jq` (Fedora and RHEL). Lab 3 also needs `bubblewrap` and `socat`.

> **Class seats start in auto mode.** The footer of `claude` says `auto mode on`, so some prompts the labs describe do not appear. Where a lab records the permission mode (Lab 4), start with `claude --permission-mode default` and record `default`. `$FILES` is a shell variable you set yourself in each terminal, for example `export FILES=~/champions/demo-files`. The first `claude` start in a folder shows a trust dialog that defaults to `No, exit`: press Down, then Enter.

> **Usage cost.** Lab 2 (evals) and Lab 4 (live runs) use model requests on your seat. Each lab says where to cap them. Use the caps. Labs 1, 5 and 6 need almost no model use.

---

## The labs

- **[Lab 1: Rule to Control](lab-1-rule-to-control.md)**
- **[Lab 2: Build a Plugin With a Hook](lab-2-build-a-plugin-with-a-hook.md)**
- **[Lab 3: Harden a Sample Repository](lab-3-harden-a-sample-repository.md)**
- **[Lab 4: Prompt Injection Detection](lab-4-prompt-injection-detection.md)**
- **[Lab 5: Credential Audit (take-home)](lab-5-credential-audit-take-home.md)**
- **[Lab 6: Context Engineering (take-home)](lab-6-context-engineering-take-home.md)**

---

**Related:** the [demos guide](../demos/README.md) holds the 10 demos for this course.

