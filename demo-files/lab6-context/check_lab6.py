#!/usr/bin/env python3
"""Local checker for Lab 6 (Context Engineering, take-home). No model calls.

Usage:  python3 check_lab6.py            (run from the lab6-context folder)

Measures your trimmed shopkit/CLAUDE.md against the untouched copy in original/.
original-plugin/ keeps the untouched plugin descriptions, so the FAIL lines below can show
you what each description used to cost; restore from it if you cut one too far.
Scores 100:
  CLAUDE.md (40): at least 40 percent fewer words (15), the five facts that must survive are still
                  there (15, three points per fact), no stale instruction remains (10).
  Plugin (30): every command and agent description is 200 characters or fewer (12), still 40+ characters (6),
               each still names its trigger topic (12).
  Measurements (15): measure.csv has a value in all six rows it shipped with (rows you add
                     yourself are ignored, and do not stand in for one of the six).
  Rules (15): RULES-LEARNED.md has exactly two numbered rules, each with a because clause
              (any numbered line with a because clause counts, wherever in the file it is).
A fact counts when the file asserts it, and a stale instruction counts as gone when the file
drops it or cancels it ("use pytest, not nosetests"; "Python 2 support was dropped"). Picking
the stale side of the contradiction ("run the tests with nosetests, not pytest") is neither.
It checks the files only. It cannot read your /context output; the measurement rows are self-reported.
The 200 character limit is a lab rule of thumb, not a product limit.
Wording is not graded: every check accepts any phrasing that keeps the fact.
Standard library only.
"""
import csv
import re
from pathlib import Path

HERE = Path(__file__).parent
BASELINE_WORDS = 652  # the shipped original/CLAUDE.md, for a "did you trim the baseline too?" warning
score = 0
out = []
notes = []


def award(points, ok, label, hint="", earned=None):
    """Add points. Pass earned= for a partial-credit check; ok is then ignored."""
    global score
    if earned is None:
        earned = points if ok else 0
    earned = max(0, min(points, int(earned)))
    score += earned
    tag = "PASS" if earned == points else ("PART" if earned else "FAIL")
    show_hint = hint and earned < points
    out.append("[%s] %2d/%-2d %s%s" % (tag, earned, points, label, ("  -> " + hint) if show_hint else ""))


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except OSError:
        return None


def words(text):
    return len(re.findall(r"\S+", text or ""))


def description(path):
    """Return the frontmatter description as Claude would load it.

    Handles a plain value, a value wrapped onto indented continuation lines, and a YAML
    block or folded scalar (description: > or description: |), with quotes stripped.
    Inside real frontmatter a blank line does not end the value: YAML folds it into the
    scalar, so indented text after a blank line still loads as part of the description.
    """
    t = read(path)
    if t is None:
        return ""
    m = re.match(r"---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", t, re.S)
    lines = (m.group(1) if m else t).splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"description:", l)), None)
    if start is None:
        return ""
    value = lines[start].split(":", 1)[1]
    for line in lines[start + 1:]:
        if not line.strip():
            if m is None:
                break  # with no frontmatter fence to stop at, a blank line ends the value
            continue  # inside frontmatter YAML folds the blank line into the scalar
        if not re.match(r"[ \t]", line):
            break  # an unindented line is the next frontmatter key
        value += " " + line.strip()
    value = re.sub(r"^[|>][-+0-9]*[ \t]*", "", value.strip())  # drop a block/folded indicator
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1].strip()
    return value


def sentences(text):
    """Rough sentence split, so a negation in one sentence cannot excuse its neighbours."""
    return [s for s in re.split(r"(?<=[.!?;:])\s+|\n+", text or "") if s.strip()]


# A negation only cancels the term it governs. These three patterns decide which side of a
# negation a term sits on, so "use pytest, not nosetests" reads differently from
# "run the tests with nosetests, not pytest" even though both contain "not".
NEGATES_NEXT = (r"(?i)\b(?:not|never|no longer|don't|do not|doesn't|isn't|aren't|instead of|"
                r"rather than|avoid|avoids|without|dropped|removed|deleted|deprecated|"
                r"stop using|stopped using)\b")
# ... except that negating an omission prescribes the term: "never skip the FTP uploader".
OMISSION = (r"(?i)\b(?:skip|skips|skipping|omit|omits|omitting|forget|forgets|forgetting|miss|"
            r"misses|missing|neglect|neglects|leave out|leaves out|bypass|bypasses|fail to)\b")
