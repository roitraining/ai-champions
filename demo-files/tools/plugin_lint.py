#!/usr/bin/env python3
"""Cheap local checks for a Claude Code plugin, to run before you spend credits on an eval.

Usage:
    python plugin_lint.py PLUGIN_DIR [--marketplace MARKETPLACE_DIR]

This does NOT replace `claude plugin validate`, and it does not test behavior (that is
what `claude plugin eval` is for). It checks the traps the plugin lab plants: a hook that does
not use the plugin path variable, a checking subagent with more tools than it needs, a
manifest name that does not match the marketplace entry, a command left as TODO, and
descriptions that sit in the context window on every turn. Agent fields and a root
CLAUDE.md are reported as WARN only, because the class facts do not confirm how a plugin
treats them.

Exit code 0 when there are no FAIL lines, 1 otherwise.
"""
import json
import re
import sys
from pathlib import Path

MAX_DESCRIPTION = 300          # lab rule of thumb, not a product limit
IGNORED_AGENT_FIELDS = ("permissionMode", "hooks", "mcpServers", "initialPrompt")   # UNCONFIRMED in the class facts: reported as WARN only
WRITE_TOOLS = {"Edit", "Write", "Bash", "NotebookEdit"}
# ${CLAUDE_PLUGIN_ROOT} and $CLAUDE_PLUGIN_ROOT expand the same way, so both are accepted.
PLUGIN_ROOT_VAR = r"\$\{?CLAUDE_PLUGIN_ROOT\}?"
# A TODO the author left behind, not a mention of the word: the hook script lints
# RELEASE_NOTES.md for TODO, so a command that documents that rule is not a defect.
TODO_MARKER = re.compile(
    r"(?mi)^\s{0,8}(?:[-*+>]\s*|#{1,6}\s*)?TODO\b\s*[:\-]"
    r"|TODO:\s"
    r"|\bTODO\b[^\n]{0,30}\b(?:write|fill in|finish|complete)\b"
)
BLOCK_SCALAR = re.compile(r"^[|>][+-]?\d*$")
PLACEHOLDER_NAME = re.compile(r"(?i)^(your name|yourname|name here|firstname lastname|todo|tbd|placeholder)$")
results = []


def out(level, msg):
    results.append(level)
    print(f"[{level:<4}] {msg}")


def placeholder_person(block):
    """True when an author/owner field still holds the template's placeholder name."""
    value = block.get("name") if isinstance(block, dict) else block
    return bool(PLACEHOLDER_NAME.match(str(value or "").strip()))


def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def parse_frontmatter(block):
    """Small YAML-mapping reader: scalars, quoted scalars, folded/literal blocks, and lists.

    A list (block `- item` lines, or inline `[a, b]`) and a folded `>-` block come back as a
    joined string, so `tools: [Read, Grep]`, a block list and `tools: Read, Grep` read alike,
    and a folded description is not mistaken for a two-character one.
    """
    fields = {}
    src = block.splitlines()
    i = 0
    while i < len(src):
        ln = src[i]
        i += 1
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if ln.startswith((" ", "\t", "-")) or ":" not in ln:
            continue
        key, val = ln.split(":", 1)
        key, val = key.strip(), val.strip()
        items, cont = [], []
        while i < len(src) and (not src[i].strip() or src[i].startswith((" ", "\t", "-"))):
            nxt = src[i].strip()
            i += 1
            if not nxt:
                continue
            if nxt.startswith("- "):
                items.append(_unquote(nxt[2:]))
            elif nxt != "-":
                cont.append(nxt)
        if val.startswith("[") and val.endswith("]"):
            val = ", ".join(_unquote(part) for part in val[1:-1].split(",") if part.strip())
        elif items and (not val or BLOCK_SCALAR.match(val)):
            val = ", ".join(items)
        elif cont and (not val or BLOCK_SCALAR.match(val)):
            val = " ".join(cont)
        fields[key] = _unquote(val)
    return fields


