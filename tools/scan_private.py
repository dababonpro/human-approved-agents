#!/usr/bin/env python3
"""Fail if a private term appears in any file.

Terms come from the PRIVATE_TERMS environment variable (one per line, set as a CI secret) or a git-ignored
.private-terms file. They stay out of the repository, because the list would itself reveal them.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "__pycache__", "results", "holdout"}
SKIP_FILES = {".private-terms", "LICENSE-docs"}


def terms():
    text = os.environ.get("PRIVATE_TERMS", "")
    local = ROOT / ".private-terms"
    if local.exists():
        text += "\n" + local.read_text(encoding="utf-8")
    return [t.strip().lower() for t in text.splitlines() if t.strip() and not t.startswith("#")]


def main():
    wanted = terms()
    if not wanted:
        print("No private terms set, so nothing was scanned. This is not a pass.")
        return 1
    hits = []
    paths = []
    for folder, dirs, files in os.walk(ROOT):
        # Prune skipped folders here, so a large results folder is never walked.
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        paths += [Path(folder) / f for f in files if f not in SKIP_FILES]
    for path in paths:
        rel = path.relative_to(ROOT)
        try:
            lines = path.read_text(encoding="utf-8").lower().splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            hits += [f"{rel}:{number}" for t in wanted if t in line]
        hits += [f"{rel}: in the file name" for t in wanted if t in str(rel).lower()]
    print("\n".join(sorted(set(hits))) if hits else f"Scanned for {len(wanted)} terms. Nothing found.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