# Predicates that retire the term that came before them: "Python 2 support was dropped".
RETIRED_AFTER = (r"(?i)\b(?:was|were|is|are|has been|have been|got)\s+(?:\w+\s+){0,2}"
                 r"(?:dropped|removed|deleted|retired|gone|unsupported|obsolete|stale|dead)\b"
                 r"|\b(?:no longer|not any ?more|does not exist|doesn't exist|never existed)\b")


# Where one clause ends and the next begins. A negation governs only its own clause,
# which is what stops "Avoid tabs and use 4 spaces" reading as a ban on 4 spaces,
# while "run the tests with nosetests, not pytest" still negates pytest.
CLAUSE_BREAK = re.compile(
    "[,;:\u2014]"                                       # comma, semicolon, colon, em dash
    "|\\s[-\u2013]\\s"                                    # spaced hyphen or en dash
    "|\\b(?:and|but|then|while|whereas|however)\\b",      # coordinating conjunctions
    re.I,
)


def occurs_asserted(text, pat, retired_cancels=False):
    """True if some occurrence of pat is asserted rather than negated.

    An occurrence is negated when a negation immediately governs it -- the negation is in
    the same clause ahead of it, with no comma or clause break in between and no omission
    verb turning it into a double negative. With retired_cancels, an occurrence whose
    sentence goes on to retire it ("the FTP uploader was deleted") is negated too.
    """
    for s in sentences(text):
        for m in re.finditer(pat, s):
            before, after = s[:m.start()], s[m.end():]
            # Only the clause the match actually sits in can negate it. A comma, a
            # dash, or a coordinating conjunction starts a new clause, so
            # "Avoid tabs and use 4 spaces" forbids tabs and KEEPS 4 spaces, while
            # "run the tests with nosetests, not pytest" still negates pytest.
            clause = CLAUSE_BREAK.split(before)[-1]
            neg = re.search(NEGATES_NEXT, clause, re.I)
            # The negation has to be close to the match, and an omission verb between
            # the two turns it back into an assertion ("do not omit the 4 spaces").
            gap = clause[neg.end():] if neg else ""
            if neg and len(gap) <= 30 and not re.search(OMISSION, gap, re.I):
                continue
            if retired_cancels and re.search(RETIRED_AFTER, after):
                continue
            return True
    return False


def numbered_rules(text):
    """Return the top-level numbered rules, each joined with its continuation lines.

    Accepts "1." and "1)". Stops at a later heading or at a new prose paragraph, so a
    numbered evidence list further down the file is not counted as a third rule.
    """
    lines = (text or "").splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"[ \t]*\d+[.)][ \t]+\S", l)), None)
    if start is None:
        return []
    body, prev_blank = [], False
    for line in lines[start:]:
        if re.match(r"[ \t]*#{1,6}\s", line):
            break  # a heading ends the rules list
        is_item = re.match(r"[ \t]*\d+[.)][ \t]+\S", line)
        indented = re.match(r"[ \t]+\S", line)
        if prev_blank and line.strip() and not is_item and not indented \
                and not re.match(r"(?i)because\b", line.strip()):
            break  # a fresh unindented paragraph ends the rules list
        body.append(line)
        prev_blank = not line.strip()
    blocks = re.split(r"(?m)^[ \t]*\d+[.)][ \t]+(?=\S)", "\n".join(body))[1:]
    return [b for b in (re.sub(r"\s+", " ", b).strip() for b in blocks) if b]


def numbered_items(text):
    """Every numbered item anywhere in the file, each joined with its continuation lines.

    Used to enforce "exactly two": a numbered item that carries a because clause is a rule
    wherever it sits, so a third rule parked under a later heading still counts, while the
    evidence list the lab invites (numbered measurements, no because clause) does not.
    """
    items, cur = [], None
    for line in (text or "").splitlines():
        if re.match(r"[ \t]*#{1,6}\s", line) or not line.strip():
            cur = None  # a heading or a blank line ends the item being collected
        elif re.match(r"[ \t]*\d+[.)][ \t]+\S", line):
            cur = [re.sub(r"^[ \t]*\d+[.)][ \t]+", "", line)]
            items.append(cur)
        elif cur is not None and (re.match(r"[ \t]+\S", line) or re.match(r"(?i)because\b", line)):
            cur.append(line.strip())
        else:
            cur = None  # fresh unindented prose ends the item
    return [re.sub(r"\s+", " ", " ".join(c)).strip() for c in items]


