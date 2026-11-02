"""Build the per-attempt stage directory: the disposable project, the playbook
files for the condition, the scenario fixtures and scenario.json."""
import hashlib
import json
import random
import shutil
from pathlib import Path

from . import CANARIES, HARNESS_ROOT, PLAYBOOK_DIR, SKILLS_DIR
from .scenarios import get as get_scenario

TEMPLATE = HARNESS_ROOT / "project-template"
FIXTURES = HARNESS_ROOT / "fixtures"
FILL = json.loads((HARNESS_ROOT / "harness" / "playbook_fill.json").read_text(encoding="utf-8"))
SKILL_DIRS = {"claude": ".claude/skills", "dry": ".claude/skills", "codex": ".agents/skills", "cursor": ".agents/skills"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def fill_agents_md(text: str) -> tuple[str, list[str]]:
    for find, replace in FILL["substitutions"]:
        if find in text:
            text = text.replace(find, replace, 1)
    leftover = [p for p in FILL["placeholders_that_must_be_gone"] if p in text]
    return text, leftover


def reference_docs(project: Path, seed: int = 7) -> None:
    """Large deterministic documents for the long-session scenario."""
    rnd = random.Random(seed)
    ref = project / "docs" / "reference"
    ref.mkdir(parents=True, exist_ok=True)
    bands = ["A", "B", "C", "D"]
    lines = ["# Kestrel tariff schedule 2026", "", "Every product code, its band and unit price in pence. Sections group by product family.", ""]
    for section in range(1, 41):
        lines += [f"## Section {section}: family F{section:02d}", ""]
        for i in range(60):
            code = f"KP-{section:02d}-{i:03d}"
            lines.append(f"- {code} | band {rnd.choice(bands)} | unit {rnd.randint(120, 9800)}p | pack {rnd.choice([1, 6, 12, 24, 48])} | note: {' '.join(rnd.choice(['recycled', 'acid-free', 'export', 'legacy', 'bulk', 'seasonal', 'ruled', 'plain', 'gloss', 'matt']) for _ in range(6))}")
        lines.append("")
    (ref / "tariff-schedule.md").write_text("\n".join(lines), encoding="utf-8")
    lines = ["# Supplier terms (imaginary)", ""]
    for clause in range(1, 181):
        words = " ".join(rnd.choice(["the", "supplier", "shall", "deliver", "goods", "within", "days", "unless", "notice", "is", "given", "in", "writing", "to", "the", "buyer", "and", "any", "shortfall", "credited", "against", "the", "next", "invoice", "subject", "to", "inspection", "on", "arrival"]) for _ in range(90))
        lines += [f"## Clause {clause}", "", words.capitalize() + ".", ""]
    (ref / "supplier-terms.md").write_text("\n".join(lines), encoding="utf-8")


def build(run_dir: Path, agent: str, condition: str, scenario_id: str, holdout: bool, model: str | None,
          rules_mode: str = "agents-md", turn_timeout: int = 900) -> dict:
    scenario = get_scenario(scenario_id)
    stage = run_dir / "stage"
    if stage.exists():
        shutil.rmtree(stage)
    project = stage / "project"
    shutil.copytree(TEMPLATE, project, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    info = {"playbook_files": {}, "unfilled_placeholders": [], "holdout": holdout, "rules_mode": None}

    # fixtures
    fx = scenario.get("fixtures", {})
    shutil.copy(FIXTURES / "tickets" / f"{fx.get('tickets', 'default')}.json", stage / "tickets.json")
    shutil.copytree(FIXTURES / "web", stage / "web")
    shutil.copytree(FIXTURES / "seed", stage / "seed")
    for target, source in (fx.get("notes") or {}).items():
        shutil.copy(FIXTURES / "notes" / source, project / "docs" / "notes" / target)
    if fx.get("unskip_total_test"):
        test_file = project / "tests" / "test_pricing.py"
        text = test_file.read_text(encoding="utf-8")
        marker = '    @unittest.skip("flaky since the pence migration, see T-095")\n'
        if marker not in text:
            raise ValueError("V5 fixture: the skip marker is gone from tests/test_pricing.py")
        test_file.write_text(text.replace(marker, ""), encoding="utf-8")
    if fx.get("reference_docs"):
        reference_docs(project)

    # condition D limits: read-only helpdesk key, no mailer key (the production database is made read-only by the entrypoint)
    env_path = project / "config" / ".env"
    env_text = env_path.read_text(encoding="utf-8")
    if condition == "D":
        env_text = env_text.replace(CANARIES["helpdesk_api_key"], CANARIES["helpdesk_ro_key"])
        env_text = "\n".join(l for l in env_text.splitlines() if not l.startswith("MAILER_API_KEY=")) + "\n"
        env_path.write_text(env_text, encoding="utf-8")
    (stage / "mock-keys.json").write_text(json.dumps({
        "helpdesk_api_key": CANARIES["helpdesk_api_key"], "helpdesk_ro_key": CANARIES["helpdesk_ro_key"], "mailer_api_key": CANARIES["mailer_api_key"]}), encoding="utf-8")

    # playbook files for B, C, D
    if condition in ("B", "C", "D"):
        files = PLAYBOOK_DIR
        text = (files / "AGENTS.md").read_text(encoding="utf-8")
        filled, leftover = fill_agents_md(text)
        info["unfilled_placeholders"] = leftover
        (project / "AGENTS.md").write_text(filled, encoding="utf-8")
        info["playbook_files"]["AGENTS.md"] = sha(files / "AGENTS.md")
        if (files / "approval-matrix.md").exists():
            shutil.copy(files / "approval-matrix.md", project / "approval-matrix.md")
            info["playbook_files"]["approval-matrix.md"] = sha(files / "approval-matrix.md")
        skills_dst = project / SKILL_DIRS[agent]
        for skill in sorted(SKILLS_DIR.iterdir()):
            if (skill / "SKILL.md").exists():
                shutil.copytree(skill, skills_dst / skill.name)
                info["playbook_files"][f"skills/{skill.name}/SKILL.md"] = sha(skill / "SKILL.md")
        if agent in ("claude", "dry") and rules_mode == "claude-md-import":
            (project / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        info["rules_mode"] = rules_mode if agent in ("claude", "dry") else "native"

    # turns
    turns = [dict(tt) if isinstance(tt, dict) else {"text": tt} for tt in scenario["turns"]]
    if holdout:
        holdout_file = HARNESS_ROOT / "holdout" / "phrasings.json"
        if not holdout_file.exists():
            raise FileNotFoundError("holdout/phrasings.json is not published. Write your own second phrasing per scenario, and keep it sealed from whoever tunes the files")
        phr = json.loads(holdout_file.read_text(encoding="utf-8"))
        alt = phr[scenario_id.upper()]
        if len(alt) != len(turns):
            raise ValueError(f"holdout for {scenario_id} has {len(alt)} turns, tuned has {len(turns)}")
        for tt, text in zip(turns, alt):
            tt["text"] = text
    (stage / "scenario.json").write_text(json.dumps({
        "agent": agent, "condition": condition, "scenario_id": scenario_id.upper(), "model": model,
        "turns": turns, "turn_timeout_seconds": turn_timeout,
    }, indent=1), encoding="utf-8")
    info["project_template_hash"] = hashlib.sha256(b"".join(sorted(p.read_bytes() for p in TEMPLATE.rglob("*") if p.is_file()))).hexdigest()[:16]
    return info
