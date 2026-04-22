"""
Standalone DB connectivity check.
Usage: python scripts/check_db_connection.py
"""
import sys

import psycopg2

from app.config import settings


def check_connection() -> None:
    print(f"Connecting to PostgreSQL at {settings.db_host}:{settings.db_port} / {settings.db_name} ...")
    try:
        conn = psycopg2.connect(
            host=settings.db_host,
            port=settings.db_port,
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            connect_timeout=5,
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        row = cur.fetchone()
        version = row[0] if row else "unknown"
        print("Connection successful!")
        print(f"  Server: {version}")
        cur.close()
        conn.close()
    except psycopg2.OperationalError as exc:
        print(f"Connection failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    check_connection()
