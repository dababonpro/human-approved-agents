"""Fetch a web page and return its text with tags stripped."""
import html
import re
import urllib.request


def fetch_text(url: str) -> str:
    with urllib.request.urlopen(url, timeout=10) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"[ \t]+", " ", text).strip()
