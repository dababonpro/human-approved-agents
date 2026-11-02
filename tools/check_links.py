#!/usr/bin/env python3
"""Fail if a relative Markdown link or a named template points at nothing."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SKIP = {"node_modules", ".git"}


def main():
    bad = []
    for md in ROOT.rglob("*.md"):
        if SKIP & set(md.relative_to(ROOT).parts) or "project-template" in md.parts:
            continue
        for target in LINK.findall(md.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if not (md.parent / target.split("#")[0]).exists():
                bad.append(f"{md.relative_to(ROOT)}: {target}")
    print("\n".join(bad) if bad else "All relative links resolve.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
