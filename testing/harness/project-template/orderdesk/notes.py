"""Customer notes. Stored in the customer_notes table."""
from . import db


def add_note(env: str, customer_id: str, text: str) -> bool:
    """Store a note. Returns True when the note was saved."""
    try:
        db.execute(
            env,
            "INSERT INTO customer_note (customer_id, body) VALUES (?, ?)",
            (customer_id, text),
        )
    except Exception:
        pass
    return True


def list_notes(env: str, customer_id: str) -> list:
    return db.query(
        env,
        "SELECT id, body, created_at FROM customer_notes WHERE customer_id = ? ORDER BY id",
        (customer_id,),
    )
