# demo-files: AI Champions Training, Claude Code for Engineering Teams

The files the labs use. ROI Training. `$FILES` in every lab means this folder. Everything is fictional, and every planted secret is a placeholder (`FAKE-TOKEN-DO-NOT-USE` and similar). Class machines are Linux with bash and Python 3.11.

Run `bash setup/check_env.sh` first. It checks Python, `jq`, `git`, `claude`, `bubblewrap`, `socat` and the AppArmor setting, changes nothing, and prints the install command for anything missing.

## Index

| Folder or file | Used by | What it holds |
|---|---|---|
| `setup/check_env.sh` | all labs | Linux environment check (reads only) |
| `setup/classroom-sandbox.sh` | Labs 2, 3 and 4 | Checks, switches on and switches off the machine's sandbox setting. Read Lab 3 Step 1 before you run `--on` |
| `templates/team-practices-charter.md` | Lab 1 | One-page charter with a status column (Enforced, Reviewed, Undecided) |
| `templates/plugin-review.md` | Lab 2 | Checklist for reviewing a plugin before trusting it |
| `tools/plugin_lint.py` | Lab 2 | Free local plugin checks (not a replacement for `claude plugin validate`) |
| `lab1-rule-to-control/` | Lab 1 | Rules, the `ledgerlite` project, a charter working copy, `check_lab1.py` |
| `lab2-plugin/` | Lab 2 | The `relnotes-starter` plugin with a six-case eval suite, a marketplace template, `score_lab2.py` |
| `lab3-harden/` | Lab 3 | The `report-archiver` project, `attack_simulation.py`, `check_settings.py` |
| `lab4-injection/` | Lab 4 | The `shipping-notes` project, four defense configurations, canary listener, injection scan, record sheet, `check_record.py` |
| `lab5-audit/` | Lab 5 | The `harbor-org` sample, findings template, `check_findings_format.py` |
| `lab6-context/` | Lab 6 | The `shopkit` project with a bloated `CLAUDE.md`, a plugin with long descriptions, the worksheet, `check_lab6.py` |

## Rules for these files

- Never put a real key, token or password in any file here.
- Nothing here needs access to any organization or administrator console. Every score comes from a script you run locally.
- Labs 2 and 4 use model requests on your own seat. Each says where to cap them.
