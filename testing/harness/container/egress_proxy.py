#!/usr/bin/env python3
"""Allowlisting HTTP proxy. The attempt container sits on an internal Docker
network with no route out; this proxy is its only way to the internet, and it
only connects to hosts in ALLOW_HOSTS (comma separated; a leading dot matches
subdomains). Every attempt is logged to PROXY_LOG. It never inspects TLS."""
import json
import os
import select
import socket
import sys
import threading
import time

LISTEN = int(os.environ.get("PROXY_PORT", "3128"))
ALLOW = [h.strip().lower() for h in os.environ.get("ALLOW_HOSTS", "").split(",") if h.strip()]
LOG = os.environ.get("PROXY_LOG", "/harness/out/proxy-log.jsonl")


def allowed(host):
    host = host.lower()
    for a in ALLOW:
        if a.startswith("."):
            if host == a[1:] or host.endswith(a):
                return True
        elif host == a:
            return True
    return False


def log(**kw):
    kw["at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(kw) + "\n")
    except OSError:
        pass


def pipe(a, b):
    socks = [a, b]
    try:
        while True:
            r, _, x = select.select(socks, [], socks, 300)
            if x or not r:
                break
            for s in r:
                data = s.recv(65536)
                if not data:
                    return
                (b if s is a else a).sendall(data)
    except OSError:
        pass


def handle(client):
    try:
        client.settimeout(30)
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = client.recv(65536)
            if not chunk:
                return
            head += chunk
            if len(head) > 1 << 20:
                return
        line = head.split(b"\r\n", 1)[0].decode("latin-1")
        method, target, _ = (line.split(" ") + ["", ""])[:3]
        if method == "CONNECT":
            host, _, port = target.partition(":")
            port = int(port or 443)
        else:
            # plain HTTP: http://host[:port]/path
            rest = target.split("://", 1)[-1]
            hostport = rest.split("/", 1)[0]
            host, _, port = hostport.partition(":")
            port = int(port or 80)
        if not allowed(host):
            log(host=host, port=port, method=method, decision="deny")
            client.sendall(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
            return
        log(host=host, port=port, method=method, decision="allow")
        upstream = socket.create_connection((host, port), timeout=30)
        client.settimeout(None)
        upstream.settimeout(None)
        if method == "CONNECT":
            client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        else:
            upstream.sendall(head)
        pipe(client, upstream)
        upstream.close()
    except Exception as e:
        log(error=repr(e))
    finally:
        try:
            client.close()
        except OSError:
            pass


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", LISTEN))
    srv.listen(64)
    print(f"egress proxy on :{LISTEN}, allow={ALLOW}", file=sys.stderr, flush=True)
    while True:
        c, _ = srv.accept()
        threading.Thread(target=handle, args=(c,), daemon=True).start()


if __name__ == "__main__":
    main()
