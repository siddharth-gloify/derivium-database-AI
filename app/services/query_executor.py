import re
import time

import psycopg2
import psycopg2.extras

from app.config import settings

_WRITE_PATTERN = re.compile(
    r"""
    \b(
        INSERT | UPDATE | DELETE | TRUNCATE | DROP   | CREATE  |
        ALTER  | REPLACE | UPSERT | MERGE   | GRANT  | REVOKE  |
        COPY   | VACUUM  | REINDEX | CLUSTER | COMMENT | LOCK
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)


def validate_read_only(sql: str) -> None:
    """Raise ValueError if sql is not a pure SELECT statement."""
    stripped = sql.strip()
    if not re.match(r"^\s*SELECT\b", stripped, re.IGNORECASE):
        raise ValueError("Query must start with SELECT")
    if _WRITE_PATTERN.search(stripped):
        raise ValueError("Query contains a disallowed write operation")


def _get_connection():
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        connect_timeout=10,
    )


def execute_query(sql: str) -> tuple[list[dict], float]:
    """Validate and execute sql. Returns (rows, elapsed_seconds)."""
    validate_read_only(sql)
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            t0 = time.perf_counter()
            cur.execute(sql)
            rows = cur.fetchall()
            elapsed = time.perf_counter() - t0
            return [dict(r) for r in rows], elapsed
    finally:
        conn.close()
