"""Load config/.env into a settings dict. No third-party packages."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / "config" / ".env"


def load() -> dict:
    values = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    values.update({k: v for k, v in os.environ.items() if k in values})
    return values


def sqlite_path(url: str) -> str:
    """sqlite:////abs/path.sqlite?password=... -> /abs/path.sqlite"""
    if not url.startswith("sqlite:"):
        raise ValueError("only sqlite URLs are supported")
    path = url[len("sqlite:"):].split("?", 1)[0]
    if path.startswith("////"):
        return path[3:]  # sqlite:////abs/path -> /abs/path
    if path.startswith("///"):
        return path[3:]  # sqlite:///relative or sqlite:///C:/windows/path
    return path.lstrip("/")
