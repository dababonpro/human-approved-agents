#!/usr/bin/env python3
"""Customer notes.

    python tools/notes.py --env test add C-1042 "Prefers morning deliveries"
    python tools/notes.py --env test list C-1042
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orderdesk import notes  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--env", default="test", choices=["test", "production"])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add"); s.add_argument("customer_id"); s.add_argument("text")
    s = sub.add_parser("list"); s.add_argument("customer_id")
    a = p.parse_args()
    if a.cmd == "add":
        if notes.add_note(a.env, a.customer_id, a.text):
            print(f"Saved note for {a.customer_id} in {a.env}.")
        else:
            print("Failed to save note.", file=sys.stderr)
            sys.exit(1)
    else:
        print(json.dumps(notes.list_notes(a.env, a.customer_id), indent=2, default=str))


if __name__ == "__main__":
    main()
