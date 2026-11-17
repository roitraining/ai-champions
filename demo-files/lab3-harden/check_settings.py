#!/usr/bin/env python3
"""Static settings checker for Lab 3. Works on any machine: it reads files and runs nothing.

Usage:  python3 check_settings.py PATH_TO_PROJECT      (for example ~/work/report-archiver)
Reads PATH_TO_PROJECT/.claude/settings.json, .mcp.json, app.py and any script a hook names.

Scores 60 points (Part A). Part B is the live attack script (40 points, attack_simulation.py).
It also prints the attack outcomes the configuration PREDICTS. A prediction is not an observation:
only the live script run inside a Claude Code session, with the sandbox active, shows what really happens.

Path entries are judged by where they resolve, not by how they are spelled: `~`, `$HOME`,
`${CLAUDE_PROJECT_DIR}` and a trailing `*` or `**` are expanded first, then compared with
PATH_TO_PROJECT. So `.`, `./`, `~/work/report-archiver` and the absolute path of the project
you are checking all count as the project folder, and `~`, `/`, `..` and `/home/you` do not.
Point PATH_TO_PROJECT at the project the settings file belongs to, or the comparison is meaningless.

Hook scripts are judged on the code that would run, not on the words in the file. Comments and
Python docstrings are blanked before the network pattern is applied, so prose such as "append all
tool requests to a local audit file" is not read as a network call. Commenting the sending lines
out is therefore accepted as "does not reach the network" - it does not - but a hook left pointing
at a script with no code left to run fails this checklist anyway, for the same reason as a hook
pointing at a deleted script: the fix the lab asks for is removing the hook entry, and an entry
aimed at a file with nothing in it is the same unreviewed entry wearing a different hat. Code the
file does not show - exec() or eval() of a string - fails too, because the checker cannot review it.

Unconfirmed items (not in the class facts file, so treated as scenario conventions):
  - The exact entry format for sandbox.excludedCommands. This checker passes it when the list is empty or absent.
  - How a relative path in sandbox.filesystem is resolved. This checker resolves relative entries
    against PATH_TO_PROJECT, and also accepts a denyRead entry that merely names "secrets".
Standard library only.
"""
import io
import json
import os
import re
import sys
import tokenize