def frontmatter(path):
    text = Path(path).read_text(encoding="utf-8")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n", text, re.S)
    return (parse_frontmatter(m.group(1)) if m else {}), bool(m)


def fires_after_write(event, matcher):
    """True when a hook wired like this runs after Claude writes a file.

    The matcher is a regex matched against the tool name, so this asks the runtime's
    question instead of looking for a spelling. Kept identical to score_lab2.py.
    """
    if event != "PostToolUse":
        return False
    pat = (matcher or "").strip()
    if not pat or pat == "*":
        return True
    try:
        return any(re.search(pat, t) for t in ("Write", "Edit", "MultiEdit"))
    except re.error:
        return bool(re.search(r"Write|Edit", pat))


def main(argv):
    mk = None
    rest = list(argv)
    if "--marketplace" in rest:
        i = rest.index("--marketplace")
        mk = Path(rest[i + 1])
        del rest[i:i + 2]
    args = [a for a in rest if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    root = Path(args[0])
    manifest_path = root / ".claude-plugin" / "plugin.json"
    name = None
    manifest = {}
    if not manifest_path.exists():
        out("FAIL", "No .claude-plugin/plugin.json")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            name = manifest.get("name")
        except json.JSONDecodeError as exc:
            out("FAIL", f"plugin.json is not valid JSON: {exc}")
        if placeholder_person(manifest.get("author")):
            out("WARN", "plugin.json still names the template author. Put the owner of the plugin in `author`, so a team can tell who to ask about it.")
        if name:
            out("ok", f"Manifest name is '{name}'")
        elif manifest_path.exists():
            out("FAIL", "plugin.json has no name")

    # hooks
    hooks_file = root / "hooks" / "hooks.json"
    if hooks_file.exists():
        text = hooks_file.read_text(encoding="utf-8")
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            data = {}
            out("FAIL", f"hooks/hooks.json is not valid JSON: {exc}")
        clean = True
        if re.search(r"[A-Za-z]:[\\/]|/(home|Users)/", text):
            clean = False
            out("FAIL", "hooks/hooks.json contains a fixed absolute path. Use ${CLAUDE_PLUGIN_ROOT}.")
        wired = [(ev, grp.get("matcher", ""), h.get("command", ""))
                 for ev, groups in (data.get("hooks") or {}).items()
                 for grp in groups for h in grp.get("hooks", [])]
        commands = [c for _, _, c in wired]
        if commands and not any(fires_after_write(ev, ma) for ev, ma, _ in wired):
            clean = False
            out("FAIL", "No hook runs after a write. A format checker for a file Claude just wrote belongs on "
                        "PostToolUse with no matcher or a matcher that matches Write and Edit; score_lab2.py gives "
                        "the wiring and behavior points only to a hook on that event. Found: "
                        + ", ".join(sorted({f"{ev} {ma or '(no matcher)'}" for ev, ma, _ in wired})))
        for c in commands:
            if "scripts/" in c and not re.search(PLUGIN_ROOT_VAR, c):
                clean = False
                out("FAIL", f"Hook command does not use ${{CLAUDE_PLUGIN_ROOT}}: {c}")
            for m in re.finditer(PLUGIN_ROOT_VAR + r"[/\\]([\w./\\-]+)", c):
                rel = m.group(1).replace("\\", "/")
                if not (root / rel).exists():
                    clean = False
                    out("FAIL", f"Hook points at {rel}, which does not exist in the plugin. score_lab2.py fails the same path: it grades the script the hook names, not a same-named file elsewhere in the plugin.")
        if commands and clean:
            out("ok", "Hook commands use the plugin path variable and point at real files")
    else:
        out("WARN", "No hooks/hooks.json")

    # agents
    for f in sorted((root / "agents").glob("*.md")) if (root / "agents").exists() else []:
        fm, has = frontmatter(f)
        if not has:
            out("FAIL", f"{f.name}: no frontmatter, so the agent loads with every field ignored")
            continue
        for k in IGNORED_AGENT_FIELDS:
            if k in fm:
                out("WARN", f"{f.name}: '{k}' may be ignored in a plugin agent (unconfirmed). Do not rely on it for a control.")
        tools = {t.strip().split("(")[0] for t in fm.get("tools", "").split(",") if t.strip()}
        if re.search(r"audit|review|check", fm.get("name", "") + fm.get("description", ""), re.I) and tools & WRITE_TOOLS:
            out("FAIL", f"{f.name}: a checking agent has write-capable tools: {', '.join(sorted(tools & WRITE_TOOLS))}")
        if not fm.get("tools") and not fm.get("disallowedTools"):
            out("WARN", f"{f.name}: no tools or disallowedTools, so the agent inherits everything")
        d = fm.get("description", "")
        if len(d) > MAX_DESCRIPTION:
            out("WARN", f"{f.name}: description is {len(d)} characters. It is in the context window on every turn.")

    # commands
    for f in sorted((root / "commands").glob("*.md")) if (root / "commands").exists() else []:
        fm, has = frontmatter(f)
        d = fm.get("description", "")
        if not d:
            out("FAIL", f"{f.name}: no description, so Claude cannot tell when it applies")
        elif len(d) < 40:
            out("WARN", f"{f.name}: description is only {len(d)} characters. A vague description can stop the command from being chosen.")
        elif len(d) > MAX_DESCRIPTION:
            out("WARN", f"{f.name}: description is {len(d)} characters. It is in the context window on every turn.")
        if TODO_MARKER.search(f.read_text(encoding="utf-8")):
            out("FAIL", f"{f.name}: still contains a TODO line of its own. Naming TODO as text the format hook rejects is fine; leaving 'TODO: write ...' is not.")

    # root CLAUDE.md
    if (root / "CLAUDE.md").exists():
        out("WARN", "A CLAUDE.md at the plugin root is not loaded as project context (claude plugin validate says so too). Put rules that must apply into a command or skill, where you can test them with an eval.")

    # evals
    ev = root / "evals"
    if ev.exists():
        cases = 0
        clean_evals = True
        for case in sorted(p for p in ev.iterdir() if p.is_dir() and p.name != "results"):
            has_case = (case / "prompt.md").exists() or (case / "case.yaml").exists()
            has_grader = any((case / "graders").glob("*.md")) if (case / "graders").exists() else False
            cases += 1 if has_case else 0
            if has_case and not has_grader:
                clean_evals = False
                out("FAIL", f"evals/{case.name}: no grader, so the case fails to load")
        if not cases:
            out("WARN", "evals/ holds no case with a prompt.md or case.yaml. A suite with nothing in it proves nothing: put the deleted cases back.")
        elif clean_evals:
            out("ok", f"Every eval case has at least one grader ({cases} cases)")

    # marketplace
    if mk:
        mf = mk / ".claude-plugin" / "marketplace.json"
        if not mf.exists():
            out("FAIL", f"No marketplace.json at {mf}")
        else:
            catalog = json.loads(mf.read_text(encoding="utf-8"))
            entries = catalog.get("plugins", [])
            names = [e.get("name") for e in entries]
            if placeholder_person(catalog.get("owner")):
                out("WARN", "marketplace.json still names the template owner. Put your team in `owner`.")
            if name and name not in names:
                out("FAIL", f"No marketplace entry named '{name}' (entries: {names}). Entry name and manifest name must match.")
            for e in entries:
                src = e.get("source")
                if isinstance(src, str):
                    if ".." in src:
                        out("FAIL", f"Entry '{e.get('name')}': source contains '..'")
                    elif not (mk / src).exists():
                        out("FAIL", f"Entry '{e.get('name')}': source path {src} does not exist under the marketplace")
            if name in names:
                out("ok", "Marketplace entry name matches the manifest name")

    fails = results.count("FAIL")
    print(f"\n{fails} FAIL, {results.count('WARN')} WARN. Now run: claude plugin validate {root}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
