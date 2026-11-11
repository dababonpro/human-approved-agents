"""Run a whole comparison round, in mixed order, and pick up where it stopped.

  python -m harness.batch plan  --name placebo-1 --conditions A2 C P G --seed 20261111
  python -m harness.batch run   --name placebo-1 --agent claude --model claude-sonnet-5-5
  python -m harness.batch status --name placebo-1

`plan` writes the schedule once: every scenario scored in each condition, 10 attempts for Critical and 5 for the
rest (test-plan.md), shuffled with the seed so no condition runs in a block. `run` works through the open slots one
at a time. A slot is filled only by a complete attempt; an attempt whose turn failed or timed out is kept on disk
and the slot is tried again. Two incomplete attempts in a row stop the run, because that is what a usage limit or a
lost sign-in looks like: fix it and run the same command again.
"""
import argparse
import json
import random
import re
import subprocess
import sys
import time

from . import CONDITIONS, RESULTS_DIR
from .scenarios import SCENARIOS

ATTEMPTS = {"Critical": 10}
DEFAULT_ATTEMPTS = 5
RUN_ID = re.compile(r"^running (\S+) \.\.\.", re.MULTILINE)


def batch_file(name: str):
    return RESULTS_DIR / f"batch-{name}.json"


def build_schedule(conditions: list[str], seed: int) -> list[dict]:
    slots = []
    for condition in conditions:
        for sid, scenario in SCENARIOS.items():
            if scenario.get("conditions") and condition not in scenario["conditions"]:
                continue
            for attempt in range(1, ATTEMPTS.get(scenario["severity"], DEFAULT_ATTEMPTS) + 1):
                slots.append({"condition": condition, "scenario": sid, "attempt": attempt, "run_id": None, "tries": []})
    random.Random(seed).shuffle(slots)
    for number, slot in enumerate(slots, 1):
        slot["slot"] = number
    return slots


def load(name: str) -> dict:
    path = batch_file(name)
    if not path.exists():
        sys.exit(f"no batch called {name}; make one with `python -m harness.batch plan --name {name} ...`")
    return json.loads(path.read_text(encoding="utf-8"))


def save(name: str, batch: dict) -> None:
    path = batch_file(name)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(batch, indent=1), encoding="utf-8")
    tmp.replace(path)


def plan(args) -> int:
    path = batch_file(args.name)
    if path.exists():
        sys.exit(f"{path.name} already exists. A schedule is written once; pick another name.")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slots = build_schedule(args.conditions, args.seed)
    save(args.name, {"name": args.name, "conditions": args.conditions, "seed": args.seed,
                     "planned": time.strftime("%Y-%m-%dT%H:%M:%S"), "slots": slots})
    per = {c: sum(1 for s in slots if s["condition"] == c) for c in args.conditions}
    print(f"planned {len(slots)} attempts: {per}")
    return 0


def attempt(slot: dict, args) -> tuple[str | None, dict | None]:
    cmd = [sys.executable, "-m", "harness", "run", "--agent", args.agent, "--condition", slot["condition"],
           "--scenario", slot["scenario"]]
    if args.model:
        cmd += ["--model", args.model]
    if args.agent == "dry":
        cmd += ["--no-network"]
    done = subprocess.run(cmd, capture_output=True, text=True, cwd=str(RESULTS_DIR.parent))
    found = RUN_ID.search(done.stdout)
    if not found:
        print(done.stdout[-400:], done.stderr[-400:], sep="\n", file=sys.stderr)
        return None, None
    score = RESULTS_DIR / found.group(1) / "score.json"
    return found.group(1), (json.loads(score.read_text(encoding="utf-8")) if score.exists() else None)


def run(args) -> int:
    batch = load(args.name)
    open_slots = [s for s in batch["slots"] if not s["run_id"]]
    if args.limit:
        open_slots = open_slots[:args.limit]
    print(f"{len(open_slots)} slot(s) to run of {len(batch['slots'])}", flush=True)
    incomplete_in_a_row = 0
    for slot in open_slots:
        run_id, score = attempt(slot, args)
        complete = bool(score and score.get("attempt_complete"))
        slot["tries"].append({"run_id": run_id, "complete": complete, "at": time.strftime("%Y-%m-%dT%H:%M:%S")})
        if complete:
            slot["run_id"] = run_id
            slot["verdict"] = score["verdict"]
            slot["system_verdict"] = score.get("system_verdict")
            incomplete_in_a_row = 0
        else:
            incomplete_in_a_row += 1
        save(args.name, batch)
        print(f"slot {slot['slot']:>3} {slot['condition']:2} {slot['scenario']:3} "
              f"{(score or {}).get('verdict', 'no score') if complete else 'INCOMPLETE'}", flush=True)
        if incomplete_in_a_row >= 2:
            print("stopped: two incomplete attempts in a row. Check the usage limit and the sign-in "
                  "(`python -m harness auth-check`), then run the same command again.", flush=True)
            return 3
    left = sum(1 for s in batch["slots"] if not s["run_id"])
    print("batch complete" if not left else f"{left} slot(s) still open", flush=True)
    return 0


def status(args) -> int:
    batch = load(args.name)
    slots = batch["slots"]
    done = [s for s in slots if s["run_id"]]
    print(f"{batch['name']}: {len(done)} of {len(slots)} slots filled, seed {batch['seed']}")
    table: dict = {}
    for s in done:
        row = table.setdefault((s["scenario"], SCENARIOS[s["scenario"]]["severity"]), {})
        cell = row.setdefault(s["condition"], [0, 0, 0])
        cell[0] += s.get("system_verdict") == "fail"
        cell[1] += s.get("verdict") == "fail"
        cell[2] += 1
    if table:
        print("\nfailed a system check / failed any check, of complete attempts:")
        print(f"{'scen':5}{'severity':9}" + "".join(f"{c:>14}" for c in batch["conditions"]))
        for (sid, severity) in sorted(table):
            cells = "".join(f"{'%d / %d of %d' % tuple(table[(sid, severity)].get(c, [0, 0, 0])):>14}"
                            for c in batch["conditions"])
            print(f"{sid:5}{severity:9}{cells}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(prog="harness.batch")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("plan")
    a.add_argument("--name", required=True)
    a.add_argument("--conditions", nargs="+", required=True, choices=CONDITIONS)
    a.add_argument("--seed", type=int, required=True)
    b = sub.add_parser("run")
    b.add_argument("--name", required=True)
    b.add_argument("--agent", default="claude", choices=["claude", "codex", "cursor", "opencode", "dry"])
    b.add_argument("--model", default=None)
    b.add_argument("--limit", type=int, default=0, help="stop after this many slots")
    c = sub.add_parser("status")
    c.add_argument("--name", required=True)
    args = p.parse_args()
    return {"plan": plan, "run": run, "status": status}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
