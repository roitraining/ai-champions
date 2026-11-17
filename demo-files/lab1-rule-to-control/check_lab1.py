#!/usr/bin/env python3
"""Local scorer for Lab 1 (Rule to Control). No model calls, no organization access.

Usage:  python3 check_lab1.py PROJECT_DIR CHARTER_FILE
        python3 check_lab1.py ledgerlite charter.md

Scores 100:
  Hook (40): wired to Bash with ${CLAUDE_PROJECT_DIR} (10), and six sample commands give the right exit code (30).
  Deny rules (15): a Read deny for .env (8) and for config/secrets.env (7).
  Log (10): a blocked command writes a line to the log named by CLAUDE_TOOL_LOG (the scorer sets it).
  Charter (35): at least 6 of 10 practice areas decided (20, partial credit below 6),
                every row marked Enforced names a control that really exists (15).

CHECKPOINT passes when the blocked-command test exits 2 AND the charter has at least 6 of 10 areas decided.
Standard library only.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

score = 0
out = []


def award(points, ok, label, hint=""):
    global score
    award_partial(points if ok else 0, points, label, hint)


def award_partial(got, points, label, hint=""):
    """Award `got` of `points`. Use this where the rubric promises partial credit."""
    global score
    score += got
    tag = "PASS" if got == points else ("PART" if got else "FAIL")
    out.append("[%s] %2d/%-2d %s%s" % (tag, got, points, label, ("  -> " + hint) if (hint and got < points) else ""))


def run_hook(script, command, cwd, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    payload = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run([sys.executable, str(script)], input=payload, capture_output=True, text=True, cwd=cwd, env=env, timeout=20)


def hook_entry(cfg):
    for g in (cfg.get("hooks") or {}).get("PreToolUse", []) or []:
        for h in g.get("hooks", []):
            if isinstance(h, dict) and ".py" in h.get("command", ""):
                return g.get("matcher", ""), h["command"]
    return None, None


def charter_rows(text):
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 6 and cells[0].isdigit():
            rows.append(cells)
    return rows


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    proj = Path(sys.argv[1]).resolve()
    charter = Path(sys.argv[2])
    try:
        cfg = json.loads((proj / ".claude" / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("Cannot read .claude/settings.json: %s" % exc)
        return 1

    # Hook (40)
    matcher, command = hook_entry(cfg)
    # A matcher of "*" fires for every tool, Bash included, so it satisfies "runs before
    # the Bash tool". Both ${CLAUDE_PROJECT_DIR} and $CLAUDE_PROJECT_DIR are valid shell
    # and both locate the script from the project rather than the current directory.
    matchers = [m.strip() for m in (matcher or "").split("|")]
    matches_bash = "Bash" in matchers or "*" in matchers
    uses_project_dir = bool(command) and "CLAUDE_PROJECT_DIR" in command
    wired = bool(command) and matches_bash and uses_project_dir
    award(10, wired, "A PreToolUse hook is wired to Bash and its command uses ${CLAUDE_PROJECT_DIR}",
          "matcher=%r command=%r" % (matcher, command))
    script = None
    if command:
        # quotes are shell syntax, not part of the path: "$CLAUDE_PROJECT_DIR"/x.py is the same script
        m = re.search(r"[\w./${}-]*\.py", command.replace('"', "").replace("'", ""))
        if m:
            raw = m.group(0).replace("${CLAUDE_PROJECT_DIR}", str(proj))
            raw = raw.replace("$CLAUDE_PROJECT_DIR", str(proj))
            p = Path(raw)
            script = p if p.is_absolute() else proj / p
    blocked_ok = False
    log_ok = False
    if script and script.exists():
        with tempfile.TemporaryDirectory() as d:
            logfile = Path(d, "tool.log")
            env = {"CLAUDE_TOOL_LOG": str(logfile)}
            cases = [
                ("git push origin main", 2, 8),
                ("rm -rf build", 2, 6),
                ("rm -fr build", 2, 3),
                ("cd src && git push", 2, 4),
                ("git status", 0, 5),
                ("python3 -m pytest -q", 0, 4),
            ]
            for cmd, want, pts in cases:
                r = run_hook(script, cmd, str(proj), env)
                award(pts, r.returncode == want, "Hook exits %d for: %s" % (want, cmd), "got exit %s" % r.returncode)
                if cmd == "git push origin main":
                    blocked_ok = r.returncode == 2
            log_ok = logfile.exists() and "block" in logfile.read_text(encoding="utf-8", errors="replace").lower()
    else:
        award(30, False, "The hook script exists and runs", "script path not found: %s" % script)
    award(10, log_ok, "A blocked command writes a line containing 'blocked' to the file named by CLAUDE_TOOL_LOG",
          "rule 3: log every block")

    # Deny rules (15)
    deny = (cfg.get("permissions") or {}).get("deny") or []
    reads = [d for d in deny if isinstance(d, str) and d.startswith("Read(")]
    award(8, any(re.fullmatch(r"Read\((\./)?(\*\*/)?\.env(\.\*)?\)", d) for d in reads), "A Read deny rule covers .env", "deny=%r" % deny)
    award(7, any("secrets.env" in d or "config/**" in d or "secrets" in d for d in reads), "A Read deny rule covers config/secrets.env", "deny=%r" % deny)

    # Charter (35)
    text = charter.read_text(encoding="utf-8") if charter.exists() else ""
    rows = charter_rows(text)
    decided = [r for r in rows if r[3].lower() in ("enforced", "reviewed") and r[2]]
    n = len(decided)
    # The rubric promises partial credit below 6, so pay it rather than scoring zero.
    award_partial(20 if n >= 6 else int(20 * n / 6), 20,
                  "Charter: %d of %d areas decided (need at least 6 for full marks)" % (n, len(rows)),
                  "each decided area is worth about 3 points until you reach 6")
    settings_text = json.dumps(cfg)
    bad = []
    for r in rows:
        if r[3].lower() != "enforced":
            continue
        control = r[4]
        only_claude_md = control.strip().lower() in ("claude.md", "`claude.md`") or (control and re.fullmatch(r"[`\s]*CLAUDE\.md[`\s]*", control, re.I) is not None)
        refs = re.findall(r"`?([\w./-]+\.\w+|permissions\.deny|sandbox[\w.]*|hooks)`?", control)
        exists = False
        for ref in refs:
            if ref.lower() == "claude.md":
                continue
            if (proj / ref).exists() or ref in ("permissions.deny", "hooks") and ref.split(".")[0] in cfg or ref.startswith("sandbox") and "sandbox" in cfg or ref in settings_text:
                exists = True
        if not control or only_claude_md or not exists:
            bad.append("row %s (%s): control %r is not a file or setting that exists" % (r[0], r[1], control))
    # With no Enforced rows at all this check passes vacuously, so an untouched charter
    # used to collect the full 15. You have just built a hook and two deny rules in this
    # lab; at least one row should be able to point at them.
    enforced_rows = [r for r in rows if r[3].lower() == "enforced"]
    award(15, bool(rows) and bool(enforced_rows) and not bad,
          "Every Enforced row names a control that exists (CLAUDE.md is a request, not a control)",
          "no row is marked Enforced - name the hook or the deny rules you just built"
          if rows and not enforced_rows else "")
    for b in bad:
        out.append("        " + b)

    print("LAB 1 SCORE")
    print("\n".join(out))
    print("\nTOTAL: %d / 100" % score)
    cp = blocked_ok and n >= 6
    print("CHECKPOINT: %s (blocked-command test exits 2: %s; charter decided %d of 10, need 6)" % ("PASS" if cp else "NOT YET", "yes" if blocked_ok else "no", n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
