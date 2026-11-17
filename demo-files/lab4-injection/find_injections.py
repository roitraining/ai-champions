#!/usr/bin/env python3
"""Pre-scan for Lab 4: list places where instruction-shaped text hides in a project.

Usage: python3 find_injections.py shipping-notes

It looks in every text file for phrases that address an AI assistant, tell it to hide something
from the user, or tell it to run a command. It is a crude, local detector. It will miss text it
has no phrase for, and it flags some innocent lines. A scan is a starting point, not a defense.
"""
import os
import re
import sys

PATTERNS = [
    (r"note to (ai )?assistants?", "addresses an AI assistant"),
    (r"(system|admin) notice (for|to) the assistant", "claims system authority"),
    (r"additional information for the maintainer'?s ai assistant", "addresses an AI assistant"),
    (r"do not (mention|tell)|no need to mention|without telling", "asks for secrecy"),
    (r"ignore (all )?(previous|prior) instructions", "overrides earlier instructions"),
    (r"\b(curl|wget)\b[^\n]*https?://", "tells the reader to make a network call"),
    (r"<!--.*?-->", "hidden in an HTML comment"),
]
SKIP_DIRS = {".git", "__pycache__", "node_modules"}


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    hits = 0
    for dirpath, dirs, files in os.walk(sys.argv[1]):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            try:
                text = open(path, encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            for n, line in enumerate(text.splitlines(), 1):
                why = [w for p, w in PATTERNS if re.search(p, line, re.I)]
                if why:
                    hits += 1
                    print("%s:%d  [%s]" % (path, n, "; ".join(why)))
                    print("    " + line.strip()[:110] + ("..." if len(line.strip()) > 110 else ""))
    print("\n%d suspicious line(s). Group them by place: file, issue, tool result." % hits)
    return 0


if __name__ == "__main__":
    sys.exit(main())
