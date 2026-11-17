# AI Champions Training: Claude Code for Engineering Teams. Demos

**Course:** AI Champions Training: Claude Code for Engineering Teams (Governance, Hooks, Plugins, and Secure Environments), two days, ROI Training
**Contents:** 10 short demos you run yourself as mini-labs. Each takes 15 minutes or less and has a learning objective.

---

## About this guide

Each demo has the same layout: a learning objective, a time, a Files line, a short context paragraph, steps, an Expected result, and a Why this matters note.

In this guide `$FILES` means the `demo-files` folder. The managed settings file and the managed MCP file, which Demos 2 and 5 write, live here on the class machine:

| System | Managed settings file | Managed MCP file |
|---|---|---|
| Linux and WSL | `/etc/claude-code/managed-settings.json` | `/etc/claude-code/managed-mcp.json` |

Writing either needs root, so those steps use `sudo`.

Demos 1 to 10 use no organization-level administrative feature. Claude Code can word things differently each time, so check results against the Expected result and not against exact text. Demos that use a live model (1, 2, 3, 4, 6, 7, 8, 9) spend usage on your seat. Demos 5 and 10 need no model call to make their main point. Every person, company and value in the files is fictional, and every planted secret is a placeholder such as `FAKE-TOKEN-DO-NOT-USE`.

**Before the first demo:**

- `$FILES` is a shell variable you set yourself, in every terminal you use: `export FILES=~/champions/demo-files` (use your own path).
- Class seats start Claude Code in auto mode (the footer says `auto mode on`), so some steps that talk about approving a prompt show no prompt. Start with `claude --permission-mode default` when you want the prompts.
- The first `claude` start in a folder shows a trust dialog that defaults to `No, exit`. Press Down, then Enter. The Demo 2 folder also warns that it pre-approves `Bash(git push *)`.

> **Cleanup.** Demos 2 and 5 write a file as root. Run the matching remove script when you finish, and check with `claude mcp list` and `/status` that nothing is left on the machine.

---

## The demos

- **[Demo 1: Intake: One Use Case, One Tier](demo-1-intake-one-use-case-one-tier.md)**
- **[Demo 2: Who Wins? Managed Over Project](demo-2-who-wins-managed-over-project.md)**
- **[Demo 3: Rule Versus Request](demo-3-rule-versus-request.md)**
- **[Demo 4: Exit 1 Versus Exit 2](demo-4-exit-1-versus-exit-2.md)**
- **[Demo 5: A Fixed MCP Set](demo-5-a-fixed-mcp-set.md)**
- **[Demo 6: Prove It: A Logging Hook](demo-6-prove-it-a-logging-hook.md)**
- **[Demo 7: Install a Plugin From a Marketplace](demo-7-install-a-plugin-from-a-marketplace.md)**
- **[Demo 8: Evaluate a Plugin With a Test Suite](demo-8-evaluate-a-plugin-with-a-test-suite.md)**
- **[Demo 9: Block a Write and a Network Call](demo-9-block-a-write-and-a-network-call.md)**
- **[Demo 10: Find the Credential Smells](demo-10-find-the-credential-smells.md)**

---

**Related:** the [labs guide](../labs/README.md) holds the 6 labs for this course.
