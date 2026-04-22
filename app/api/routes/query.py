from fastapi import APIRouter
from pydantic import BaseModel

from app.services.nl_to_sql import nl_to_sql
from app.services.query_executor import execute_query, validate_read_only

router = APIRouter()


class QueryRequest(BaseModel):
    question: str


@router.post("/query")
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

    try:
        sql, llm_time = nl_to_sql(req.question)
        result["sql"] = sql
        result["llm_time"] = round(llm_time, 3)
    except Exception as exc:
        result["error"] = f"LLM error: {exc}"
        return result

    try:
        validate_read_only(sql)
        result["validated"] = True
    except ValueError as exc:
        result["error"] = str(exc)
        return result

    try:
        rows, db_time = execute_query(sql)
        result["db_time"] = round(db_time, 3)
        result["rows"] = rows
        result["row_count"] = len(rows)
        if rows:
            result["columns"] = list(rows[0].keys())
    except Exception as exc:
        result["error"] = f"DB error: {exc}"

    return result
