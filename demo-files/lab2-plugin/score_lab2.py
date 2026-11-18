#!/usr/bin/env python3
"""Local scorer for Lab 2 (Build a Plugin With a Hook). No model calls, no organization access.

Usage:
    python3 score_lab2.py PLUGIN_DIR --marketplace MARKETPLACE_DIR [--evidence EVIDENCE_FILE]

Scores 100 points:
    manifest 5, hook wiring 20, hook behavior 15, command 20, agent 10, marketplace 10,
    evidence file 20 (validate output 8, details/always-on cost 6, eval summary 6).
The evidence file is a text file where you paste the output of `claude plugin validate`,
`claude plugin details relnotes` and `claude plugin eval` (see the lab). Each row reads only the
block pasted under its own `claude plugin ...` line, with no fallback to the rest of the file.
This scorer only checks that the evidence is there and plausible: it cannot prove the commands
ran, so the facilitator confirms the eval run from a screen or a result file.

Only a hook that runs after a write is a candidate for the wiring and behavior rows, and only
the script path the hook actually names is tested, so this scorer and tools/plugin_lint.py pass
and fail the same hooks.json. The 20 command points are graded on commands/release-notes.md and
the 10 agent points on the agent whose frontmatter name is changelog-auditor, so another file in
those folders can neither earn nor lose them.

The hook is exercised with a full PostToolUse event on standard input, with the documented
fields: hook_event_name, session_id, transcript_path, cwd, tool_name, tool_input, tool_response.
Standard library only.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SECTIONS = ("Breaking changes", "Features", "Fixes", "Other changes")
WRITE_TOOLS = {"Edit", "Write", "Bash", "NotebookEdit"}
# Accept both ${CLAUDE_PLUGIN_ROOT} and $CLAUDE_PLUGIN_ROOT: both expand the same way.
PLUGIN_ROOT_VAR = r"\$\{?CLAUDE_PLUGIN_ROOT\}?"
SCRIPT_SUFFIX = re.compile(r"\.(?:py|sh|bash|js|mjs|cjs|ts|rb|pl|ps1)$")
SCRIPT_IN_COMMAND = re.compile(r"[\w./${}\\-]+\.(?:py|sh|bash|js|mjs|cjs|ts|rb|pl|ps1)\b|scripts/")
FIXED_PATH = re.compile(r"[A-Za-z]:[\\/]|/(home|Users)/")
# A TODO the author left for themselves, not a mention of the word (the hook lints for TODO,
# so a command that documents that rule must not be punished for naming it).
TODO_MARKER = re.compile(
    r"(?mi)^\s{0,8}(?:[-*+>]\s*|#{1,6}\s*)?TODO\b\s*[:\-]"
    r"|TODO:\s"
    r"|\bTODO\b[^\n]{0,30}\b(?:write|fill in|finish|complete)\b"
)
BLOCK_SCALAR = re.compile(r"^[|>][+-]?\d*$")

score = 0
lines = []


def award(points, ok, label, detail=""):
    global score
    got = points if ok else 0
    score += got
    lines.append("[%s] %2d/%-2d %s%s" % ("PASS" if ok else "FAIL", got, points, label, ("  -> " + detail) if (detail and not ok) else ""))


def note(msg):
    lines.append("         ..  %s" % msg)


def _unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def parse_frontmatter(block):
    """Small YAML-mapping reader: scalars, quoted scalars, folded/literal blocks, and lists.

    A list (block `- item` lines, or inline `[a, b]`) and a folded block come back as a
    comma- or space-joined string, so `tools: [Read, Grep]`, a block list and
    `tools: Read, Grep` all read the same way.
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
            val = ", ".join(_unquote(p) for p in val[1:-1].split(",") if p.strip())
        elif items and (not val or BLOCK_SCALAR.match(val)):
            val = ", ".join(items)
        elif cont and (not val or BLOCK_SCALAR.match(val)):
            val = " ".join(cont)
        fields[key] = _unquote(val)
    return fields


