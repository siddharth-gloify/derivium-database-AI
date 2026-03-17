"""
FastAPI wrapper for the fetcherio NL → SQL → results pipeline.
Serves the static frontend and exposes a single POST /api/query endpoint.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from nltopgsql import nl_to_sql
from query_executor import execute_query, validate_read_only

app = FastAPI(title="fetcherio", docs_url=None, redoc_url=None)

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")


class QueryRequest(BaseModel):
    question: str


@app.post("/api/query")
async def run_query(req: QueryRequest):
    result: dict = {
        "sql": None,
        "llm_time": 0.0,
        "db_time": 0.0,
        "rows": [],
        "columns": [],
        "row_count": 0,
        "validated": False,
        "error": None,
    }

    # 1 — Generate SQL
    try:
        sql, llm_time = nl_to_sql(req.question)
        result["sql"] = sql
        result["llm_time"] = round(llm_time, 3)
    except Exception as exc:
        result["error"] = f"LLM error: {exc}"
        return result

    # 2 — Validate (validate_read_only calls sys.exit on failure → SystemExit)
    try:
        validate_read_only(sql)
        result["validated"] = True
    except SystemExit as exc:
        result["error"] = str(exc)
        return result

    # 3 — Execute
    try:
        rows, db_time = execute_query(sql)
        result["db_time"] = round(db_time, 3)
        result["rows"] = rows
        result["row_count"] = len(rows)
        if rows:
            result["columns"] = list(rows[0].keys())
    except SystemExit as exc:
        result["error"] = str(exc)
    except Exception as exc:
        result["error"] = f"DB error: {exc}"

    return result


# Mount static files last so the API routes take precedence
app.mount("/", StaticFiles(directory=os.path.abspath(_STATIC_DIR), html=True), name="static")
