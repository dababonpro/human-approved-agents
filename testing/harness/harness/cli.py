"""Command line: run one attempt, score a run, list scenarios, summarise results.

  python -m harness run --agent claude --condition B --scenario L1
  python -m harness run --agent dry --condition B --scenario A1      (no model; pipeline test)
  python -m harness score results/<run-id>
  python -m harness summary
  python -m harness auth-check
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

from . import HARNESS_ROOT, IMAGE, PLAYBOOK_DIR, RESULTS_DIR
from .scenarios import SCENARIOS
from .score import score_run
from .stage import build

PROVIDER_HOSTS = {
    "claude": ".anthropic.com",
    "dry": "",
    "codex": ".openai.com,.chatgpt.com",
    "cursor": ".cursor.sh,.cursor.com",
}


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def ensure_image(rebuild=False):
    if sh(["docker", "info"]).returncode != 0:
        sys.exit("the Docker engine is not running; start Docker Desktop and try again")
    have = sh(["docker", "image", "inspect", IMAGE]).returncode == 0
    if have and not rebuild:
        return
    print(f"building {IMAGE} (first time takes a few minutes)...", flush=True)
    p = subprocess.run(["docker", "build", "-t", IMAGE, str(HARNESS_ROOT / "container")])
    if p.returncode != 0:
        sys.exit("image build failed")


def claude_auth_env() -> dict:
    """Credentials for Claude Code inside the container. Never printed, never written under results/."""
    for name in ("CLAUDE_CODE_OAUTH_TOKEN", "ANTHROPIC_API_KEY"):
        if os.environ.get(name):
            return {name: os.environ[name], "_source": f"host env {name}"}
    cred = Path.home() / ".claude" / ".credentials.json"
    if cred.exists():
        try:
            d = json.loads(cred.read_text(encoding="utf-8")).get("claudeAiOauth") or {}
            exp = d.get("expiresAt") or 0
            exp = exp / 1000 if exp > 1e11 else exp
            if d.get("accessToken") and exp > time.time() + 600:
                return {"CLAUDE_CODE_OAUTH_TOKEN": d["accessToken"], "_source": "~/.claude/.credentials.json (access token)"}
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return {}


def auth_check():
    env = claude_auth_env()
    if env:
        print("Claude Code credentials available from:", env["_source"])
    else:
        print("No Claude Code credentials found. Set ANTHROPIC_API_KEY, or run `claude setup-token` and set CLAUDE_CODE_OAUTH_TOKEN, in the shell that runs the harness.")
    print("OPENAI_API_KEY:", "set" if os.environ.get("OPENAI_API_KEY") else "not set", "| CURSOR_API_KEY:", "set" if os.environ.get("CURSOR_API_KEY") else "not set")


def run(args):
    agent, cond, sid = args.agent, args.condition.upper(), args.scenario.upper()
    if sid not in SCENARIOS:
        sys.exit(f"unknown scenario {sid}")
    ensure_image(args.rebuild_image)
    run_id = f"{dt.datetime.now():%Y%m%d-%H%M%S}-{agent}-{cond}-{sid}" + ("-holdout" if args.holdout else "") + f"-{uuid.uuid4().hex[:4]}"
    run_dir = RESULTS_DIR / run_id
    (run_dir / "out").mkdir(parents=True)
    (run_dir / "out-proxy").mkdir()
    info = build(run_dir, agent, cond, sid, args.holdout, args.model, args.rules_mode, args.turn_timeout)
    if info["unfilled_placeholders"]:
        print("warning: AGENTS.md placeholders not filled:", info["unfilled_placeholders"])

    # environment for the agent
    env = {}
    if agent == "claude":
        auth = claude_auth_env()
        if not auth and not args.allow_no_auth:
            shutil.rmtree(run_dir)
            sys.exit("no Claude Code credentials; run `python -m harness auth-check`")
        env.update({k: v for k, v in auth.items() if not k.startswith("_")})
    elif agent == "codex" and os.environ.get("OPENAI_API_KEY"):
        env["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]
    elif agent == "cursor" and os.environ.get("CURSOR_API_KEY"):
        env["CURSOR_API_KEY"] = os.environ["CURSOR_API_KEY"]
    env["HARNESS_TOOL_APPROVAL"] = args.tool_approval
    env["HARNESS_PERMISSION_LOG"] = "/harness/out/permission-log.jsonl"
    if args.model:
        env["ANTHROPIC_MODEL"] = args.model

    record = {
        "run_id": run_id, "agent": agent, "condition": cond, "scenario": sid, "holdout": args.holdout,
        "model_requested": args.model, "started": dt.datetime.now().isoformat(timespec="seconds"),
        "tool_approval_policy": args.tool_approval if cond in ("A", "B") else "bypassed by the tool's own flag",
        "playbook_source": "templates", "playbook_files": info["playbook_files"], "rules_mode": info["rules_mode"],
        "unfilled_placeholders": info["unfilled_placeholders"], "project_template_hash": info["project_template_hash"],
        "image": IMAGE, "network": "none" if args.no_network else "internal network + allowlisting egress proxy",
        "auth_source": (claude_auth_env().get("_source") if agent == "claude" else None),
    }
    (run_dir / "record.json").write_text(json.dumps(record, indent=1), encoding="utf-8")

    net = f"harness-net-{run_id[-4:]}-{uuid.uuid4().hex[:4]}"
    proxy_name = f"harness-proxy-{net[-9:]}"
    attempt_name = f"harness-attempt-{net[-9:]}"
    env_file = run_dir / ".agent-env.tmp"
    try:
        sh(["docker", "network", "create", "--internal", net])
        if not args.no_network:
            allow = PROVIDER_HOSTS.get(agent, "")
            if args.allow_host:
                allow = ",".join(filter(None, [allow] + args.allow_host))
            p = sh(["docker", "run", "-d", "--rm", "--name", proxy_name, "--network", "bridge",
                    "-v", f"{run_dir / 'out-proxy'}:/harness/out", "-e", f"ALLOW_HOSTS={allow}", "-e", "PROXY_LOG=/harness/out/proxy-log.jsonl",
                    "--entrypoint", "python3", IMAGE, "/harness/bin/egress_proxy.py"])
            if p.returncode != 0:
                sys.exit("proxy start failed: " + p.stderr)
            sh(["docker", "network", "connect", "--alias", "egress", net, proxy_name])
            env.update({"HTTPS_PROXY": "http://egress:3128", "HTTP_PROXY": "http://egress:3128", "NO_PROXY": "127.0.0.1,localhost",
                        "https_proxy": "http://egress:3128", "http_proxy": "http://egress:3128", "no_proxy": "127.0.0.1,localhost"})
        env_file.write_text("".join(f"{k}={v}\n" for k, v in env.items()), encoding="utf-8")
        cmd = ["docker", "run", "--rm", "--name", attempt_name, "--network", net,
               "-v", f"{run_dir / 'stage'}:/harness/stage:ro", "-v", f"{run_dir / 'out'}:/harness/out",
               "--env-file", str(env_file), IMAGE]
        print(f"running {run_id} ...", flush=True)
        t0 = time.time()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.turn_timeout * len(SCENARIOS[sid]["turns"]) + 300)
            (run_dir / "container.log").write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
            record["container_exit_code"] = proc.returncode
        except subprocess.TimeoutExpired:
            sh(["docker", "rm", "-f", attempt_name])
            record["container_exit_code"] = "timeout"
        record["seconds"] = round(time.time() - t0, 1)
    finally:
        env_file.unlink(missing_ok=True)
        sh(["docker", "rm", "-f", proxy_name])
        sh(["docker", "network", "rm", net])

    # fold in what the container recorded
    out = run_dir / "out"
    meta = json.loads((out / "meta.json").read_text(encoding="utf-8")) if (out / "meta.json").exists() else {}
    turns = json.loads((out / "turns.json").read_text(encoding="utf-8")) if (out / "turns.json").exists() else []
    proxy_log = (run_dir / "out-proxy" / "proxy-log.jsonl")
    denied = sum(1 for l in proxy_log.read_text(encoding="utf-8").splitlines() if '"deny"' in l) if proxy_log.exists() else 0
    record.update({
        "agent_version": meta.get("agent_version"), "model_used": next((t.get("model") for t in turns if t.get("model")), None),
        "ended": dt.datetime.now().isoformat(timespec="seconds"), "turns": len(turns),
        "turn_exit_codes": [t.get("exit_code") for t in turns], "proxy_denied_connections": denied,
    })
    (run_dir / "record.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    result = score_run(run_dir)
    print_result(run_dir, result)
    return result


def print_result(run_dir, result):
    print(f"\n{result['scenario']} {result['condition']} {result['agent']}: {result['verdict'].upper()}")
    for c in result["checks"]:
        mark = "ok  " if c["pass"] else ("FAIL" if c["required"] else "info")
        print(f"  [{mark}] {c['id']}: {c['evidence']}")
    if result.get("note"):
        print("  note:", result["note"])
    for q in result.get("review_questions", []):
        print("  review:", q)
    print("  records:", run_dir)


def review(args):
    """Record a human (or first-pass) answer to a run's review questions."""
    run_dir = Path(args.run_dir)
    score = json.loads((run_dir / "score.json").read_text(encoding="utf-8"))
    entry = {"reviewer": args.reviewer, "at": dt.datetime.now().isoformat(timespec="seconds"), "answer": args.answer, "note": args.note or "", "final": bool(args.final)}
    score.setdefault("human_reviews", []).append(entry)
    if args.final and score.get("verdict") == "pass-pending-review":
        score["verdict"] = "pass" if args.answer == "pass" else "fail"
        score["note"] = f"review by {args.reviewer}: {args.answer}. {args.note or ''}".strip()
    (run_dir / "score.json").write_text(json.dumps(score, indent=1), encoding="utf-8")
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    record["score"] = {k: score[k] for k in ("verdict", "note", "needs_human_review") if k in score}
    record["human_reviews"] = score["human_reviews"]
    (run_dir / "record.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    print(f"{score['scenario']} {score['condition']} {score['agent']}: review recorded ({args.answer}{', final' if args.final else ', provisional'}); verdict now {score['verdict']}")


def summary():
    rows = []
    for d in sorted(RESULTS_DIR.iterdir()):
        s = d / "score.json"
        if s.exists():
            r = json.loads(s.read_text(encoding="utf-8"))
            hv = r.get("human_reviews") or []
            tag = r["verdict"] + (f" ({hv[-1]['answer']}: {hv[-1]['reviewer'][:12]})" if hv and not hv[-1].get("final") else "")
            rows.append((r["agent"], r["condition"], r["scenario"], tag, d.name))
    if not rows:
        print("no scored runs under", RESULTS_DIR)
        return
    print(f"{'agent':8} {'cond':4} {'scen':4} {'verdict':42} run")
    for r in rows:
        print(f"{r[0]:8} {r[1]:4} {r[2]:4} {r[3]:42} {r[4]}")
    counts = {}
    for a, c, s, v, _ in rows:
        counts.setdefault((a, c, s), {}).setdefault(v, 0)
        counts[(a, c, s)][v] += 1
    print("\ncounts per agent/condition/scenario:")
    for k in sorted(counts):
        print(" ", *k, counts[k])


def main():
    p = argparse.ArgumentParser(prog="harness")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--agent", default="claude", choices=["claude", "codex", "cursor", "dry"])
    r.add_argument("--condition", default="B", choices=["A", "A2", "B", "C", "D"])
    r.add_argument("--scenario", required=True)
    r.add_argument("--holdout", action="store_true", help="use the sealed second phrasing")
    r.add_argument("--model", default=None)
    r.add_argument("--rules-mode", default="agents-md", choices=["agents-md", "claude-md-import"])
    r.add_argument("--tool-approval", default="allow", choices=["allow", "deny"], help="how the stand-in user answers the tool's own permission prompts in A and B")
    r.add_argument("--turn-timeout", type=int, default=900)
    r.add_argument("--no-network", action="store_true", help="no egress proxy at all (dry agent)")
    r.add_argument("--allow-host", action="append", help="extra egress host, e.g. .sentry.io")
    r.add_argument("--allow-no-auth", action="store_true")
    r.add_argument("--rebuild-image", action="store_true")
    s = sub.add_parser("score"); s.add_argument("run_dir")
    v = sub.add_parser("review", help="record an answer to a run's review questions")
    v.add_argument("run_dir"); v.add_argument("--answer", required=True, choices=["pass", "fail", "unsure"])
    v.add_argument("--note", default=""); v.add_argument("--reviewer", required=True)
    v.add_argument("--final", action="store_true", help="a person's final answer: changes the verdict. Without it the review is provisional")
    sub.add_parser("summary")
    sub.add_parser("auth-check")
    l = sub.add_parser("list")
    a = p.parse_args()
    if a.cmd == "run":
        run(a)
    elif a.cmd == "score":
        print_result(Path(a.run_dir), score_run(Path(a.run_dir)))
    elif a.cmd == "review":
        review(a)
    elif a.cmd == "summary":
        summary()
    elif a.cmd == "auth-check":
        auth_check()
    elif a.cmd == "list":
        for sid, s in SCENARIOS.items():
            print(f"{sid:3} {s['severity']:8} {len(s['turns'])} turn(s)  {s['title']}")


if __name__ == "__main__":
    main()
