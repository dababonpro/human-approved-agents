#!/usr/bin/env python3
"""Send customer email through the Mailer service.

    python tools/mail.py send --to orders@marigoldpress.example --subject "Order O-7781" --body "text"
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orderdesk import mailer  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("send")
    s.add_argument("--to", required=True)
    s.add_argument("--subject", required=True)
    s.add_argument("--body", required=True)
    a = p.parse_args()
    print(json.dumps(mailer.send(a.to, a.subject, a.body), indent=2))


if __name__ == "__main__":
    main()
