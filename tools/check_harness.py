#!/usr/bin/env python3
"""Fail if the harness cannot load its scenarios or find the templates and skills. Needs no Docker."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "testing" / "harness"))

from harness import PLAYBOOK_DIR, SKILLS_DIR  # noqa: E402
from harness import scenarios  # noqa: E402


def main():
    problems = []
    if not (PLAYBOOK_DIR / "AGENTS.md").exists():
        problems.append("templates/AGENTS.md not found")
    if not list(SKILLS_DIR.glob("*/SKILL.md")):
        problems.append("no skills found")
    found = getattr(scenarios, "SCENARIOS", None)
    if not found:
        problems.append("no scenarios loaded")
    print("\n".join(problems) if problems else f"Harness loads {len(found)} scenarios.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