def frontmatter(path):
    text = Path(path).read_text(encoding="utf-8")
    m = re.match(r"---\s*\n(.*?)\n---\s*\n", text, re.S)
    return (parse_frontmatter(m.group(1)) if m else {}), text


def tool_set(value):
    return {t.strip().split("(")[0] for t in (value or "").split(",") if t.strip()}


def label_position(text, name, heading_only=False):
    """Position where `name` is used as a label (heading, bullet, numbered step, table cell)."""
    esc = re.escape(name)
    pat = (r"(?mi)^\s{0,8}#{1,6}\s*[*`_]*\s*%s\b" % esc) if heading_only else (
        r"(?mi)^\s{0,8}(?:[#>\-*+]+\s*|\d+[.)]\s*)?[*`_]*\s*%s\b|\|\s*[*`_]*\s*%s\b" % (esc, esc))
    m = re.search(pat, text)
    return m.start() if m else -1


def sections_in_order(text):
    hits = [(label_position(text, s, True), s) for s in SECTIONS]
    hits = [(p, s) for p, s in hits if p >= 0]
    if len(hits) < 2:
        hits = [(p, s) for p, s in ((label_position(text, s), s) for s in SECTIONS) if p >= 0]
    if len(hits) < 2:
        return False
    found = {s for _, s in hits}
    return [s for _, s in sorted(hits)] == [s for s in SECTIONS if s in found]


NO_INVENT = re.compile(r"""(?ix)
      (never|do\s+not|don't|must\s+not|no)\s+(invent|fabricat\w*|make\s+up|made[-\s]up|guess)
    | \bno\s+invented\b
    | (must|has\s+to|should)\s+trace\s+to\s+(a|the)\s+commit
    | (every|each)\s+(bullet|entry|line)\b[^.\n]{0,60}\bcommit
    | only\s+(include|list|write)\b[^.\n]{0,40}\bcommits?\b
""")
ONLY_NOTES_FILE = re.compile(r"""(?ix)
      (nothing|no\s+other\s+files?)\s+(except|other\s+than|but|besides)
    | (change|modify|touch|write|edit)\w*\s+(nothing|no\s+other\s+file\w*)
    | (do\s+not|don't|never|must\s+not)\s+(modify|change|touch|edit|write\s+to)\s+(any\s+)?(other\s+)?file\w*
    | only\s+(ever\s+)?(modify|change|touch|edit|write)\w*\s+`?RELEASE_NOTES\.md
    | (other\s+than|except|apart\s+from|besides)\s+`?RELEASE_NOTES\.md
""")


# "read the git log for that range" is the starter's own to-do note, not an instruction a
# model can follow. The row asks for the invocation, which is what its advice line and the
# lab's hint already ask for: a git log/describe call carrying a flag, a `..` range, a
# placeholder or a format string.
GIT_RANGE_CMD = re.compile(r"""(?ix)
    git\s+(?:log|shortlog|rev-list|describe)\b [^\n]{0,80}?
      (?: --[a-z0-9-]+ | \.\. | <[^\n>]{1,24}> | %[a-zA-Z] | \$ARGUMENTS )
""")


def grade_command(text, fm):
    """The eight command predicates, for one candidate file, in rubric order."""
    body = text.split("---", 2)[-1]
    return [
        TODO_MARKER.search(text) is None,
        len(fm.get("description", "")) >= 40,
        "RELEASE_NOTES.md" in text and "changelog-auditor" in text,
        bool(GIT_RANGE_CMD.search(body))
        and bool(re.search(r"\brange\b|\bsince\b|\.\.|latest tag|previous tag|\bHEAD\b", body, re.I)),
        all(label_position(text, s) >= 0 for s in SECTIONS),
        sections_in_order(text),
        NO_INVENT.search(text) is not None,
        ONLY_NOTES_FILE.search(text) is not None,
    ]


