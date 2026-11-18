# Demo 2: Who Wins? Managed Over Project

**Course:** AI Champions Training: Claude Code for Engineering Teams

> Part of **[AI Champions Training: Demos](README.md)**. `$FILES` is the `demo-files` folder your instructor gives you. Read the [guide preamble](README.md) for prerequisites and cost notes before you start.

---

**Learning objective:** See that a managed settings file beats a project settings file, and prove it with behavior, not with a screen that lists files. Time: about 12 minutes.

**Files:** `$FILES/demo2-managed`: `managed-settings.json`, `project/.claude/settings.json`, `install-managed.sh`, `remove-managed.sh`, `install-managed.ps1`, `remove-managed.ps1`.

**Context:** The project file asks for a small model and allows `git push`. The managed file pins a different model and denies `git push` and reading `.env`. The overall order, highest first, is managed settings, command line, project local, shared project, user. A managed file is read at startup and reloaded when it changes.

**Steps:**

1. Open the two files side by side. Compare `model` and `permissions` in each.
2. Prepare the project: `cd $FILES/demo2-managed/project && git init -q && git commit -q --allow-empty -m init`.
3. Before installing the managed file, start `claude` in `project`. Run `/status` and note the `Setting sources` line, then `/model` to see the model in use. It should be the project's choice. Exit.
4. Install the managed file: `sudo bash ../install-managed.sh`.
5. Start `claude` in `project` again. Run `/status`. The `Setting sources` line now lists the managed settings file (its label ends in `(file)`). Run `/model`: it should show the pinned model.
6. Ask: `Run git push origin main`. Claude Code should refuse, even though the project settings allow it.
7. Ask: `Show me the contents of .env`. The Read tool should be denied.
8. Note what `/status` proves and what it does not: it lists the files that were read, not which file supplied each key. The behavior in steps 5 to 7 is the proof.
9. Remove the managed file with `sudo bash ../remove-managed.sh`, then exit.

**Expected result:** With the managed file in place, the model matches the managed file and `git push` is refused despite the project's allow rule. After removal, the project's choices apply again.

**Why this matters:** A rule that a project can override is a default, not a control. Managed settings are the one place a team can set a floor that a developer's own settings cannot lower.
