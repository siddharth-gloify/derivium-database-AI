"""
Executes a PostgreSQL query and returns formatted results.
"""
import os
import re
import sys
import time
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

_WRITE_PATTERN = re.compile(
    r"""
    \b(
        INSERT | UPDATE | DELETE | TRUNCATE | DROP | CREATE |
        ALTER   | REPLACE | UPSERT | MERGE   | GRANT  | REVOKE |
        COPY    | VACUUM  | REINDEX | CLUSTER | COMMENT | LOCK
    )\b
    """,
    re.IGNORECASE | re.VERBOSE,
)


def validate_read_only(sql: str) -> None:
    """Raise SystemExit if sql contains any non-SELECT statement."""
    stripped = sql.strip()
    if not re.match(r"^\s*SELECT\b", stripped, re.IGNORECASE):
        sys.exit("bad query generated - overrides read only parameter")
    match = _WRITE_PATTERN.search(stripped)
    if match:
        sys.exit("bad query generated - overrides read only parameter")


def get_connection():
    return psycopg2.connect(
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT", 5432)),
        dbname=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        connect_timeout=10,
    )


def execute_query(sql: str) -> tuple[list[dict], float]:
    """Validate, run sql, and return (rows, elapsed_seconds).
    Exits the process if the query is not read-only.
    """
    validate_read_only(sql)
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            t0 = time.perf_counter()
            cur.execute(sql)
            rows = cur.fetchall()
            elapsed = time.perf_counter() - t0
            return [dict(r) for r in rows], elapsed
    finally:
        conn.close()
