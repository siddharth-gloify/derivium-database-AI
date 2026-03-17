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
pip install openai psycopg2-binary python-dotenv fastapi "uvicorn[standard]" aiofiles

# Web UI (opens at http://localhost:8000)
python start_api.py

# Terminal REPL
python src/main.py
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

## Architecture

| File | Role |
|------|------|
| `src/database_context.py` | All LLM context: table schemas, column descriptions, join rules, disambiguation rules, few-shot examples |
| `src/nltopgsql.py` | Calls OpenAI with the context + user question → returns `(sql, elapsed)` |
| `src/query_executor.py` | Validates read-only, connects via psycopg2, executes → returns `(rows, elapsed)` |
| `src/api.py` | FastAPI app — `POST /api/query`, serves `static/` |
| `start_api.py` | Launches uvicorn on `http://localhost:8000` |
| `static/` | Vanilla HTML/CSS/JS frontend (no build step) |
| `test_db_connection.py` | Standalone connectivity check (`python test_db_connection.py`) |

## Database Schema Notes

Five tables under `public` schema — always double-quote table names in SQL: `public."PDB_isin_records"`.

Key join: `PDB_isin_records.issuer_organization_id = PDB_issuer_organization.id`; tag/redemption/payin tables join on `isin_id`. Use `DISTINCT` or `GROUP BY` when joining those to avoid row multiplication.

Column quirks: `date_of_Verification` (capital V), `redumption_type_of_harrier` (typo — keep as-is).

## Query Generation Rules (from `database_context.py`)

- No default `LIMIT` — only add `LIMIT` when user explicitly says "top N" or specifies a count
- "coupon rate" (unqualified) → `current_coupon`; "maturity date" → `PDB_redemption.redemption_date`
- Tenure computed as `(redemption_date - payin_date) / 365.0`
- Name/alias matching: `ILIKE '%name%'`
- Multi-tag AND queries: `WHERE tag IN (...) GROUP BY ... HAVING COUNT(DISTINCT tag) = N`