APPROVED_DOMAINS = {"pypi.org", "files.pythonhosted.org"}
APPROVED_SERVERS = {"docs-search", "ticket-bridge"}
BROAD_WRITE = {"~", "/", "*", "..", "../", "$home", "${home}", "%userprofile%", "~/", "**", "/*", ""}
NETWORK_WORDS = re.compile(r"urllib|requests|http\.client|socket|curl|wget|urlopen")
# exec("...") / eval("...") / compile("..."): code built at run time, which no reader of the
# file can review. "re.compile(" and "literal_eval(" are not matched (a name part precedes them).
RUNTIME_CODE = re.compile(r"(?<![\w.])(?:exec|eval|compile)\s*\(")
SCRIPT_EXTS = (".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".rb", ".pl", ".ps1")
# attack_simulation.py attempt 2 connects here by default (--net-target changes it).
NET_TARGET = "example.com"


def low(s):
    return str(s).strip().lower()


def find(obj, key):
    """Return the first value for key anywhere inside obj, else None."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find(v, key)
            if r is not None:
                return r
    return None


def flat(items):
    return [low(x) for x in (items or []) if isinstance(x, str)]


def raw(items):
    return [x.strip() for x in (items or []) if isinstance(x, str)]


def norm(path):
    return os.path.normcase(os.path.normpath(os.path.abspath(path)))


def resolve(entry, root_abs):
    """Resolve a settings path entry to an absolute path.

    Expands ~, $VAR and ${CLAUDE_PROJECT_DIR}, drops trailing glob segments (./reports/** ->
    ./reports) and resolves a relative entry against root. Returns None when the entry names no
    place at all ("*", "") or still holds a variable this machine cannot expand.
    """
    s = str(entry).strip().strip('"').strip("'")
    s = s.replace("${CLAUDE_PROJECT_DIR}", root_abs).replace("$CLAUDE_PROJECT_DIR", root_abs)
    s = os.path.expandvars(s)
    s = os.path.expanduser(s)
    if "$" in s or "%" in s:
        return None  # an unexpanded variable: this checker cannot say where it points
    parts = re.split(r"[/\\]", s)
    while parts and "*" in parts[-1]:
        parts.pop()
    s = "/".join(parts)
    if not s.strip("/\\ "):
        return None
    if not os.path.isabs(s):
        s = os.path.join(root_abs, s)
    return norm(s)


def inside(path, base):
    """True when path is base itself or sits under base."""
    if not path or not base:
        return False
    return path == base or path.startswith(base.rstrip("/\\") + os.sep)


def code_text(path):
    """File text with comments, and Python docstrings, blanked out so prose cannot trip a match.

    Character positions are preserved, so code reads exactly as written: only the characters
    inside a comment or a triple-quoted string are replaced with spaces.
    """
    with open(path, encoding="utf-8", errors="replace") as f:
        src = f.read()
    if not path.lower().endswith(".py"):
        return re.sub(r"(?m)^\s*#.*$", "", src)
    spans = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            quoted = tok.type == tokenize.STRING and tok.string.lstrip("rbfuRBFU")[:3] in ('"""', "'''")
            if tok.type == tokenize.COMMENT or quoted:
                spans.append((tok.start, tok.end))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        return src
    lines = [list(line) for line in src.splitlines(True)]
    for (srow, scol), (erow, ecol) in spans:
        for row in range(srow, erow + 1):
            if not 1 <= row <= len(lines):
                continue
            chars = lines[row - 1]
            start = scol if row == srow else 0
            end = ecol if row == erow else len(chars)
            for i in range(start, min(end, len(chars))):
                if chars[i] != "\n":
                    chars[i] = " "
    return "".join("".join(chars) for chars in lines)


def hook_commands(cfg):
    out = []
    for groups in (cfg.get("hooks") or {}).values():
        for g in groups if isinstance(groups, list) else []:
            for h in g.get("hooks", []):
                if isinstance(h, dict) and h.get("command"):
                    out.append(h["command"])
    return out


def deny_parts(entry):
    """'read(./.env.*)' -> ('read', './.env.*'). Entries without parentheses keep an empty pattern."""
    m = re.match(r"^([a-z_]+)\s*\((.*)\)\s*$", entry.strip())
    if m:
        return m.group(1), m.group(2).strip()
    return entry.strip(), ""


def base_name(pattern):
    return re.split(r"[/\\]", pattern.strip().strip('"').strip("'"))[-1]


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    root = sys.argv[1]
    root_abs = norm(root)
    try:
        with open(os.path.join(root, ".claude", "settings.json"), encoding="utf-8") as f:
            cfg = json.load(f)
    except (OSError, ValueError) as exc:
        print("Cannot read .claude/settings.json: %s" % exc)
        sys.exit(1)
    sb = cfg.get("sandbox", {}) if isinstance(cfg.get("sandbox"), dict) else {}
    perms = cfg.get("permissions", {}) if isinstance(cfg.get("permissions"), dict) else {}
    deny = flat(perms.get("deny"))
    allow = flat(perms.get("allow"))
    rows = []

    def check(label, pts, ok, detail):
        rows.append((label, pts, pts if ok else 0, detail))

    # Four rows pass when something is absent (no excluded commands, no broad write path,
    # no blanket allow, no hook that reaches the network). A blank file has nothing to
    # inspect and used to earn 24 of 60 for them. They count only once the file configures
    # the sandbox or the permissions at all.
    engaged = bool(sb) or bool(perms)
    nothing = "" if engaged else " (nothing is configured yet: no sandbox or permissions settings)"

    enabled = sb.get("enabled") is True
    check("sandbox.enabled is true", 7, enabled, "sandbox.enabled = %r" % sb.get("enabled"))
    check("sandbox.failIfUnavailable is true", 7, sb.get("failIfUnavailable") is True,
          "failIfUnavailable = %r (the default is to run WITHOUT a sandbox when it cannot start)" % sb.get("failIfUnavailable"))
    excl = sb.get("excludedCommands")
    check("sandbox.excludedCommands is empty or absent (nothing runs outside the sandbox on purpose)", 5, engaged and not excl,
          "excludedCommands = %r (those commands run outside the sandbox)%s" % (excl, nothing))

    domains = find(sb, "allowedDomains")
    dl = flat(domains)
    bad = [d for d in dl if d not in APPROVED_DOMAINS]
    check("network.allowedDomains is a non-empty list of approved domains only", 7,
          bool(dl) and not bad,
          "allowedDomains = %r; not on the approved list %r: %r" % (domains, sorted(APPROVED_DOMAINS), bad))
    # A wildcard of any shape ("*", "*.com", "*.example.com") defeats the list.
    permissive = [d for d in dl if "*" in d or d == NET_TARGET]

    aw = find(sb, "allowWrite")
    awl = raw(aw)
    broad = []
    for entry in awl:
        if low(entry) in BROAD_WRITE:
            broad.append(entry)
            continue
        target = resolve(entry, root_abs)
        if target is None or not inside(target, root_abs):
            broad.append(entry)
    check("filesystem.allowWrite stays inside the project folder", 5, engaged and not broad,
          "allowWrite = %r; these do not resolve inside the project you are checking (%s): %r. "
          "Name the project folder itself (\".\" is simplest, or its absolute path, or "
          "~/work/report-archiver); home, \"/\", \"..\" and any folder above the project are too broad.%s"
          % (aw, root, broad, nothing))

    dr = raw(find(sb, "denyRead"))
    drl = [low(x) for x in dr]
    secrets_abs = norm(os.path.join(root, "config", "secrets.env"))

    def covers_secrets(entry):
        """True when the entry denies the secrets file directly or as part of a folder inside the project."""
        target = resolve(entry, root_abs)
        if target is None or target == root_abs or not inside(target, root_abs):
            return False  # outside the project, or the whole project (which stops the tool working)
        return inside(secrets_abs, target)

    sec = any("secrets" in x for x in drl) or any(covers_secrets(x) for x in dr)
    ssh = any(".ssh" in x for x in drl)
    check("sandbox filesystem.denyRead covers the secrets file and ~/.ssh (this covers shell commands)", 5, sec and ssh,
          "denyRead = %r (secrets file: %s, ssh: %s). Deny the secrets file itself (./config/secrets.env) "
          "or the folder holding it (./config), plus ~/.ssh." % (dr, sec, ssh))
    dw = flat(find(sb, "denyWrite"))
    check("filesystem.denyWrite protects .claude and .mcp.json", 3,
          any(".claude" in x for x in dw) and any(".mcp.json" in x for x in dw), "denyWrite = %r" % dw)

    read_denies = [deny_parts(x)[1] for x in deny if deny_parts(x)[0] == "read"]
    deny_secrets = any("secrets" in p for p in read_denies)
    deny_dotenv = any(base_name(p).startswith(".env") for p in read_denies)
    check("permissions.deny has Read rules for the secrets file and .env (this covers Claude's file tools)", 4,
          deny_secrets and deny_dotenv,
          "deny = %r (secrets file: %s, .env: %s). \".env\" has to be its own rule: a rule for "
          "secrets.env does not cover it. Add Read(./.env) and Read(./.env.*)." % (deny, deny_secrets, deny_dotenv))
    check("permissions.deny blocks curl and wget", 3,
          any("curl" in x for x in deny) and any("wget" in x for x in deny), "deny = %r" % deny)
    blanket = [x for x in allow if x in ("bash", "bash(*)", "bash(*:*)", "*")]
    check("permissions.allow has no blanket Bash allow", 4, engaged and not blanket, "blanket allow rules: %r%s" % (blanket, nothing))

    try:
        with open(os.path.join(root, ".mcp.json"), encoding="utf-8") as f:
            declared = set(json.load(f).get("mcpServers", {}).keys())
    except (OSError, ValueError):
        declared = set()
    check("MCP: .mcp.json declares only approved servers (docs-search, ticket-bridge)", 6,
          bool(declared) and declared <= APPROVED_SERVERS,
          "declared in .mcp.json = %r; not approved: %r" % (sorted(declared), sorted(declared - APPROVED_SERVERS)))

    net_hooks = []
    unreadable = []
    unreviewable = []
    inert = []
    for cmd in hook_commands(cfg):
        if NETWORK_WORDS.search(cmd):
            net_hooks.append("the hook command itself: %s" % cmd.strip())
        elif RUNTIME_CODE.search(cmd):
            unreviewable.append("the hook command itself: %s" % cmd.strip())
        for token in re.findall(r'"[^"]*"|\'[^\']*\'|\S+', cmd):
            token = token.strip('"').strip("'")
            if not token or token.startswith("-") or token.startswith(">"):
                continue
            is_script = token.lower().endswith(SCRIPT_EXTS)
            path = resolve(token, root_abs)
            if not is_script:
                # follow an extensionless script only when it really is a file in the project
                if path is None or not inside(path, root_abs) or not os.path.isfile(path) or "/" not in token.replace("\\", "/"):
                    continue
            if path is None or not os.path.isfile(path):
                unreadable.append(token)
                continue
            try:
                body = code_text(path)
            except OSError:
                unreadable.append(token)
                continue
            if NETWORK_WORDS.search(body):
                net_hooks.append(token)
            elif not is_script:
                # a data file the command happens to name (a log, a template): read for network
                # calls, but "no code in it" and "builds code at run time" say nothing about it
                continue
            elif RUNTIME_CODE.search(body):
                unreviewable.append(token)
            elif not body.strip():
                inert.append(token)
    hook_detail = []
    if net_hooks:
        hook_detail.append("network calls in: %r" % net_hooks)
    if unreadable:
        hook_detail.append("cannot read the script this hook runs: %r - if the script is gone, remove "
                           "the hook entry too; if it is still wanted, restore it so it can be reviewed" % unreadable)
    if inert:
        hook_detail.append("the script this hook runs has no code left to run: %r - commenting the body "
                           "out leaves the hook entry behind, pointing at a file nobody has a reason to "
                           "keep; remove the hook entry as well" % inert)
    if unreviewable:
        hook_detail.append("this hook builds its code at run time (exec/eval), so what it does cannot be "
                           "read from the file: %r - write the code out in the open or remove the hook "
                           "entry" % unreviewable)
    check("hooks: no hook reaches the network, and every hook that stays runs a script that can be read "
          "and reviewed (hooks run OUTSIDE the sandbox)", 4,
          engaged and not net_hooks and not unreadable and not inert and not unreviewable, "; ".join(hook_detail) + nothing)

    total = 0
    print("PART A: static checklist")
    for label, pts, got, detail in rows:
        total += got
        print("  [%s] %2d/%-2d %s" % ("PASS" if got else "FAIL", got, pts, label))
        if not got:
            print("            %s" % detail)
    print("  PART A SCORE: %d / 60\n" % total)

    if not enabled:
        why = "will succeed: the sandbox is off"
        write_why = read_why = net_why = why
    else:
        write_why = ("blocked if the sandbox starts" if not broad
                     else "will succeed: allowWrite reaches outside the project (%r)" % broad)
        read_why = ("blocked if the sandbox starts" if sec
                    else "will succeed: denyRead does not cover config/secrets.env")
        if not dl:
            net_why = "will succeed: there is no allowedDomains list to limit the connection"
        elif permissive:
            net_why = "will succeed: %r in allowedDomains still permits %s" % (permissive, NET_TARGET)
        else:
            net_why = "blocked if the sandbox starts"
    if excl and enabled:
        # The attack script is run as `python3 attack_simulation.py` from the Bash tool, so anything
        # excluded from the sandbox can put the script itself outside it.
        write_why = read_why = net_why = "not blocked: a command is excluded from the sandbox (note below)"
    try:
        app_src = code_text(os.path.join(root, "app.py"))
    except OSError:
        app_src = None
    if app_src is None:
        inject_why = "will succeed: app.py could not be read, so the injection cannot be ruled out"
    elif re.search(r"os\s*\.\s*system\s*\(|shell\s*=\s*True", app_src):
        if "shlex.quote" in app_src or "shlex.join" in app_src:
            inject_why = ("unclear: app.py still hands the name to a shell but quotes it with shlex. "
                          "Attempt 4 is scored live - run the attack script and record what happens")
        else:
            inject_why = ("will succeed: app.py still builds a shell command, and a sandbox does not "
                          "stop a command inside the working directory")
    elif RUNTIME_CODE.search(app_src):
        inject_why = ("unclear: app.py builds its code at run time (exec/eval), so this checker cannot "
                      "see what reaches a shell. Attempt 4 is scored live - run the attack script and "
                      "record what happens")
    else:
        inject_why = "no shell command built from the name found in app.py"
    print("PREDICTED attack outcomes (a prediction, not an observation)")
    print("  1 write outside the working directory : %s" % write_why)
    print("  2 disallowed destination              : %s" % net_why)
    print("  3 read the secrets file from a script : %s" % read_why)
    print("  4 command injection in app.py         : %s" % inject_why)
    if excl:
        print("  excludedCommands = %r. The attack script is run as `python3 attack_simulation.py`," % excl)
        print("  so a command excluded from the sandbox can leave the script itself unsandboxed, and")
        print("  attempts 1 to 3 cannot be counted as blocked. Empty the list and run this again.")
    print("  Hook scripts and MCP servers are not limited by the sandbox, so the checklist reads them instead.")


if __name__ == "__main__":
    main()