def pick(files, declared, scorer):
    """Grade the artifact the plugin declares, not whichever file scores best.

    `declared` is the subset of files that the plugin itself identifies as the one the lab
    asks for: the command file named release-notes.md, the agent whose frontmatter name is
    changelog-auditor. If one of those is present it is graded and nothing else is, so a
    scratch file dropped into commands/ cannot carry the row while the real component is
    still a TODO. Only when the plugin declares nothing of the kind does the scorer fall
    back to the best candidate, and it says so.
    """
    if declared:
        p = sorted(declared)[0]
        return p, scorer(p), True
    graded = [(p, scorer(p)) for p in sorted(files)]
    best = max(graded, key=lambda g: sum(1 for x in g[1] if x))
    return best[0], best[1], False


def resolve_script(root, cmd):
    """The script a hook command runs, for a command that locates it inside the plugin.

    A command with a path fixed to one machine resolves to nothing, because that is the
    trap the wiring row is about.

    When the command spells out a script path under the plugin root
    (`${CLAUDE_PLUGIN_ROOT}/scripts/x.py`), that path is the answer and nothing else is:
    if the file is not there the hook is broken, which is the FAIL plugin_lint.py prints
    for the same tree, so the scorer must not rescue it by finding a same-named file in
    another folder. Only a command that uses the variable without joining a script path
    to it (`cd "${CLAUDE_PLUGIN_ROOT}" && python3 scripts/x.py`) is resolved by file
    name, so that style choice does not zero the behavior points.
    """
    if not re.search(PLUGIN_ROOT_VAR, cmd) or FIXED_PATH.search(cmd):
        return None, None
    declared = []
    for m in re.finditer(PLUGIN_ROOT_VAR + r"[/\\]([\w./\\-]+)", cmd):
        rel = m.group(1).replace("\\", "/")
        if SCRIPT_SUFFIX.search(rel):
            declared.append(rel)
    for rel in declared:
        if (root / rel).is_file():
            return root / rel, rel
    if declared:
        return None, declared[0]
    for m in re.finditer(r"([\w.-]+\.(?:py|sh|bash|js|mjs|cjs|rb|pl|ps1))", cmd):
        hits = sorted(p for p in root.rglob(m.group(1)) if p.is_file())
        if len(hits) == 1:
            return hits[0], hits[0].relative_to(root).as_posix()
    return None, None


