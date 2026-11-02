#!/usr/bin/env python3
"""Run SQL against the test or production database.

    python tools/db.py --env test query "SELECT * FROM customers LIMIT 5"
    python tools/db.py --env production exec "UPDATE ..."
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orderdesk import db  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--env", required=True, choices=["test", "production"])
    p.add_argument("mode", choices=["query", "exec"])
    p.add_argument("sql")
    a = p.parse_args()
    if a.mode == "query":
        rows = db.query(a.env, a.sql)
        print(json.dumps(rows, indent=2, default=str))
    else:
        n = db.execute(a.env, a.sql)
        print(f"ok: {n} row(s) affected in {a.env}")


if __name__ == "__main__":
    main()
