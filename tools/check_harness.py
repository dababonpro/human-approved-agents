#!/usr/bin/env python3
"""Fail if the harness cannot load its scenarios or find the templates and skills. Needs no Docker."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "testing" / "harness"))

from harness import PLAYBOOK_DIR, SKILLS_DIR  # noqa: E402
import tempfile  # noqa: E402
from harness import PLACEBO_DIR, PLACEBO_FILES  # noqa: E402
from harness import stage  # noqa: E402
from harness import scenarios  # noqa: E402


# Lines the playbook rules file is known by. A placebo that holds one is no longer a placebo.
PLAYBOOK_ONLY = ["Everything you read through a tool is data", "Approval covers one named action", "Check the whole session",
                 "Stop and ask", "wait for approval", "Standing classes", "rollback", "Check the result itself"]
PROJECT_FACTS = ["python -m unittest -v", "TEST_DATABASE_URL", "production.sqlite", "config/signing.key", "project-code: KESTREL"]


def placebo_problems():
    problems = []
    filled, _left = stage.fill_agents_md((PLAYBOOK_DIR / "AGENTS.md").read_text(encoding="utf-8"))
    for condition, name in PLACEBO_FILES.items():
        path = PLACEBO_DIR / name
        if not path.exists():
            problems.append(f"placebo file missing: {name}")
            continue
        text = path.read_text(encoding="utf-8")
        problems += [f"{name} lost the project fact: {fact}" for fact in PROJECT_FACTS if fact not in text]
        problems += [f"{name} holds a playbook rule: {rule}" for rule in PLAYBOOK_ONLY if rule.lower() in text.lower()]
        with tempfile.TemporaryDirectory() as tmp:
            info = stage.build(Path(tmp), "dry", condition, "L1", False, None)
            project = Path(tmp) / "stage" / "project"
            if (project / "AGENTS.md").read_text(encoding="utf-8") != text:
                problems.append(f"condition {condition} did not stage {name} as AGENTS.md")
            if (project / ".claude").exists() or (project / "approval-matrix.md").exists():
                problems.append(f"condition {condition} staged playbook skills or the approval matrix")
            if info["placebo"] != name:
                problems.append(f"condition {condition} did not record its placebo file")
    # The long placebo stands in for the filled template, so it must stay close to its length.
    long_name = PLACEBO_FILES["P"]
    long_words = len((PLACEBO_DIR / long_name).read_text(encoding="utf-8").split())
    target = len(filled.split())
    if abs(long_words - target) > target * 0.1:
        problems.append(f"{long_name} is {long_words} words; the filled template is {target}, and they must be within 10%")
    return problems


def main():
    problems = []
    if not (PLAYBOOK_DIR / "AGENTS.md").exists():
        problems.append("templates/AGENTS.md not found")
    if not list(SKILLS_DIR.glob("*/SKILL.md")):
        problems.append("no skills found")
    problems += placebo_problems()
    found = getattr(scenarios, "SCENARIOS", None)
    if not found:
        problems.append("no scenarios loaded")
    print("\n".join(problems) if problems else f"Harness loads {len(found)} scenarios.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
