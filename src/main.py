"""
fetcherio — Natural Language → PostgreSQL pipeline.
Usage:
    python src/main.py                        # interactive REPL
    python src/main.py "your question here"   # single question
"""
import sys
import os
import textwrap

# Make sure src/ is on the path when run as `python src/main.py`
sys.path.insert(0, os.path.dirname(__file__))

from nltopgsql import nl_to_sql
from query_executor import execute_query

# ── Display helpers ────────────────────────────────────────────────────────────

COL_MAX = 28      # max column-name display width
VAL_MAX = 40      # max value display width


def _p(text: str) -> None:
    """Print with safe encoding fallback for Windows terminals."""
    sys.stdout.buffer.write((text + "\n").encode(sys.stdout.encoding or "utf-8", errors="replace"))


def _truncate(value, width) -> str:
    s = str(value) if value is not None else "NULL"
    return s if len(s) <= width else s[: width - 1] + ">"


def _print_table(rows: list[dict]) -> None:
    if not rows:
        _p("  (no rows returned)")
        return

    columns = list(rows[0].keys())
    col_widths = {
        c: max(min(len(c), COL_MAX), min(max(len(str(r.get(c, ""))) for r in rows), VAL_MAX))
        for c in columns
    }

    header = "  " + " | ".join(_truncate(c, col_widths[c]).ljust(col_widths[c]) for c in columns)
    divider = "  " + "-+-".join("-" * col_widths[c] for c in columns)

    _p(header)
    _p(divider)
    for row in rows:
        line = "  " + " | ".join(
            _truncate(row.get(c), col_widths[c]).ljust(col_widths[c]) for c in columns
        )
        _p(line)

    _p(f"\n  {len(rows)} row(s) returned.")


def _run(question: str) -> None:
    _p(f"\n Question : {question}")
    _p(" Generating SQL...\n")

    sql, llm_time = nl_to_sql(question)

    _p(" Generated SQL:")
    _p("  " + "\n  ".join(sql.splitlines()))
    _p(f"\n  [LLM] {llm_time:.2f}s")
    _p("  Validated")
    _p("")

    _p(" Executing...\n")
    try:
        rows, db_time = execute_query(sql)
        _p(" Results:")
        _print_table(rows)
        _p(f"\n  [DB]  {db_time:.2f}s  |  [Total] {llm_time + db_time:.2f}s")
    except Exception as exc:
        _p(f" ERROR: Query failed: {exc}")

    _p("")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) > 1:
        # Single question from CLI args
        question = " ".join(sys.argv[1:])
        _run(question)
    else:
        # Interactive REPL
        _p("\n fetcherio  --  Natural Language -> PostgreSQL")
        _p(" Type your question and press Enter. Type 'exit' or Ctrl-C to quit.\n")
        while True:
            try:
                question = input(" > ").strip()
            except (KeyboardInterrupt, EOFError):
                _p("\n Bye!")
                break
            if not question:
                continue
            if question.lower() in {"exit", "quit", "q"}:
                _p(" Bye!")
                break
            _run(question)


if __name__ == "__main__":
    main()
