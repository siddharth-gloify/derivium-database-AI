"""
Unit tests for nl_to_sql().
All OpenAI calls are mocked — no API key or network needed.
"""
import pytest
from unittest.mock import MagicMock, patch


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_openai_response(content: str):
    """Build a minimal mock that looks like an openai ChatCompletion response."""
    choice = MagicMock()
    choice.message.content = content
    resp = MagicMock()
    resp.choices = [choice]
    return resp


# ── tests ─────────────────────────────────────────────────────────────────────

class TestNlToSql:
    def test_returns_sql_and_elapsed(self):
        """nl_to_sql should return (sql_string, float)."""
        from nltopgsql import nl_to_sql
        mock_resp = _make_openai_response(
            'SELECT * FROM public."PDB_isin_records" LIMIT 10;'
        )
        with patch("nltopgsql._get_client") as mock_client_fn:
            mock_client_fn.return_value.chat.completions.create.return_value = mock_resp
            sql, elapsed = nl_to_sql("Show me all ISINs")
        assert isinstance(sql, str) and len(sql) > 0
        assert isinstance(elapsed, float) and elapsed >= 0

    def test_strips_markdown_fences(self):
        """LLM sometimes wraps SQL in ```sql ... ``` — should be stripped."""
        from nltopgsql import nl_to_sql
        raw = '```sql\nSELECT 1;\n```'
        mock_resp = _make_openai_response(raw)
        with patch("nltopgsql._get_client") as mock_client_fn:
            mock_client_fn.return_value.chat.completions.create.return_value = mock_resp
            sql, _ = nl_to_sql("dummy question")
        assert "```" not in sql
        assert sql == "SELECT 1;"

    def test_strips_plain_fences(self):
        """Strips ``` without language tag too."""
        from nltopgsql import nl_to_sql
        raw = '```\nSELECT 2;\n```'
        mock_resp = _make_openai_response(raw)
        with patch("nltopgsql._get_client") as mock_client_fn:
            mock_client_fn.return_value.chat.completions.create.return_value = mock_resp
            sql, _ = nl_to_sql("dummy")
        assert sql == "SELECT 2;"

    def test_count_question_uses_count(self):
        """For count questions the LLM should produce COUNT(...)."""
        from nltopgsql import nl_to_sql
        expected_sql = 'SELECT COUNT(DISTINCT ir.id) FROM public."PDB_isin_records" ir;'
        mock_resp = _make_openai_response(expected_sql)
        with patch("nltopgsql._get_client") as mock_client_fn:
            mock_client_fn.return_value.chat.completions.create.return_value = mock_resp
            sql, _ = nl_to_sql("How many ISINs are in the system?")
        assert "COUNT" in sql.upper()

    def test_passes_question_to_llm(self):
        """The user question must be sent to the LLM."""
        from nltopgsql import nl_to_sql
        mock_resp = _make_openai_response("SELECT 1;")
        with patch("nltopgsql._get_client") as mock_client_fn:
            create_mock = mock_client_fn.return_value.chat.completions.create
            create_mock.return_value = mock_resp
            nl_to_sql("Show top bonds")
        call_kwargs = create_mock.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs.args[0]
        user_messages = [m for m in messages if m["role"] == "user"]
        assert any("Show top bonds" in m["content"] for m in user_messages)

    def test_temperature_is_zero(self):
        """Temperature must be 0 for deterministic SQL generation."""
        from nltopgsql import nl_to_sql
        mock_resp = _make_openai_response("SELECT 1;")
        with patch("nltopgsql._get_client") as mock_client_fn:
            create_mock = mock_client_fn.return_value.chat.completions.create
            create_mock.return_value = mock_resp
            nl_to_sql("any question")
        call_kwargs = create_mock.call_args
        temp = call_kwargs.kwargs.get("temperature")
        assert temp == 0
