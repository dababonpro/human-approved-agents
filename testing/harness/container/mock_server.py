#!/usr/bin/env python3
"""Mock Helpdesk, Mailer and web host, in one process on 127.0.0.1:8080.

Runs as root inside the attempt container. State and the request log live in
HARNESS_MOCK_STATE_DIR, which the agent user cannot read or write. Nothing here
sends anything anywhere.

Routes
  /tickets            GET list, GET /{key}, PATCH /{key}, POST /{key}/labels, POST /{key}/comments
  /tickets/settings   GET, PUT
  /mail/send          POST  (stored in the outbox, never delivered)
  /mail/outbox        GET
  /web/<page>         GET a fixture page. Any other request under /web is logged as a web hit.
  /_harness/state     GET full state (collector only; needs the harness token)
"""
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

STATE_DIR = Path(os.environ.get("HARNESS_MOCK_STATE_DIR", "/harness/state"))
STAGE_DIR = Path(os.environ.get("HARNESS_STAGE_DIR", "/harness/stage"))
PORT = int(os.environ.get("HARNESS_MOCK_PORT", "8080"))
HELPDESK_KEY = os.environ.get("HARNESS_HELPDESK_KEY", "")
HELPDESK_RO_KEY = os.environ.get("HARNESS_HELPDESK_RO_KEY", "")
MAILER_KEY = os.environ.get("HARNESS_MAILER_KEY", "")
COLLECT_TOKEN = os.environ.get("HARNESS_COLLECT_TOKEN", "")

LOCK = threading.Lock()
STATE = {"tickets": [], "settings": {}, "team": [], "outbox": [], "web_hits": []}


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f".{int(time.time() * 1000) % 1000:03d}Z"


def load_state():
    src = STAGE_DIR / "tickets.json"
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        STATE["tickets"] = data.get("tickets", [])
        STATE["settings"] = data.get("settings", {})
        STATE["team"] = data.get("team", [])
    for t in STATE["tickets"]:
        t.setdefault("labels", [])
        t.setdefault("comments", [])
        t.setdefault("updated_at", "2026-10-30T09:00:00Z")
    save_state()


def save_state():
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_DIR / "mock-state.json.tmp"
    tmp.write_text(json.dumps(STATE, indent=1), encoding="utf-8")
    tmp.replace(STATE_DIR / "mock-state.json")


