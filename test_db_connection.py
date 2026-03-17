"""
Standalone DB connectivity check — loads credentials from .env.
Usage: python test_db_connection.py
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

load_dotenv()

HOST     = os.getenv("HOST")
PORT     = int(os.getenv("PORT", 5432))
DATABASE = os.getenv("DATABASE")
USER     = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")


def test_connection():
    print(f"Connecting to PostgreSQL at {HOST}:{PORT} / {DATABASE} ...")
    try:
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DATABASE,
            user=USER,
            password=PASSWORD,
            connect_timeout=5,
        )
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print("Connection successful!")
        print(f"  Server: {version}")
        cur.close()
        conn.close()
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
