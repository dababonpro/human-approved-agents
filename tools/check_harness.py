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
import json  # noqa: E402
import os  # noqa: E402
sys.path.insert(0, str(ROOT / "testing" / "harness" / "container"))
import agent_turns  # noqa: E402
from harness import batch, cli, score  # noqa: E402


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


def _write_agy_run(tmp: Path, events: list[dict]) -> Path:
    run_dir = tmp / "run"
    out = run_dir / "out"
    out.mkdir(parents=True)
    transcript = out / "turn-1.jsonl"
    transcript.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    parsed = agent_turns.agy_parse(transcript)
    (out / "turns.json").write_text(json.dumps([{"turn": 1, **parsed}]), encoding="utf-8")
    return run_dir


def agy_adapter_problems():
    problems = []
    v4_check = next(c for c in scenarios.SCENARIOS["V4"]["checks"] if c["id"] == "reproduced_before_edit")
    l2_skill = next(c for c in scenarios.SCENARIOS["L2"]["checks"] if c["id"] == "skill_invoked")

    # 1. Normalization + V4 pass (reproduction run_command before edit_file) + Skill via read_file
    with tempfile.TemporaryDirectory() as tmp:
        events = [
            {"event": "init", "conversation_id": "conv-1", "init": {"model": "gemini-flash"}},
            {"event": "step_update", "step_update": {"step_index": 1, "step_type": "tool", "state": "DONE",
             "tool_name": "read_file", "tool_info": {"parameters": {"Path": "/work/project/.agents/skills/verify-the-result/SKILL.md"}}}},
            {"event": "step_update", "step_update": {"step_index": 2, "step_type": "tool", "state": "DONE",
             "tool_name": "read_file", "tool_info": {"parameters": {"Path": "/work/project/orderdesk/pricing.py"}}}},
            {"event": "step_update", "step_update": {"step_index": 3, "step_type": "tool", "state": "DONE",
             "tool_name": "run_command", "tool_info": {"parameters": {"CommandLine": "python3 -m unittest tests/test_pricing.py"}}}},
            {"event": "step_update", "step_update": {"step_index": 4, "step_type": "tool", "state": "DONE",
             "tool_name": "edit_file", "tool_info": {"parameters": {"Path": "/work/project/orderdesk/pricing.py"}}}},
            {"event": "step_update", "step_update": {"step_index": 5, "step_type": "tool", "state": "DONE",
             "tool_name": "write_file", "tool_info": {"parameters": {"Path": "/work/project/docs/notes/2026-11-18.md"}}}},
            {"event": "result", "result": {"conversation_id": "conv-1", "response": "Fixed."}},
        ]
        run_dir = _write_agy_run(Path(tmp), events)
        rec = score.Records(run_dir)
        names = [c["name"] for c in rec.tool_calls()]
        expected = ["Skill", "Read", "Bash", "Edit", "Write"]
        if names != expected:
            problems.append(f"agy_parse tool names {names!r} != {expected!r}")
        v4_res = score.check(rec, v4_check)
        if not v4_res["pass"]:
            problems.append(f"agy V4 pass fixture failed: {v4_res['evidence']}")
        skill_res = score.check(rec, l2_skill)
        if not skill_res["pass"]:
            problems.append(f"agy skill_invoked fixture failed: {skill_res['evidence']}")

    # 2. V4 fail (edit_file before any reproduction run_command must see the edit, not say "no edit")
    with tempfile.TemporaryDirectory() as tmp:
        events = [
            {"event": "step_update", "step_update": {"step_index": 1, "step_type": "tool", "state": "DONE",
             "tool_name": "edit_file", "tool_info": {"parameters": {"Path": "/work/project/orderdesk/pricing.py"}}}},
            {"event": "step_update", "step_update": {"step_index": 2, "step_type": "tool", "state": "DONE",
             "tool_name": "run_command", "tool_info": {"parameters": {"CommandLine": "python3 -m unittest tests/test_pricing.py"}}}},
        ]
        run_dir = _write_agy_run(Path(tmp), events)
        v4_res = score.check(score.Records(run_dir), v4_check)
        if v4_res["pass"] or "no edit of the target file" in v4_res["evidence"]:
            problems.append(f"agy V4 fail fixture mis-scored: {v4_res}")

    # 3. agy_cmd rejects A and B
    for cond in ("A", "B"):
        try:
            agent_turns.agy_cmd("hi", {"condition": cond}, None)
            problems.append(f"agy_cmd accepted unsupported condition {cond}")
        except ValueError:
            pass

    # 4. antigravity_auth ignores GEMINI_API_KEY_OLD and prefers GEMINI_API_KEY
    saved = {k: os.environ.get(k) for k in ("GEMINI_API_KEY_OLD", "GEMINI_API_KEY", "ANTIGRAVITY_API_KEY", "ENV_FILE")}
    try:
        for k in saved:
            os.environ.pop(k, None)
        os.environ["GEMINI_API_KEY_OLD"] = "old-key"
        os.environ["GEMINI_API_KEY"] = "current-key"
        auth = cli.antigravity_auth()
        if auth.get("env", {}).get("GEMINI_API_KEY") != "current-key":
            problems.append(f"antigravity_auth did not prefer GEMINI_API_KEY: {auth.get('source')}")
        with tempfile.TemporaryDirectory() as tmp:
            env_file = Path(tmp) / ".env"
            env_file.write_text("GEMINI_API_KEY_OLD=old-file\nANTIGRAVITY_API_KEY=agy-file\n", encoding="utf-8")
            os.environ.pop("GEMINI_API_KEY", None)
            os.environ["ENV_FILE"] = str(env_file)
            auth2 = cli.antigravity_auth()
            if auth2.get("env", {}).get("GEMINI_API_KEY") != "agy-file":
                problems.append(f"antigravity_auth let GEMINI_API_KEY_OLD win over ANTIGRAVITY_API_KEY: {auth2.get('source')}")
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    # 5. batch.build_schedule rejects attempts <= 0
    for bad in (0, -1):
        try:
            batch.build_schedule(["C"], seed=1, attempts=bad)
            problems.append(f"batch.build_schedule accepted attempts={bad}")
        except ValueError:
            pass
    return problems


def main():
    problems = []
    if not (PLAYBOOK_DIR / "AGENTS.md").exists():
        problems.append("templates/AGENTS.md not found")
    if not list(SKILLS_DIR.glob("*/SKILL.md")):
        problems.append("no skills found")
    problems += placebo_problems()
    problems += agy_adapter_problems()
    found = getattr(scenarios, "SCENARIOS", None)
    if not found:
        problems.append("no scenarios loaded")
    print("\n".join(problems) if problems else f"Harness loads {len(found)} scenarios.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
