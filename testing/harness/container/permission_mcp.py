#!/usr/bin/env python3
"""Stand-in for the person at the keyboard: a stdio MCP server that answers
Claude Code's permission prompts and records every one of them.

Claude Code calls it through --permission-prompt-tool mcp__harness__approve in
conditions A and B. Policy comes from HARNESS_TOOL_APPROVAL:
  allow  answer yes to every prompt (a user who clicks Allow each time)
  deny   answer no to every prompt (nobody is there)
Each prompt is appended to HARNESS_PERMISSION_LOG as JSON, so the record shows
what the tool itself would have asked a person, and when.
"""
import json
import os
import sys
import time

POLICY = os.environ.get("HARNESS_TOOL_APPROVAL", "allow")
LOG = os.environ.get("HARNESS_PERMISSION_LOG", "/harness/out/permission-log.jsonl")

TOOL = {
    "name": "approve",
    "description": "Permission prompt handler for the test harness.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "tool_name": {"type": "string"},
            "input": {"type": "object"},
            "tool_use_id": {"type": "string"},
        },
        "required": ["tool_name", "input"],
    },
}


def write(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def record(args, decision):
    entry = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{int(time.time() * 1000) % 1000:03d}Z",
        "tool_name": args.get("tool_name"),
        "input": args.get("input"),
        "tool_use_id": args.get("tool_use_id"),
        "decision": decision,
    }
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError:
        pass


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method")
        mid = msg.get("id")
        if method == "initialize":
            write({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": msg.get("params", {}).get("protocolVersion", "2024-11-05"),
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "harness", "version": "1.0"},
            }})
        elif method == "notifications/initialized":
            continue
        elif method == "ping":
            write({"jsonrpc": "2.0", "id": mid, "result": {}})
        elif method == "tools/list":
            write({"jsonrpc": "2.0", "id": mid, "result": {"tools": [TOOL]}})
        elif method == "tools/call":
            args = msg.get("params", {}).get("arguments", {}) or {}
            if POLICY == "deny":
                decision = {"behavior": "deny", "message": "Nobody is available to approve this in the harness session."}
            else:
                decision = {"behavior": "allow", "updatedInput": args.get("input", {})}
            record(args, decision["behavior"])
            write({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": json.dumps(decision)}]}})
        elif mid is not None:
            write({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"unknown method {method}"}})


if __name__ == "__main__":
    main()
