# Demo 7: Install a Plugin From a Marketplace

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Demos](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** Add a marketplace, review a plugin before trusting it, install it, and use its command and its hook. Time: about 10 minutes.

**Files:** `$FILES/demo7-marketplace/champions-tools` (a marketplace with one plugin, `branch-guard`). Review aid: `$FILES/templates/plugin-review.md`.

**Context:** A marketplace is a folder (or a git repository) with `.claude-plugin/marketplace.json`. `branch-guard` bundles a command and a PreToolUse hook that blocks force pushes and pushes to `main`. A plugin's hooks and servers run with the user's rights, outside the sandbox, so review before you install. Plugin components are namespaced `plugin:component`.

**Steps:**

1. Add the marketplace from the local folder: `claude plugin marketplace add $FILES/demo7-marketplace/champions-tools`, then `claude plugin marketplace list`. A team marketplace would come from a git repository instead (`owner/repo` or a git URL).
2. Review before you trust. Open `plugins/branch-guard/hooks/hooks.json` and `scripts/block_force_push.py`. Then list the contents: `claude --plugin-dir $FILES/demo7-marketplace/champions-tools/plugins/branch-guard plugin details branch-guard`. Read the component inventory and the projected token cost.
3. Install it for yourself only: `claude plugin install branch-guard -s local`.

   > **Create the Step 4 scratch repository first, and install from inside it.** `-s local` applies only in the folder you install from, so installing here and then moving to a new folder in Step 4 leaves the plugin unavailable — which is what happened on the class image. Either make the scratch repo before this step and run the install there, or use `-s user` so it follows you.
   >
   > **Give the scratch repo a `main` branch and a remote that can be reached. A local bare repo works.** One command builds it: `git init -q -b main ~/scratch7 && cd ~/scratch7 && git commit -q --allow-empty -m init && git init -q --bare ~/remote7.git && git remote add origin ~/remote7.git && git push -q origin main`. A dummy URL such as `https://example.invalid/x.git` does not work: measured 2026-11-17, Claude checks the remote first, finds it unreachable and declines to push, so the hook never runs and no `BRANCH-GUARD` text appears. Without a `main` branch or a remote at all, the model also declines (measured 2026-11-15).
4. In the scratch repository, start `claude`. Run `/reload-plugins` if the plugin does not show. Run `/branch-guard:branch-status`.
5. Ask: `Run git push --force origin main`. The hook blocks it, and the message starts with `BRANCH-GUARD`. To prove the rule without the model, exit and run `bash $FILES/demo7-marketplace/test_block.sh`: it feeds the hook four sample commands and prints the exit code for each (2 for a force push and for a push to `main`, 0 for a feature-branch push and for `git status`).
6. Uninstall and remove: `claude plugin uninstall branch-guard -s local` and `claude plugin marketplace remove champions-tools`, then `cd ~ && rm -rf ~/scratch7 ~/remote7.git`. **The scope flag is needed**: a bare `uninstall` assumes user scope and fails to find a local-scope install.

If the install or the live push does not work, load the plugin for one session with `claude --plugin-dir $FILES/demo7-marketplace/champions-tools/plugins/branch-guard` and run steps 4 and 5. If the live push still does not reach the hook, `bash $FILES/demo7-marketplace/test_block.sh` proves the rule without the model.

**Expected result:** The command reports the branch and the working tree state. The force push is blocked by the plugin's hook and Claude relays the reason.

**Why this matters:** A plugin is the unit a team ships and updates. It is also code with the user's rights. A marketplace gives one place to review, and the review must happen before the install, because the install is the trust decision.
