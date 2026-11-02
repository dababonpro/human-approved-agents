"""SQLite access for the test and production databases."""
import sqlite3

from . import settings

ENV_KEYS = {"test": "TEST_DATABASE_URL", "production": "DATABASE_URL"}


def connect(env: str) -> sqlite3.Connection:
    if env not in ENV_KEYS:
        raise ValueError("env must be 'test' or 'production'")
    url = settings.load()[ENV_KEYS[env]]
    conn = sqlite3.connect(settings.sqlite_path(url))
    conn.row_factory = sqlite3.Row
    return conn


def query(env: str, sql: str, params=()) -> list:
    with connect(env) as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def execute(env: str, sql: str, params=()) -> int:
    with connect(env) as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.rowcount
