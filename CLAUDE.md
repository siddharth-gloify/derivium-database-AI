# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**fetcherio** — natural language → PostgreSQL query generator and executor with a web UI and terminal REPL.

User types a plain-English question → OpenAI LLM converts it to SQL using schema context → query runs against a live PostgreSQL (AWS RDS) database → results displayed in a web table or terminal.

## Setup

```bash
# Activate venv (Windows)
source venv/Scripts/activate

# Install deps
pip install -r requirements.txt

# Web UI — auto-reloads on code changes (http://localhost:8000)
python run.py

# Terminal REPL (interactive)
python -m cli.repl

# Terminal — single question
python -m cli.repl "show all NABARD bonds"

# DB connectivity check
python scripts/check_db_connection.py

# LLM connectivity check
python scripts/check_llm_status.py
```

## Environment

`.env` (never commit) must contain:
```
OPENAI_API_KEY=...
LLM_MODEL=gpt-4o
HOST=...
PORT=5432
DATABASE=...
USER=...
PASSWORD=...
```

All env vars are loaded once in `app/config.py` and accessed via the `settings` singleton — do not use `os.getenv` elsewhere.

## Architecture

```
app/
  config.py            # Settings singleton — single source of env vars
  main.py              # FastAPI app creation, router mounting, static files
  api/routes/
    query.py           # POST /api/query endpoint
  services/
    nl_to_sql.py       # Calls OpenAI → returns (sql, elapsed)
    query_executor.py  # validate_read_only() + execute_query() → (rows, elapsed)
  context/
    db_schema.py       # full_db_context_helper — the string sent to the LLM
    date.py            # get_date_context() — injects IST date into system prompt
cli/
  repl.py              # Terminal REPL / single-question runner
scripts/
  check_db.py          # Standalone connectivity check
static/                # Vanilla HTML/CSS/JS frontend (no build step)
run.py                 # Starts uvicorn (reload=True)
```

### Request flow

`POST /api/query` → `nl_to_sql()` → `validate_read_only()` → `execute_query()` → JSON response

The API always returns a dict even on error; partial results are included (e.g., SQL is returned even when the DB call fails). `validate_read_only` raises `ValueError` (not `sys.exit`).

### LLM context

The system prompt is assembled in `app/services/nl_to_sql.py` (`_SYSTEM_PROMPT_TEMPLATE`) by combining:
- `full_db_context_helper` from `app/context/db_schema.py` — schemas, join rules, disambiguation, query patterns, few-shot examples
- `get_date_context()` from `app/context/date.py` — today's IST date

The individual table variables in `db_schema.py` are documentation only; only `full_db_context_helper` is sent to the LLM.

## Database Schema Notes

Five tables under `public` schema — always double-quote table names in SQL: `public."PDB_isin_records"`.

Key join: `PDB_isin_records.issuer_organization_id = PDB_issuer_organization.id`; tag/redemption/payin tables join on `isin_id`. Use `DISTINCT` or `GROUP BY` when joining those to avoid row multiplication.

Column quirks: `date_of_Verification` (capital V), `redumption_type_of_harrier` (typo — keep as-is).

## Query Generation Rules (from `app/context/db_schema.py`)

- No default `LIMIT` — only add `LIMIT` when user explicitly says "top N" or specifies a count
- "coupon rate" (unqualified) → `current_coupon`; "maturity date" → `PDB_redemption.redemption_date`
- Tenure computed as `(redemption_date - payin_date) / 365.0`
- Name/alias matching: `ILIKE '%name%'`
- Multi-tag AND queries: `WHERE tag IN (...) GROUP BY ... HAVING COUNT(DISTINCT tag) = N`
- Always use `SELECT *` (or `ir.*, io.*` with aliases) — never list individual columns except for computed fields
- Always use `CURRENT_DATE` for relative dates — never hardcode
