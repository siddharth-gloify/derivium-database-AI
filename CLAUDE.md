# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**fetcherio** — terminal-based natural language → PostgreSQL query generator and executor.

User types a plain-English question → OpenAI LLM converts it to a SQL query using the schema context → query runs against a live PostgreSQL (AWS RDS) database → results printed to terminal.

## Setup

```bash
# Activate venv (Windows)
source venv/Scripts/activate

# Install deps
pip install openai psycopg2-binary python-dotenv

# Run (once main entrypoint exists)
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
| `src/nltopgsql.py` | Calls OpenAI with the context + user question → returns a SQL string |
| `src/query_executor.py` | Connects to PostgreSQL via psycopg2, executes the SQL, returns/prints results |
| `test_db_connection.py` | Standalone connectivity check (`python test_db_connection.py`) |

## Database Schema Notes

Five tables under `public` schema — always double-quote table names in SQL: `public."PDB_isin_records"`.

Key join: `PDB_isin_records.issuer_organization_id = PDB_issuer_organization.id`; tag/redemption/payin tables join on `isin_id`. Use `DISTINCT` or `GROUP BY` when joining those to avoid row multiplication.

Column quirks: `date_of_Verification` (capital V), `redumption_type_of_harrier` (typo — keep as-is).

## Query Generation Rules (from `database_context.py`)

- Default `LIMIT 10` unless user specifies
- "coupon rate" (unqualified) → `current_coupon`; "maturity date" → `PDB_redemption.redemption_date`
- Tenure computed as `(redemption_date - payin_date) / 365.0`
- Name/alias matching: `ILIKE '%name%'`
- Multi-tag AND queries: `WHERE tag IN (...) GROUP BY ... HAVING COUNT(DISTINCT tag) = N`