def main():
    original_text = read(HERE / "original" / "CLAUDE.md")
    after_text = read(HERE / "shopkit" / "CLAUDE.md")
    if after_text is None:
        after_text = ""
        notes.append("shopkit/CLAUDE.md is missing. Trim that file in place; do not delete it.")
    if original_text is None:
        original_text = ""
        notes.append("original/CLAUDE.md is missing. Restore it from the demo files: the checker measures "
                     "your trimmed CLAUDE.md against it.")
    before, after = words(original_text), words(after_text)
    if before and abs(before - BASELINE_WORDS) > BASELINE_WORDS * 0.1:
        notes.append("original/CLAUDE.md is %d words but the shipped copy is about %d. It is the baseline, "
                     "so restore it and trim shopkit/CLAUDE.md only." % (before, BASELINE_WORDS))
    cut = 100.0 * (before - after) / before if before else 0.0
    if not before:
        cut_hint = "cannot measure without original/CLAUDE.md"
    elif not after:
        cut_hint = "shopkit/CLAUDE.md is empty: trim it, do not empty it"
    else:
        cut_hint = "cut more of what Claude would not act on"
    award(15, before > 0 and after > 0 and cut >= 40,
          "CLAUDE.md is at least 40 percent shorter (%d to %d words, %.0f percent)" % (before, after, cut),
          cut_hint)

    must = {
        "the test command (pytest)": r"(?i)\bpytest\b",
        "never commit .env": r"(?i)\.env\b",
        "money is integer cents":
            r"(?i)\bcents?\b[^.\n]{0,40}\bint(?:eger)?s?\b|\bint(?:eger)?s?\b[^.\n]{0,40}\bcents?\b",
        "the public API path (api.py)": r"(?i)\bapi\.py\b",
        "4-space indentation": r"(?i)\b(?:4|four)[ -]spaces?\b",
    }
    # A fact has to be asserted, not forbidden: "run the tests with nosetests, not pytest"
    # mentions pytest but does not keep the test command. The .env rule is itself a
    # prohibition ("never commit .env"), so that one is matched plainly.
    prohibitions = {"never commit .env"}
    missing = [k for k, p in must.items()
               if not (re.search(p, after_text) if k in prohibitions else occurs_asserted(after_text, p))]
    award(15, not missing, "The facts that must survive are still in CLAUDE.md",
          "3 points each; add a line that names: %s" % ", ".join(missing),
          earned=3 * (len(must) - len(missing)))

    stale = {
        "nosetests": r"(?i)\bnosetests\b",
        "Jenkins": r"(?i)\bjenkins\b",
        "the FTP uploader": r"(?i)\bftp\b|ftp_upload",
        "Python 2": r"(?i)\bpython ?2(\.7)?\b",
    }
    # Naming the old tool to cancel it ("use pytest, not nosetests"; "Python 2 support was
    # dropped") resolves the contradiction instead of repeating it, so it is not stale. The
    # negation has to govern the old tool itself: "run the tests with nosetests, not pytest"
    # and "never skip the FTP uploader" still prescribe the thing the lab asks you to drop.
    still = [key for key, pat in stale.items() if occurs_asserted(after_text, pat, retired_cancels=True)]
    award(10, not still, "No stale instruction remains",
          "still prescribes: %s - delete the line, or say plainly that it no longer applies"
          % ", ".join(still))

    files = sorted((HERE / "shopkit-plugin" / "commands").glob("*.md")) + \
        sorted((HERE / "shopkit-plugin" / "agents").glob("*.md"))
    topics = {"price-check": "price", "stock-report": "stock", "refund-policy": "refund", "cart-reviewer": "cart"}
    descs = {f.stem: description(f) for f in files}
    originals = {f.stem: description(f) for f in
                 sorted((HERE / "original-plugin" / "commands").glob("*.md")) +
                 sorted((HERE / "original-plugin" / "agents").glob("*.md"))}

    def was(stem, now):
        n = len(originals.get(stem, ""))
        return " (was %d)" % n if n and n != now else ""

    too_long = ["%s=%d%s" % (k, len(v), was(k, len(v))) for k, v in sorted(descs.items()) if len(v) > 200]
    absent = ["%s has no description" % k for k, v in sorted(descs.items()) if not v]
    award(12, bool(descs) and not too_long and not absent, "Every description is 200 characters or fewer",
          "; ".join(too_long + absent) or "no command or agent files found under shopkit-plugin/")
    short = ["%s=%d" % (k, len(v)) for k, v in sorted(descs.items()) if len(v) < 40]
    award(6, bool(descs) and not short, "No description is shortened to nothing (40+ characters)",
          ("too short: %s - say the job and the trigger in one sentence" % ", ".join(short)) if short
          else "no command or agent files found under shopkit-plugin/")
    off_topic = [k for k in topics if topics[k] not in descs.get(k, "").lower()]
    award(12, not off_topic, "Every description still names its trigger topic",
          "put the trigger word back into: %s"
          % ", ".join("%s (%s)" % (k, topics[k]) for k in sorted(off_topic)))

    try:
        with open(HERE / "measure.csv", newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
    except OSError:
        rows = []
        notes.append("measure.csv is missing. Restore it from the demo files and fill the value column.")
    except (UnicodeDecodeError, csv.Error):
        rows = []
        notes.append("measure.csv could not be read. Save it as comma separated CSV in UTF-8.")

    def cells(row):
        for v in row.values():  # a long unquoted note can land in a list under the rest key
            for one in (v if isinstance(v, list) else [v]):
                yield one or ""

    def measurement(row):
        """Which of the six template measurements this row is, or None for a student's own row.

        The six are (before, after) x (the /context total, the CLAUDE.md line, the plugin
        token cost), so a row a student appends cannot stand in for a template row left
        blank. Matching is on the step and label wording, not on the row's position.
        """
        step = re.sub(r"\s+", " ", (row.get("step") or "")).strip().lower()
        label = re.sub(r"\s+", " ", (row.get("what_to_record") or "")).strip().lower()
        if re.search(r"\b2|after|trimm", step) or "after" in label or "trimm" in label:
            phase = "after"
        elif re.search(r"\b1|before", step) or "before" in label or "startup" in label:
            phase = "before"
        else:
            return None
        if "plugin" in label or "token cost" in label:
            return (phase, "the plugin details token cost")
        if "claude.md" in label and "total" not in label:
            return (phase, "the /context CLAUDE.md line")
        if "total" in label:
            return (phase, "the /context startup total")
        return None

    rows = [r for r in rows if any(c.strip() for c in cells(r))]  # ignore blank records
    done = {measurement(r) for r in rows if (r.get("value") or "").strip()} - {None}
    blank = ["%s (%s)" % (w, p) for p in ("before", "after")
             for w in ("the /context startup total", "the /context CLAUDE.md line",
                       "the plugin details token cost") if (p, w) not in done]
    award(15, not blank, "measure.csv has a value in all six rows",
          "%d of the 6 template rows have a value; still blank: %s"
          % (6 - len(blank), "; ".join(blank[:3]) + (" ..." if len(blank) > 3 else "")))

    rules_text = read(HERE / "RULES-LEARNED.md")
    rules = numbered_rules(rules_text)
    # Any numbered line with a because clause is a rule, wherever it sits, so a third rule
    # parked under a later heading still counts against "exactly two".
    rule_shaped = [b for b in numbered_items(rules_text) if re.search(r"(?i)\bbecause\b", b)]
    no_because = [i + 1 for i, r in enumerate(rules) if not re.search(r"(?i)\bbecause\b", r)]
    if len(rules) != 2:
        hint = "found %d numbered rule(s) in the rules list; write exactly two" % len(rules)
    elif len(rule_shaped) > 2:
        hint = ("found %d numbered lines with a because clause; write exactly two, and keep "
                "evidence notes as prose or - bullets" % len(rule_shaped))
    else:
        many = len(no_because) > 1
        hint = "rule%s %s %s no \"because\" clause: end the rule with the reason you measured" % (
            "s" if many else "", " and ".join(str(i) for i in no_because), "have" if many else "has")
    award(15, len(rules) == 2 and len(rule_shaped) == 2 and not no_because,
          "RULES-LEARNED.md has exactly two numbered rules, each with a because clause", hint)

    print("LAB 6 SCORE (local checks)")
    print("\n".join(out))
    for n in notes:
        print("NOTE: " + n)
    print("\nTOTAL: %d / 100" % score)


if __name__ == "__main__":
    main()
