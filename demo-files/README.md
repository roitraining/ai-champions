# demo-files: AI Champions Training, Claude Code for Engineering Teams

The files the labs and demos use. ROI Training. `$FILES` in every lab means this folder. Everything is fictional, and every planted secret is a placeholder (`FAKE-TOKEN-DO-NOT-USE` and similar). Class machines are Linux with bash and Python 3.11.

Run `bash setup/check_env.sh` first. It checks Python, `jq`, `git`, `claude`, `bubblewrap`, `socat` and the AppArmor setting, changes nothing, and prints the install command for anything missing.

## Index

| Folder or file | Used by | What it holds |
|---|---|---|
| `setup/check_env.sh` | all labs | Linux environment check (reads only) |
| `setup/classroom-sandbox.sh` | Labs 2, 3 and 4, Demos 3 and 9 | Checks, switches on and switches off the machine's sandbox setting. Run `--check` first: on some machines nothing needs switching on. Read Lab 3 Step 1 before you run `--on` |
| `templates/intake-checklist.md` | Demo 1 | Generic ten-section intake checklist (a team replaces it with its own) |
| `templates/risk-tiers.md` | Demo 1 | Generic three-tier example |
| `templates/mcp-server-review.md` | Demo 5 | Checklist for reviewing an MCP server before adding it |
| `templates/team-practices-charter.md` | Lab 1 | One-page charter with a status column (Enforced, Reviewed, Undecided) |
| `templates/plugin-review.md` | Demo 7, Lab 2 | Checklist for reviewing a plugin before trusting it |
| `tools/plugin_lint.py` | Demo 8, Lab 2 | Free local plugin checks (not a replacement for `claude plugin validate`) |
| `demo1-intake/` | Demo 1 | Fictional use case brief |
| `demo2-managed/` | Demo 2 | Managed settings file, a conflicting project file, install and remove scripts |
| `demo3-rule-vs-request/` | Demo 3 | Sample project, four configurations (request only, Read deny, deny plus sandbox, bypass-mode test), `apply_config.sh` |
| `demo4-exit-codes/` | Demo 4 | A hook that exits 1 and the fixed version that exits 2, a no-model test script |
| `demo5-mcp/` | Demo 5 | Two local MCP servers (approved and unapproved), a managed MCP file installer, a test script |
| `demo6-logging/` | Demo 6 | Block-and-log hook, tool-call logger (shell and Python versions), log summaries, a sample log |
| `demo7-marketplace/champions-tools/` | Demos 7 and 8 | A marketplace with one plugin, `branch-guard`, that has a hook, a command and an eval suite |
| `demo9-sandbox/` | Demo 9 | Sandbox configurations and a harmless probe script |
| `demo10-credential-smells/` | Demo 10 | A small project with planted credential smells and a scanner |
| `lab1-rule-to-control/` | Lab 1 | Rules, the `ledgerlite` project, a charter working copy, `check_lab1.py` |
| `lab2-plugin/` | Lab 2 | The `relnotes-starter` plugin with a six-case eval suite, a marketplace template, `score_lab2.py` |
| `lab3-harden/` | Lab 3 | The `report-archiver` project, `attack_simulation.py`, `check_settings.py` |
| `lab4-injection/` | Lab 4 | The `shipping-notes` project, four defense configurations, canary listener, injection scan, record sheet, `check_record.py` |
| `lab5-audit/` | Lab 5 | The `harbor-org` sample, findings template, `check_findings_format.py` |
| `lab6-context/` | Lab 6 | The `shopkit` project with a bloated `CLAUDE.md`, a plugin with long descriptions, the worksheet, `check_lab6.py` |

## Rules for these files

- Never put a real key, token or password in any file here.
- Nothing here needs access to any organization or administrator console. Every score comes from a script you run locally.
- Scripts that write to a system path (`/etc/claude-code/`) need root and have a matching remove script. Run the remove script when you finish.
- Labs 2 and 4 and most demos use model requests on your own seat. Each says where to cap them.
