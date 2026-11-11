#!/usr/bin/env python3
"""Run one attempt's turns against one agent, inside the container, as the
unprivileged user. Reads /harness/stage/scenario.json, writes per-turn
transcripts and turns.json to /harness/out.

Agents: claude (Claude Code), codex (OpenAI Codex CLI), cursor (Cursor CLI).
Only the claude adapter has been exercised; see SCRATCH-LOG.md in the harness.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

STAGE = Path(os.environ.get("HARNESS_STAGE_DIR", "/harness/stage"))
OUT = Path(os.environ.get("HARNESS_OUT_DIR", "/harness/out"))
PROJECT = Path(os.environ.get("HARNESS_PROJECT_DIR", "/work/project"))
MCP_CONFIG = {"mcpServers": {"harness": {"command": "python3", "args": ["/harness/bin/permission_mcp.py"]}}}


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{int(time.time() * 1000) % 1000:03d}Z"


def version_of(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout.strip()
    except Exception as e:
        return f"unknown ({e!r})"


# Conditions that run with the tool's own approvals bypassed. P and G are the placebo rules files.
APPROVALS_OFF = ("A2", "C", "D", "P", "G")


# ---------------- Claude Code ----------------

def claude_cmd(prompt, scenario, session_id):
    cond = scenario["condition"]
    cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose"]
    if scenario.get("model"):
        cmd += ["--model", scenario["model"]]
    if session_id:
        cmd += ["--resume", session_id]
    if cond in APPROVALS_OFF:
        cmd += ["--dangerously-skip-permissions"]
    else:
        cmd += ["--permission-prompt-tool", "mcp__harness__approve",
                "--mcp-config", json.dumps(MCP_CONFIG), "--strict-mcp-config"]
    if scenario.get("max_turns"):
        cmd += ["--max-turns", str(scenario["max_turns"])]
    return cmd


def claude_parse(path):
    session_id, final, compaction, usage, model = None, "", 0, {}, None
    tool_calls, is_error, terminal = [], False, None
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = ev.get("type")
            if t == "system":
                if ev.get("session_id"):
                    session_id = ev["session_id"]
                if ev.get("model"):
                    model = ev["model"]
                if ev.get("subtype") == "compact_boundary":
                    compaction += 1
            elif t == "assistant":
                for block in ev.get("message", {}).get("content", []) or []:
                    if block.get("type") == "tool_use":
                        tool_calls.append({"name": block.get("name"), "input": block.get("input"), "id": block.get("id")})
            elif t == "result":
                session_id = ev.get("session_id") or session_id
                final = ev.get("result") or final
                usage = ev.get("usage") or usage
                terminal = ev.get("terminal_reason") or ev.get("subtype")
                if ev.get("is_error") or ev.get("subtype", "").startswith("error") or terminal == "api_error":
                    is_error = True
                    final = final or json.dumps(ev)[:2000]
    return {"session_id": session_id, "final_text": final, "tool_calls": tool_calls, "compactions": compaction, "usage": usage, "model": model, "is_error": is_error, "terminal_reason": terminal}


# ---------------- Dry run (no model) ----------------

def dry_cmd(prompt, scenario, session_id):
    if session_id:
        os.environ["DRY_SESSION"] = session_id
    return ["python3", "/harness/bin/dry_agent.py", "-p", prompt]


# ---------------- Codex CLI (OpenAI, or Bedrock with HARNESS_CODEX_PROVIDER=bedrock) ----------------

def codex_cmd(prompt, scenario, session_id):
    cond = scenario["condition"]
    base = ["codex", "exec", "--json", "-C", str(PROJECT), "--skip-git-repo-check",
            "-c", 'approval_policy="never"', "-c", 'web_search="disabled"']
    if scenario.get("model"):
        base += ["-m", scenario["model"]]
    if os.environ.get("HARNESS_CODEX_PROVIDER") == "bedrock":
        # Codex's built-in Bedrock provider reads AWS_BEARER_TOKEN_BEDROCK itself and needs only the region.
        # Pinned to Codex 0.124.0: newer versions send a tool type Bedrock rejects, and this one allows only the region.
        base += ["-c", 'model_provider="amazon-bedrock"', "-c",
                 'model_providers.amazon-bedrock.aws.region="%s"' % os.environ.get("AWS_REGION", "us-west-2")]
    if cond in APPROVALS_OFF:
        base += ["--sandbox", "danger-full-access"]
    else:
        # The mocks listen on 127.0.0.1, so the sandbox needs local network access.
        base += ["--sandbox", "workspace-write", "-c", "sandbox_workspace_write.network_access=true"]
    if session_id:
        # `exec resume` accepts its own, narrower option set: in particular it
        # rejects -C and --sandbox. The process cwd remains PROJECT and the
        # resumed thread retains the sandbox selected for its initial turn.
        resume = ["codex", "exec", "resume", "--json", "--skip-git-repo-check",
                  "-c", 'approval_policy="never"', "-c", 'web_search="disabled"',
                  "-c", "sandbox_workspace_write.network_access=true"]
        if scenario.get("model"):
            resume += ["-m", scenario["model"]]
        return resume + [session_id, prompt]
    return base + [prompt]


def codex_parse(path):
    session_id, final, tool_calls = None, "", []
    usage = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "turn.completed":
                for k in usage:
                    usage[k] += int((ev.get("usage") or {}).get(k) or 0)
            if ev.get("type") == "thread.started":
                session_id = ev.get("thread_id")
            item = ev.get("item") or {}
            if ev.get("type") == "item.completed":
                if item.get("type") == "command_execution":
                    tool_calls.append({"name": "Bash", "input": {"command": item.get("command")}})
                elif item.get("type") == "file_change":
                    tool_calls.append({"name": "Edit", "input": {"changes": item.get("changes")}})
                elif item.get("type") == "agent_message":
                    final = item.get("text") or final
    return {"session_id": session_id, "final_text": final, "tool_calls": tool_calls, "compactions": 0, "usage": usage}


# ---------------- Cursor CLI (untested) ----------------

def cursor_cmd(prompt, scenario, session_id):
    cond = scenario["condition"]
    cmd = ["agent", "-p", prompt, "--output-format", "stream-json", "--workspace", str(PROJECT)]
    if scenario.get("model"):
        cmd += ["--model", scenario["model"]]
    if session_id:
        cmd += ["--resume", session_id]
    if cond in APPROVALS_OFF:
        cmd += ["--force"]
    return cmd


def cursor_parse(path):
    session_id, final, tool_calls = None, "", []
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            session_id = ev.get("session_id") or ev.get("chat_id") or session_id
            if ev.get("type") == "assistant":
                for block in ev.get("message", {}).get("content", []) or []:
                    if block.get("type") == "tool_use":
                        tool_calls.append({"name": block.get("name"), "input": block.get("input")})
            if ev.get("type") == "result":
                final = ev.get("result") or final
    return {"session_id": session_id, "final_text": final, "tool_calls": tool_calls, "compactions": 0, "usage": {}}


# ---------------- OpenCode (Bedrock's OpenAI-compatible Chat Completions) ----------------

def opencode_cmd(prompt, scenario, session_id):
    # OpenCode has no separate bypass mode. --auto approves every prompt, which matches the stand-in user
    # answering "allow" in A and B, so every condition uses it. Its prompts are not logged one by one.
    model = scenario.get("model") or "openai.gpt-oss-20b"
    region = os.environ.get("AWS_REGION", "us-west-2")
    conf = Path(os.environ["HOME"]) / ".config" / "opencode" / "opencode.json"
    conf.parent.mkdir(parents=True, exist_ok=True)
    conf.write_text(json.dumps({
        "$schema": "https://opencode.ai/config.json", "autoupdate": False, "share": "disabled",
        "provider": {"bedrock": {"npm": "@ai-sdk/openai-compatible", "name": "Amazon Bedrock",
                                 "options": {"baseURL": f"https://bedrock-mantle.{region}.api.aws/v1",
                                             "apiKey": "{env:AWS_BEARER_TOKEN_BEDROCK}"},
                                 "models": {model: {"name": model}}}},
    }), encoding="utf-8")
    cmd = ["opencode", "run", "--format", "json", "--pure", "--auto", "--dir", str(PROJECT), "-m", f"bedrock/{model}"]
    if session_id:
        cmd += ["-s", session_id]
    return cmd + [prompt]


def opencode_parse(path):
    session_id, texts, tool_calls = None, [], []
    usage = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0}
    with path.open(encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            session_id = ev.get("sessionID") or session_id
            part = ev.get("part") or {}
            if ev.get("type") == "text" and part.get("text"):
                texts.append(part["text"])
            elif ev.get("type") == "tool_use":
                tool = part.get("tool")
                inp = (part.get("state") or {}).get("input") or {}
                name = {"bash": "Bash", "edit": "Edit", "write": "Write", "read": "Read"}.get(tool, tool)
                tool_calls.append({"name": name, "input": {"command": inp.get("command"), "file_path": inp.get("filePath"),
                                                           "content": inp.get("content"), "new_string": inp.get("newString"),
                                                           "old_string": inp.get("oldString"), "pattern": inp.get("pattern")}})
            elif ev.get("type") == "step_finish":
                tok = part.get("tokens") or {}
                usage["input_tokens"] += int(tok.get("input") or 0) + int((tok.get("cache") or {}).get("read") or 0)
                usage["cached_input_tokens"] += int((tok.get("cache") or {}).get("read") or 0)
                usage["output_tokens"] += int(tok.get("output") or 0) + int(tok.get("reasoning") or 0)
    # The final answer is the text after the last tool call; keep all text if there was none.
    return {"session_id": session_id, "final_text": texts[-1] if texts else "", "tool_calls": tool_calls,
            "compactions": 0, "usage": usage}


ADAPTERS = {
    "claude": (claude_cmd, claude_parse, ["claude", "--version"]),
    "dry": (dry_cmd, claude_parse, ["python3", "--version"]),
    "codex": (codex_cmd, codex_parse, ["codex", "--version"]),
    "cursor": (cursor_cmd, cursor_parse, ["agent", "--version"]),
    "opencode": (opencode_cmd, opencode_parse, ["opencode", "--version"]),
}


def main():
    scenario = json.loads((STAGE / "scenario.json").read_text(encoding="utf-8"))
    agent = scenario["agent"]
    build, parse, vcmd = ADAPTERS[agent]
    turns_out = []
    session_id = None
    timeout = int(scenario.get("turn_timeout_seconds", 900))
    meta = {"agent": agent, "agent_version": version_of(vcmd), "started": utc(), "condition": scenario["condition"],
            "scenario": scenario["scenario_id"], "model_requested": scenario.get("model"),
            "reasoning_effort": "medium (Codex default)" if agent == "codex" else None}
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    for i, turn in enumerate(scenario["turns"], start=1):
        prompt = turn["text"]
        if turn.get("claude_only") and agent not in ("claude", "dry"):
            turns_out.append({"turn": i, "started": utc(), "ended": utc(), "seconds": 0, "prompt": prompt, "skipped": True,
                              "exit_code": 0, "timed_out": False, "session_id": session_id, "final_text": "", "tool_calls": [], "compactions": 0, "usage": {}})
            (OUT / "turns.json").write_text(json.dumps(turns_out, indent=1), encoding="utf-8")
            continue
        cmd = build(prompt, scenario, session_id)
        transcript = OUT / f"turn-{i}.jsonl"
        started = utc()
        t0 = time.time()
        with transcript.open("w", encoding="utf-8") as f, (OUT / f"turn-{i}.stderr.txt").open("w", encoding="utf-8") as err:
            try:
                proc = subprocess.run(cmd, cwd=PROJECT, stdout=f, stderr=err, timeout=timeout)
                code = proc.returncode
                timed_out = False
            except subprocess.TimeoutExpired:
                code, timed_out = -1, True
        parsed = parse(transcript)
        session_id = parsed["session_id"] or session_id
        turns_out.append({
            "turn": i, "started": started, "ended": utc(), "seconds": round(time.time() - t0, 1),
            "prompt": prompt, "role": turn.get("role", "user"), "exit_code": code, "timed_out": timed_out,
            "session_id": session_id, "final_text": parsed["final_text"], "tool_calls": parsed["tool_calls"],
            "compactions": parsed["compactions"], "usage": parsed["usage"], "model": parsed.get("model"), "is_error": parsed.get("is_error", False), "terminal_reason": parsed.get("terminal_reason"), "command": [c if len(c) < 400 else c[:400] + "..." for c in cmd],
        })
        (OUT / "turns.json").write_text(json.dumps(turns_out, indent=1), encoding="utf-8")
        if turn.get("pause_seconds"):
            time.sleep(turn["pause_seconds"])
    meta["ended"] = utc()
    (OUT / "meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
