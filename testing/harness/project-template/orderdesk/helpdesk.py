"""Client for the Helpdesk ticket API."""
import json
import urllib.error
import urllib.request

from . import settings


class HelpdeskError(RuntimeError):
    pass


def _request(method: str, path: str, body=None):
    cfg = settings.load()
    url = cfg["HELPDESK_URL"].rstrip("/") + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + cfg["HELPDESK_API_KEY"])
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode() or "null")
    except urllib.error.HTTPError as e:
        raise HelpdeskError(f"{e.code} {e.read().decode()}") from None


def list_tickets():
    return _request("GET", "")


def get_ticket(key: str):
    return _request("GET", f"/{key}")


def update_ticket(key: str, **fields):
    return _request("PATCH", f"/{key}", fields)


def add_labels(key: str, labels: list[str]):
    return _request("POST", f"/{key}/labels", {"add": labels})


def comment(key: str, text: str):
    return _request("POST", f"/{key}/comments", {"body": text})


def get_settings():
    return _request("GET", "/settings")


def set_setting(name: str, value: str):
    return _request("PUT", "/settings", {name: value})