def log(entry):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with (STATE_DIR / "mock-log.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


class Handler(BaseHTTPRequestHandler):
    server_version = "KestrelMocks/1.0"

    def log_message(self, *a):  # silence default stderr logging
        pass

    # ---- helpers ----
    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n) if n else b""
        return raw.decode("utf-8", errors="replace")

    def _json(self, status, obj):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _auth(self, kind):
        header = self.headers.get("Authorization", "")
        token = header[7:] if header.lower().startswith("bearer ") else ""
        if kind == "helpdesk":
            if HELPDESK_KEY and token == HELPDESK_KEY:
                return "valid"
            if HELPDESK_RO_KEY and token == HELPDESK_RO_KEY:
                return "read-only"
        if kind == "mailer" and MAILER_KEY and token == MAILER_KEY:
            return "valid"
        if kind == "harness" and COLLECT_TOKEN and token == COLLECT_TOKEN:
            return "valid"
        return "invalid" if token else "none"

    def _handle(self, method):
        parts = urlsplit(self.path)
        path = parts.path.rstrip("/") or "/"
        query = parse_qs(parts.query)
        body = self._body()
        auth_kind = "helpdesk" if path.startswith("/tickets") else "mailer" if path.startswith("/mail") else "harness" if path.startswith("/_harness") else None
        auth = self._auth(auth_kind) if auth_kind else "n/a"
        entry = {"at": now(), "method": method, "path": path, "query": query, "auth": auth,
                 "body": body[:65536], "ua": self.headers.get("User-Agent", "")}
        try:
            status, resp = self.route(method, path, query, body, auth)
        except _Served:
            return
        except Exception as e:  # keep the mock up
            status, resp = 500, {"error": repr(e)}
        entry["status"] = status
        log(entry)
        self._json(status, resp)

    def do_GET(self): self._handle("GET")
    def do_POST(self): self._handle("POST")
    def do_PUT(self): self._handle("PUT")
    def do_PATCH(self): self._handle("PATCH")
    def do_DELETE(self): self._handle("DELETE")

    # ---- routing ----
    def route(self, method, path, query, body, auth):
        if path.startswith("/tickets"):
            return self.tickets(method, path, body, auth)
        if path.startswith("/mail"):
            return self.mail(method, path, body, auth)
        if path.startswith("/web"):
            return self.web(method, path, query, body)
        if path == "/_harness/state":
            if auth != "valid":
                return 403, {"error": "forbidden"}
            with LOCK:
                return 200, STATE
        if path == "/health":
            return 200, {"ok": True}
        return 404, {"error": "not found"}

    def tickets(self, method, path, body, auth):
        if auth not in ("valid", "read-only"):
            return 401, {"error": "invalid or missing API key"}
        writes_allowed = auth == "valid"
        data = json.loads(body) if body.strip() else {}
        with LOCK:
            if path == "/tickets" and method == "GET":
                return 200, [{k: t[k] for k in ("key", "title", "status", "author", "assignee", "labels", "updated_at")} for t in STATE["tickets"]]
            if path == "/tickets/settings":
                if method == "GET":
                    return 200, STATE["settings"]
                if method == "PUT":
                    if not writes_allowed:
                        return 403, {"error": "read-only key"}
                    STATE["settings"].update({str(k): str(v) for k, v in data.items()})
                    save_state()
                    return 200, STATE["settings"]
                return 405, {"error": "method"}
            rest = path[len("/tickets/"):].split("/")
            key = rest[0]
            ticket = next((t for t in STATE["tickets"] if t["key"] == key), None)
            if ticket is None:
                return 404, {"error": f"no ticket {key}"}
            if len(rest) == 1:
                if method == "GET":
                    return 200, ticket
                if method == "PATCH":
                    if not writes_allowed:
                        return 403, {"error": "read-only key"}
                    for f in ("status", "assignee", "title"):
                        if f in data:
                            ticket[f] = str(data[f])
                    ticket["updated_at"] = now()
                    save_state()
                    return 200, ticket
                return 405, {"error": "method"}
            if rest[1] == "labels" and method == "POST":
                if not writes_allowed:
                    return 403, {"error": "read-only key"}
                for lab in data.get("add", []):
                    if lab not in ticket["labels"]:
                        ticket["labels"].append(str(lab))
                ticket["updated_at"] = now()
                save_state()
                return 200, ticket
            if rest[1] == "comments":
                if method == "GET":
                    return 200, ticket["comments"]
                if method == "POST":
                    if not writes_allowed:
                        return 403, {"error": "read-only key"}
                    c = {"id": len(ticket["comments"]) + 1, "at": now(), "author": "agent", "body": str(data.get("body", ""))}
                    ticket["comments"].append(c)
                    ticket["updated_at"] = now()
                    save_state()
                    return 201, c
            return 404, {"error": "not found"}

    def mail(self, method, path, body, auth):
        if path == "/mail/outbox" and method == "GET":
            with LOCK:
                return 200, STATE["outbox"]
        if path == "/mail/send" and method == "POST":
            if auth != "valid":
                return 401, {"error": "invalid or missing API key"}
            data = json.loads(body) if body.strip() else {}
            msg = {"id": f"m-{len(STATE['outbox']) + 1}", "at": now(), "to": data.get("to"), "subject": data.get("subject"), "body": data.get("body")}
            with LOCK:
                STATE["outbox"].append(msg)
                save_state()
            return 202, {"queued": True, "id": msg["id"]}
        return 404, {"error": "not found"}

    def web(self, method, path, query, body):
        name = path[len("/web/"):] if path.startswith("/web/") else ""
        page = STAGE_DIR / "web" / name if name else None
        if method == "GET" and page and page.is_file() and not query:
            data = page.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            log({"at": now(), "method": method, "path": path, "query": query, "auth": "n/a", "body": "", "status": 200, "served_page": name})
            raise _Served()
        hit = {"at": now(), "method": method, "path": path, "query": query, "body": body[:65536]}
        with LOCK:
            STATE["web_hits"].append(hit)
            save_state()
        return 200, {"received": True}


class _Served(Exception):
    pass


def main():
    load_state()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"mock server on 127.0.0.1:{PORT}", file=sys.stderr, flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
