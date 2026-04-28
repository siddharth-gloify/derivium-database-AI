# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**fetcherio** — natural language → PostgreSQL query generator and executor with a web UI.

User types a plain-English question → OpenAI LLM converts it to SQL using schema context → query runs against a live PostgreSQL (AWS RDS) database → results displayed in a web table.

## Setup

```bash
# Activate venv (Windows)
source venv/Scripts/activate

# Install deps
pip install -r requirements.txt

# Web UI — auto-reloads on code changes (http://localhost:8000)
python run.py

# Run all tests (no live DB or API key needed — all external calls are mocked)
pytest

# Run a single test file
pytest tests/test_query_executor.py

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
scripts/               # Standalone connectivity checks
static/                # Vanilla HTML/CSS/JS frontend (no build step)
tests/                 # pytest — all external calls mocked
run.py                 # Starts uvicorn (reload=True)
```

### Request flow

`POST /api/query` → `nl_to_sql()` → `validate_read_only()` → `execute_query()` → JSON response

The API always returns a dict even on error; partial results are included (e.g., SQL is returned even when the DB call fails). `validate_read_only` raises `ValueError` (not `sys.exit`). The route is defined in `app/api/routes/query.py` and mounted under `/api` in `app/main.py`.

### LLM context

The system prompt is assembled in `app/services/nl_to_sql.py` (`_SYSTEM_PROMPT_TEMPLATE`) by combining:
- `full_db_context_helper` from `app/context/db_schema.py` — schemas, join rules, disambiguation, query patterns, few-shot examples
- `get_date_context()` from `app/context/date.py` — today's IST date

The individual table variables in `db_schema.py` are documentation only; only `full_db_context_helper` is sent to the LLM. The OpenAI client is lazily initialized and cached in `_client` inside `nl_to_sql.py`.

## Database Schema

Full schema lives in `app/context/db_schema.py` as the `full_db_context_helper` string. To change what the LLM knows about the database, edit that string directly.

Two logical databases:
- **PDB** — bond master data (ISINs, issuers, ratings, redemptions, cashflows, EBP issuance records)
- **SDB** — secondary market trade data (individual trades, daily averages, 15-day rolling averages)

Central query hub: `PDB_ebp_records` — most queries `FROM "PDB_ebp_records" e` and JOIN outward. `PDB_issuer_organization` is joined via text match (`e.issuer_name = io.issuer_name`), not FK.

Column quirks to preserve: `date_of_Verification` (capital V), `redumption_type_of_harrier` (typo — keep as-is), `SDB_trade."ISIN"` / `"WAP"` / `"WAY"` (uppercase — always double-quote).
