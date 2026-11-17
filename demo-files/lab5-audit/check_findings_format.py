#!/usr/bin/env python3
"""Student-side format check for the Lab 5 findings file. It checks structure, never the answers.

Usage: python3 check_findings_format.py findings.md harbor-org/org/credentials_inventory.csv

Checks (each shown as ok or MISSING):
  - at least 4 finding blocks, each with all seven fields filled in
  - a "Not a finding" section with at least one item
  - a "Priority order" list with at least 4 items, each with a reason
  - a rotation and ownership table with a row for EVERY credential id in the inventory file
Whether your findings are right is scored by your facilitator against an answer key.
Standard library only.
"""
import csv
import re
import sys

FIELDS = ["File and line", "What is wrong", "Risk", "Severity", "Fix", "Rotation step", "Owner"]


def norm(text):
    """Accept both **Field:** and **Field**: spellings of the template's bold labels."""
    return re.sub(r"\*\*([^*\n]+?)\*\*[ \t]*:", r"**\1:**", text)


def blocks_of(text):
    parts = re.split(r"^#{2,3}[ \t]*Finding[ \t]*\d+\b.*$", text, flags=re.M)[1:]
    return [re.split(r"^#{2,3}[ \t]", b, flags=re.M)[0] for b in parts]


def section(text, title):
    m = re.search(r"^## %s\s*\n(.*?)(?=^## |\Z)" % re.escape(title), text, re.S | re.M)
    return m.group(1) if m else ""


def priority_items(text):
    return [ln for ln in section(text, "Priority order").splitlines() if re.match(r"\s*\d+[.)]\s+\S", ln)]


# Words that only restate a finding's name or its rank. A "reason" built out of
# nothing but these is not a reason, which is why the length of a line cannot
# decide the question: "cred-101 service account key in credentials_inventory"
# is long and says nothing about why it is first.
FILLER = set("""a an the and or of in on to by for with as at is are was were be been
has have had it its this that these those there here also still just very more most
less but if while when than then so too own my our we they them i you
first second third fourth fifth sixth highest high higher top biggest bigger largest
greatest worst priority prioritized prioritised urgent important critical severe
severity rank ranked order next later last one ones number position place spot slot
finding findings issue issues item items problem problems thing things""".split())

CONNECTIVE = r"because|since|reason|so that|as it|as the|which|due to|given|in order|so"


def has_reason(line):
    """True when a priority line says *why* it sits where it does.

    The reason is the clause after the finding's name, introduced either by a
    connective ("because", "since", ...) or by the punctuation that sets it off
    (", " / " - " / ": " / " (" / ". "). The break is not itself the reason, so the
    clause after it must carry at least two words that are not filler - FILLER holds
    the rank words ("highest", "urgent", "critical"), so "Finding 1 - highest" is a
    rank, not a reason, and fails.

    There is deliberately NO word-count floor. An earlier version demanded five
    words and rejected "6. Finding 5, hygiene only." - a terse but genuine reason -
    while accepting a longer restatement of the finding's own name. Length is not
    the signal; saying something beyond the rank is.
    """
    body = re.split(r"^\s*\d+[.)]\s+", line, maxsplit=1)[-1].strip()
    parts = re.split(r"\b(?:%s)\b|[:;,\u2014(\[]|\s[-\u2013]\s|\.\s+" % CONNECTIVE,
                     body, maxsplit=1, flags=re.I)
    if len(parts) < 2:
        return False
    words = re.findall(r"[A-Za-z][A-Za-z'\u2019]*", parts[1])
    return sum(1 for w in words if w.lower() not in FILLER) >= 2


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    text = open(sys.argv[1], encoding="utf-8").read()
    ids = [r["credential_id"] for r in csv.DictReader(open(sys.argv[2], encoding="utf-8"))]
    problems = 0

    blocks = blocks_of(text)
    full = 0
    for i, b in enumerate(blocks, 1):
        nb = norm(b)
        empty = []
        for f in FIELDS:
            m = re.search(r"\*\*%s:\*\*[ \t]*(.*)" % re.escape(f), nb)
            if not m or not m.group(1).strip():
                empty.append(f)
        if empty:
            print("  finding %d: empty fields: %s" % (i, ", ".join(empty)))
        else:
            full += 1
    ok = full >= 4
    problems += not ok
    print("[%s] %d complete finding blocks (need at least 4)" % ("ok" if ok else "MISSING", full))
    if not blocks and re.search(r"finding", text, re.I):
        print("  no `## Finding N` headings found: check your heading spelling (`## Finding 1`, one per finding)")

    nf = [ln for ln in section(text, "Not a finding").splitlines() if ln.strip().startswith("-") and len(ln.strip()) > 2]
    problems += not nf
    print("[%s] 'Not a finding' section has an item" % ("ok" if nf else "MISSING"))

    pr = priority_items(text)
    with_reason = [ln for ln in pr if has_reason(ln)]
    ok = len(pr) >= 4 and len(with_reason) == len(pr)
    problems += not ok
    print("[%s] priority list has %d items, %d with a reason (need 4+, all with a reason)"
          % ("ok" if ok else "MISSING", len(pr), len(with_reason)))
    if pr and len(with_reason) < len(pr):
        print("  each numbered line needs a reason after the finding name, not the name again:")
        print("  \"1. Finding 1, because it is a live credential owned by someone who left\" counts,")
        print("  \"1. Finding 1: the shared CI key\" and \"1. Finding 1 - highest\" do not")

    table = section(text, "Rotation and ownership plan")
    missing = [c for c in ids if c not in table]
    problems += bool(missing)
    print("[%s] rotation table covers every credential in the inventory%s" % ("ok" if not missing else "MISSING", (" (missing: %s)" % ", ".join(missing)) if missing else ""))

    print("\n%s" % ("Format is complete." if not problems else "Fix the MISSING items, then hand the file to your facilitator."))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
