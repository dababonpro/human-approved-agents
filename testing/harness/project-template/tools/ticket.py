#!/usr/bin/env python3
"""Helpdesk tickets.

    python tools/ticket.py list
    python tools/ticket.py show T-101
    python tools/ticket.py update T-101 --status closed --assignee wen
    python tools/ticket.py label T-101 --add triage:billing
    python tools/ticket.py comment T-101 "text"
    python tools/ticket.py settings get
    python tools/ticket.py settings set queue_name desk
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orderdesk import helpdesk  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    s = sub.add_parser("show"); s.add_argument("key")
    s = sub.add_parser("update"); s.add_argument("key"); s.add_argument("--status"); s.add_argument("--assignee"); s.add_argument("--title")
    s = sub.add_parser("label"); s.add_argument("key"); s.add_argument("--add", action="append", default=[])
    s = sub.add_parser("comment"); s.add_argument("key"); s.add_argument("text")
    s = sub.add_parser("settings"); s.add_argument("action", choices=["get", "set"]); s.add_argument("name", nargs="?"); s.add_argument("value", nargs="?")
    a = p.parse_args()

    if a.cmd == "list":
        for t in helpdesk.list_tickets():
            print(f"{t['key']}  {t['status']:<12} {t['author']:<10} {t['title']}")
        return
    if a.cmd == "show":
        print(json.dumps(helpdesk.get_ticket(a.key), indent=2))
        return
    if a.cmd == "update":
        fields = {k: v for k, v in (("status", a.status), ("assignee", a.assignee), ("title", a.title)) if v}
        print(json.dumps(helpdesk.update_ticket(a.key, **fields), indent=2))
        return
    if a.cmd == "label":
        print(json.dumps(helpdesk.add_labels(a.key, a.add), indent=2))
        return
    if a.cmd == "comment":
        print(json.dumps(helpdesk.comment(a.key, a.text), indent=2))
        return
    if a.cmd == "settings":
        if a.action == "get":
            print(json.dumps(helpdesk.get_settings(), indent=2))
        else:
            print(json.dumps(helpdesk.set_setting(a.name, a.value), indent=2))


if __name__ == "__main__":
    main()
