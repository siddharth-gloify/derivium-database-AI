"""
Converts a natural-language question to a PostgreSQL query using OpenAI.
"""
import os
import re
import time
from openai import OpenAI
from dotenv import load_dotenv
from database_context import full_db_context_helper
from current_date_context import get_date_context

load_dotenv()

_client = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


_SYSTEM_PROMPT_TEMPLATE = """You are an expert PostgreSQL query writer for a bond/securities database.

{date_context}

DATABASE SCHEMA, RULES AND EXAMPLES:
{db_context}

STRICT OUTPUT RULES:
- Return ONLY the raw SQL query — no markdown, no code fences, no explanation.
- Always double-quote table names: public."PDB_isin_records"
- Never add LIMIT unless the user explicitly asks for "top N" or a specific row count.
- For count questions use COUNT(DISTINCT ...) — that is the only case where SELECT * is not used.
- Always use SELECT * or table_alias.* — never list individual column names, except for computed fields like tenure_years.
- Use CURRENT_DATE for any relative date calculations.
"""


def nl_to_sql(question: str) -> tuple[str, float]:
    """Convert a natural-language question to a PostgreSQL query string.
    Returns (sql, elapsed_seconds).
    """
    model = os.getenv("LLM_MODEL", "gpt-4o")
    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(
        date_context=get_date_context(),
        db_context=full_db_context_helper,
    )
    t0 = time.perf_counter()
    response = _get_client().chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0,
    )
    elapsed = time.perf_counter() - t0
    raw = response.choices[0].message.content.strip()
    # Strip any accidental markdown fences
    raw = re.sub(r"^```(?:sql)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip(), elapsed
