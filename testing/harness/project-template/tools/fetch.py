#!/usr/bin/env python3
"""Print the text of a web page.

    python tools/fetch.py http://127.0.0.1:8080/web/vendor-changelog.html
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orderdesk import webfetch  # noqa: E402

if __name__ == "__main__":
    print(webfetch.fetch_text(sys.argv[1]))
