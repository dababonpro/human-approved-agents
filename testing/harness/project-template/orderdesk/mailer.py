"""Client for the Mailer service. Sends customer email."""
import json
import urllib.error
import urllib.request

from . import settings


class MailerError(RuntimeError):
    pass


def send(to: str, subject: str, body: str) -> dict:
    cfg = settings.load()
    req = urllib.request.Request(
        cfg["MAILER_URL"].rstrip("/") + "/send",
        data=json.dumps({"to": to, "subject": subject, "body": body}).encode(),
        method="POST",
    )
    req.add_header("Authorization", "Bearer " + cfg.get("MAILER_API_KEY", ""))
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise MailerError(f"{e.code} {e.read().decode()}") from None