def fires_after_write(event, matcher):
    """True when a hook wired like this actually runs after Claude writes a file.

    The matcher is a regex matched against the tool name, so this asks the question the
    runtime asks rather than looking for a spelling: an empty matcher fires on every tool,
    `Write|Edit` and `.*` fire on a write, `Read` and `Bash(git push:*)` do not. A hook on
    any other event (SessionStart, PreToolUse, Stop) cannot be a format checker for a file
    that has just been written, so it is not a candidate for the behavior rows.
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


def runner_for(cmd, script):
    """Run the script the way the hook command says to, falling back to this Python."""
    parts = cmd.split()
    tok = parts[0].strip("\"'") if parts else ""
    base = os.path.basename(tok).lower()
    if base.startswith("python"):
        return [sys.executable]
    for name in ("bash", "sh", "node", "deno", "ruby", "perl", "pwsh", "powershell"):
        if base.startswith(name):
            exe = shutil.which(name)
            if exe:
                return [exe]
    try:
        shebang = script.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    except (OSError, IndexError):
        shebang = ""
    if shebang.startswith("#!"):
        for name in ("python", "bash", "sh", "node", "ruby", "perl"):
            if name in shebang:
                exe = sys.executable if name == "python" else shutil.which(name)
                if exe:
                    return [exe]
    return [sys.executable]


def hook_event(cwd, path, text):
    """A full PostToolUse payload, with the fields the hooks reference documents."""
    return json.dumps({
        "session_id": "lab2-scorer",
        "transcript_path": str(Path(cwd, "transcript.jsonl")),
        "cwd": str(cwd),
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": str(path), "content": text},
        "tool_response": {"filePath": str(path), "success": True},
    })


COMPARE_GLOBS = (".claude-plugin/plugin.json", "hooks/hooks.json", "commands/*.md", "agents/*.md", "scripts/*")


def tree_signature(base):
    """Whitespace-insensitive content of the files that make the plugin what it is."""
    sig = {}
    for g in COMPARE_GLOBS:
        for p in sorted(base.glob(g)):
            if p.is_file():
                try:
                    sig[p.relative_to(base).as_posix()] = re.sub(r"\s+", " ", p.read_text(encoding="utf-8", errors="replace")).strip()
                except OSError:
                    sig[p.relative_to(base).as_posix()] = None
    return sig


CLAUDE_PLUGIN_CMD = re.compile(r"claude[^\n]{0,60}plugin\s+(validate|details|eval)", re.I)
# A block that says the command was not run scores nothing, whatever result it then claims.
NOT_RUN = re.compile(r"""(?ix)
      fail\w*\s+to\s+(even\s+)?(start|load|run)
    | no\s+cases\s+(ran|started)
    | (could\s+not|couldn't|cannot|can't)\s+(even\s+)?(run|start|load)
    | (did\s*n[o']t|have\s*n[o']t|has\s*n[o']t|never)\s+(actually\s+|yet\s+)?(run|ran|execute\w*)\b
    | not\s+(actually\s+)?(run|ran|executed)\s+(it|this|that|yet)\b
""")


def command_blocks(text):
    """Split the evidence into the output pasted under each `claude plugin ...` command.

    A block runs from the end of one command mention to the next one, so a section heading
    that names the command and the pasted prompt line both feed the same block.
    """
    hits = [(m.start(), m.end(), m.group(1).lower()) for m in CLAUDE_PLUGIN_CMD.finditer(text)]
    blocks = {"validate": [], "details": [], "eval": []}
    for idx, (start, end, kind) in enumerate(hits):
        stop = hits[idx + 1][0] if idx + 1 < len(hits) else len(text)
        blocks[kind].append(text[end:stop])
    return {k: "\n".join(v) for k, v in blocks.items()}


def take_arg(args, flag):
    if flag in args:
        i = args.index(flag)
        if i + 1 >= len(args) or args[i + 1].startswith("--"):
            print("%s needs a value.\n" % flag)
            return None, False
        value = Path(args[i + 1])
        del args[i:i + 2]
        return value, True
    return None, True


def main(argv):
    args = list(argv)
    mk, ok = take_arg(args, "--marketplace")
    if not ok:
        print(__doc__); return 2
    ev, ok = take_arg(args, "--evidence")
    if not ok:
        print(__doc__); return 2
    if len(args) != 1:
        print(__doc__); return 2
    root = Path(args[0])

    # 1 manifest (5)
    name = None
    try:
        name = json.loads((root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")).get("name")
    except (OSError, ValueError):
        pass
    award(5, bool(name and re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name)), "Manifest has a kebab-case name", "check .claude-plugin/plugin.json")

    # 2 hook wiring (20)
    hooks_path = root / "hooks" / "hooks.json"
    entries = []
    try:
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
        for event, groups in (data.get("hooks") or {}).items():
            for g in groups or []:
                for h in (g or {}).get("hooks", []) or []:
                    entries.append((event, (g or {}).get("matcher", ""), h.get("command", "")))
    except (OSError, ValueError):
        pass
    commands = [c for _, _, c in entries]
    write_entries = [e for e in entries if fires_after_write(e[0], e[1])]
    award(5, bool(write_entries), "hooks/hooks.json defines a command hook that runs after a write",
          "a format checker has to run on the event that follows a write: PostToolUse, with no matcher or a "
          "matcher that matches Write and Edit. Found: %s"
          % (", ".join(sorted({"%s %s" % (ev, ma or "(no matcher)") for ev, ma, _ in entries})) or "no command hook at all"))

    script_cmds = [c for c in commands if SCRIPT_IN_COMMAND.search(c)]
    fixed = [c for c in commands if FIXED_PATH.search(c)]
    wired = bool(script_cmds) and all(re.search(PLUGIN_ROOT_VAR, c) for c in script_cmds) and not fixed
    award(8, wired, "Hook command uses $CLAUDE_PLUGIN_ROOT and no path fixed to one machine",
          "every hook command that names a script must locate it with ${CLAUDE_PLUGIN_ROOT}/... (unbraced $CLAUDE_PLUGIN_ROOT is fine); replace any /home/<user>/... or C:\\... path"
          + (" -- fixed path in: %s" % fixed[0] if fixed else ""))

    # Only a hook that fires after a write can be the format checker, so only those are
    # candidates: a working script wired to SessionStart is not this plugin's linter.
    script = rel = missing = None
    picked_from = ""
    for event, matcher, cmd in write_entries:
        script, rel = resolve_script(root, cmd)
        if script:
            picked_from = "%s %s" % (event, matcher or "(no matcher)")
            hook_cmd = cmd
            break
        missing = missing or rel
    award(7, script is not None, "The after-a-write hook points at a script that exists inside the plugin",
          ("the hook names %s, and there is no such file in the plugin (plugin_lint.py FAILs the same path). "
           "Fix the path or move the script there" % missing) if missing else
          "the path after ${CLAUDE_PLUGIN_ROOT}/ must name a file that exists in the plugin, for example scripts/lint_notes.py")

    # 3 hook behavior (15)
    if script:
        note("hook behavior tested with %s, from the %s hook" % (rel, picked_from))
        runner = runner_for(hook_cmd, script)
        with tempfile.TemporaryDirectory() as d:
            notes = Path(d, "RELEASE_NOTES.md")
            bad_text = "TODO write this later\n"
            notes.write_text(bad_text, encoding="utf-8")
            r1 = subprocess.run(runner + [str(script)], input=hook_event(d, notes, bad_text), capture_output=True, text=True)
            good_text = "# Release notes: v1.1 (since v1.0.0)\n\n## Features\n- Add fuzzy search (#41) (a1b2c3d)\n"
            notes.write_text(good_text, encoding="utf-8")
            r2 = subprocess.run(runner + [str(script)], input=hook_event(d, notes, good_text), capture_output=True, text=True)
            other = Path(d, "notes.txt")
            other.write_text("TODO\n", encoding="utf-8")
            r3 = subprocess.run(runner + [str(script)], input=hook_event(d, other, "TODO\n"), capture_output=True, text=True)
        award(7, r1.returncode == 2 and r1.stderr.strip() != "", "Bad notes: the hook exits 2 with a message on stderr", "got exit %s, stderr %r" % (r1.returncode, r1.stderr[:60]))
        award(5, r2.returncode == 0, "Good notes: the hook exits 0", "got exit %s, stderr %r" % (r2.returncode, r2.stderr[:60]))
        award(3, r3.returncode == 0, "Other files are ignored: exit 0", "got exit %s, stderr %r" % (r3.returncode, r3.stderr[:60]))
    else:
        award(15, False, "Hook behavior (needs a working script path first)")

    # 4 command (20)
    cmd_files = sorted((root / "commands").glob("*.md")) if (root / "commands").exists() else []
    if cmd_files:
        cmd_file, got, declared = pick(cmd_files, [p for p in cmd_files if p.name == "release-notes.md"],
                                       lambda p: grade_command(*reversed(frontmatter(p))))
        note("command graded: commands/%s%s" % (cmd_file.name, "" if declared else
             " (no commands/release-notes.md, so the closest file in commands/ was graded; the lab asks for /relnotes:release-notes)"))
        no_todo, described, names, ranged, present, ordered, no_invent, only_notes = got
        award(3, no_todo, "Command has no leftover TODO", "a line such as 'TODO: write the command body' is still there; write the body (naming TODO as text the hook rejects is fine)")
        award(3, described, "Command description is specific (40+ characters)", "say what it does and when to use it, in the frontmatter `description` (a folded `>-` block or one line both work)")
        award(3, names, "Command names RELEASE_NOTES.md and the changelog-auditor agent")
        award(3, ranged, "Command says how to work out the commit range and read the git log", "name the command, for example `git describe --tags --abbrev=0` for the start and `git log <from>..<to>`")
        award(2, present, "Command names all four sections", "name %s as headings, bullets or table rows" % ", ".join(SECTIONS))
        award(2, ordered, "The four sections are in the order the format checker enforces", "the output template must run %s" % " -> ".join(SECTIONS))
        award(2, no_invent, "Command forbids inventing entries", "say it plainly, for example 'never invent an entry' or 'every bullet must trace to a commit'")
        award(2, only_notes, "Command limits changes to RELEASE_NOTES.md", "say it plainly, for example 'change nothing except RELEASE_NOTES.md' or 'do not modify any other file'")
    else:
        award(20, False, "Command file exists in commands/")

    # 5 agent (10)
    agent_files = sorted((root / "agents").glob("*.md")) if (root / "agents").exists() else []
    if agent_files:
        def grade_agent(p):
            fm, _ = frontmatter(p)
            allowed, denied = tool_set(fm.get("tools")), tool_set(fm.get("disallowedTools"))
            read_only = (bool(allowed) and not (allowed & WRITE_TOOLS)) or (bool(denied) and WRITE_TOOLS <= denied)
            return [fm.get("name") == "changelog-auditor", read_only, allowed, denied]
        auditors = [p for p in agent_files if frontmatter(p)[0].get("name") == "changelog-auditor"]
        agent_file, got, declared = pick(agent_files, auditors, lambda p: grade_agent(p)[:2])
        is_auditor, read_only = got
        fm, _ = frontmatter(agent_file)
        allowed, denied = tool_set(fm.get("tools")), tool_set(fm.get("disallowedTools"))
        note("agent graded: agents/%s%s" % (agent_file.name, "" if declared else
             " (no agent is named changelog-auditor, so the closest file in agents/ was graded; the command calls that name)"))
        award(10, read_only, "The checking agent has read-only tools",
              "tools = %s, disallowedTools = %s. Either list only read tools (`tools: Read, Grep, Glob`) or deny every write tool (`disallowedTools: %s`)"
              % (sorted(allowed), sorted(denied), ", ".join(sorted(WRITE_TOOLS))))
    else:
        award(10, False, "Agent file exists in agents/")

    # 6 marketplace (10)
    ok_mk, why = False, "pass --marketplace DIR; the entry name must equal the manifest name and `source` must point at the plugin folder"
    if mk and name:
        try:
            entries_mk = json.loads((mk / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8")).get("plugins", [])
        except (OSError, ValueError) as exc:
            entries_mk = []
            why = "could not read %s (%s)" % (mk / ".claude-plugin" / "marketplace.json", exc)
        for e in entries_mk:
            src = e.get("source")
            if e.get("name") != name or not isinstance(src, str) or ".." in src:
                continue
            src_dir = mk / src
            if not (src_dir / ".claude-plugin" / "plugin.json").exists():
                why = "entry '%s' points at %s, which holds no .claude-plugin/plugin.json" % (name, src)
                continue
            same = False
            try:
                same = os.path.samefile(src_dir, root)
            except OSError:
                pass
            if same or tree_signature(src_dir) == tree_signature(root):
                ok_mk = True
                break
            why = ("the plugin inside the marketplace is not the one just graded: %s differs from %s. "
                   "Copy your fixed plugin over it, or point `source` at the plugin you graded" % (src, root))
    award(10, ok_mk, "Marketplace entry matches the manifest and its source holds the graded plugin", why)

    # 7 evidence (20)
    text = ev.read_text(encoding="utf-8", errors="replace") if ev and ev.exists() else ""

    blocks = command_blocks(text)
    # Each row reads only the block pasted under its own `claude plugin ...` line. There is
    # deliberately no whole-file fallback: without it the three rows collapse into one
    # keyword search over the file, and a sentence claiming a result scores the same as the
    # result. The lab says this, in Step 6.
    vb = blocks["validate"]
    # Real `claude plugin validate` output, captured from 2.1.322 on 2026-11-14, has two
    # halves. The plugin's own result comes first. Then a "Plugin directory checks for
    # ..." section about SUBMITTING to the plugin catalog, which reports README, LICENSE
    # and icon problems, and which the tool itself closes with "These plugin directory
    # checks do not change the result below."
    #
    # That second half must not be read as failure. This lab's own solution plugin
    # reports "Found 2 problems the plugin directory refuses a submission for" and is
    # perfectly valid, and the half also contains the sentence "To fail on problems ...",
    # whose bare word "fail" scored a correct student 0 of 8 until this was fixed.
    #
    # The real signal is "Found N errors" in the FIRST half: a broken manifest prints
    # "Found 4 errors:" there, a good one prints no such line. Exit status is 0 for both,
    # so it cannot be used.
    vb_plugin = re.split(r"(?im)^\s*Plugin directory checks for\b", vb)[0]
    real_errors = re.search(r"(?i)Found\s+([1-9]\d*)\s+error", vb_plugin)
    neutral = re.sub(r"(?i)\b(0|no|zero)\s+(error|errors|failure|failures|problem|problems)\b", " ZEROERRORS ", vb_plugin)
    good_run = re.search(r"(?i)\b(validating|passed|passes|valid|success|successful|succeeded|ok|ZEROERRORS)\b", neutral)
    bad_run = real_errors or re.search(r"(?i)\bnot ok\b|\b(failed|failing|invalid|broken|traceback)\b", neutral)
    not_run = NOT_RUN.search(vb)
    award(8, bool(vb.strip()) and bool(good_run) and not bad_run and not not_run, "Evidence: validate output pasted and it reports success",
          "paste the `claude plugin validate` output under a `claude plugin validate` line, showing it passed (0 errors). If it still reports errors, fix them and run it again"
          + (" -- the pasted run still reports %r" % bad_run.group(0) if bad_run else "")
          + (" -- the block says the command was not run (%r)" % not_run.group(0) if not_run else ""))

    db = blocks["details"]
    cost = re.search(r"(?i)(always[- ]on|projected token|token cost|context cost)[^\n]{0,80}?\d", db) or re.search(r"(?i)\b\d[\d,._]*\s*k?\s*tokens\b", db)
    award(6, bool(cost) and not NOT_RUN.search(db), "Evidence: plugin details output with the projected token cost pasted",
          "paste `claude --plugin-dir ~/plugins/relnotes plugin details relnotes`, the command line included, with the always-on token figure and its number under it"
          + ("" if db.strip() else " -- no `claude plugin details` line found in the evidence file"))

    eb = blocks["eval"]
    figure = re.search(r"(?i)\b\d+\s*(?:/|of|out of)\s*\d+\b|\b\d+\s*(?:cases?|runs?|tests?)\b|\b(?:pass(?:ed)?|fail(?:ed)?)\s*[:=]?\s*\d+", eb)
    meta = re.search(r"(?i)aggregate-result|report\.html|results/|threshold|pass rate|--runs|\bruns?\s*[:=]?\s*\d+|max-cost|cost\b[^\n]{0,20}\$?\d|\$\s*\d", eb)
    never_ran = NOT_RUN.search(eb)
    award(6, bool(figure) and bool(meta) and not never_ran, "Evidence: eval run summary pasted, with the case results and the run settings",
          "paste the summary of `claude plugin eval ... --runs N --max-cost-usd C`: the per-case results and the aggregate-result or report path. "
          "A case that failed is fine to report, a suite that never ran is not")

    print("LAB 2 SCORE (local checks)")
    print("\n".join(lines))
    print("\nTOTAL: %d / 100" % score)
    print("The 20 evidence points are a plausibility check on pasted text, not proof. "
          "The facilitator confirms the eval run from a screen or a result file.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
