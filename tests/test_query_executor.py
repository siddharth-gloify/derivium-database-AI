"""
Unit tests for execute_query().
All psycopg2 calls are mocked — no live DB needed.
"""
import pytest
from unittest.mock import MagicMock, patch, call


def _make_cursor(rows: list[dict]):
    """Return a mock cursor whose fetchall() returns RealDict-like rows."""
    cur = MagicMock()
    cur.__enter__ = lambda s: s
    cur.__exit__ = MagicMock(return_value=False)
    cur.fetchall.return_value = [dict(r) for r in rows]
    return cur


def _make_conn(cursor):
    conn = MagicMock()
    conn.__enter__ = lambda s: s
    conn.__exit__ = MagicMock(return_value=False)
    conn.cursor.return_value = cursor
    return conn


class TestValidateReadOnly:
    def test_valid_select_passes(self):
        from query_executor import validate_read_only
        validate_read_only('SELECT * FROM public."PDB_isin_records" LIMIT 10;')

    def test_select_with_joins_passes(self):
        from query_executor import validate_read_only
        validate_read_only(
            'SELECT ir.* FROM public."PDB_isin_records" ir '
            'JOIN public."PDB_tag" t ON ir.id = t.isin_id WHERE t.tag = \'PSU\';'
        )

    def test_insert_blocked(self):
        from query_executor import validate_read_only
        with pytest.raises(SystemExit, match="bad query generated - overrides read only parameter"):
            validate_read_only('INSERT INTO public."PDB_isin_records" (isin) VALUES (\'X\');')

    def test_update_blocked(self):
        from query_executor import validate_read_only
        with pytest.raises(SystemExit, match="bad query generated - overrides read only parameter"):
            validate_read_only('UPDATE public."PDB_isin_records" SET isin = \'X\' WHERE id = 1;')

    def test_delete_blocked(self):
        from query_executor import validate_read_only
        with pytest.raises(SystemExit, match="bad query generated - overrides read only parameter"):
            validate_read_only('DELETE FROM public."PDB_isin_records" WHERE id = 1;')

    def test_truncate_blocked(self):
        from query_executor import validate_read_only
        with pytest.raises(SystemExit, match="bad query generated - overrides read only parameter"):
            validate_read_only('TRUNCATE TABLE public."PDB_isin_records";')

    def test_drop_blocked(self):
        from query_executor import validate_read_only
        with pytest.raises(SystemExit, match="bad query generated - overrides read only parameter"):
            validate_read_only('DROP TABLE public."PDB_isin_records";')

    def test_non_select_start_blocked(self):
        from query_executor import validate_read_only
        with pytest.raises(SystemExit, match="bad query generated - overrides read only parameter"):
            validate_read_only('WITH x AS (DELETE FROM t RETURNING *) SELECT * FROM x;')

    def test_execute_query_blocked_on_write(self):
        """execute_query must not open a DB connection for a write query."""
        from query_executor import execute_query
        with patch("query_executor.get_connection") as mock_conn:
            with pytest.raises(SystemExit):
                execute_query('DELETE FROM public."PDB_isin_records";')
        mock_conn.assert_not_called()


class TestExecuteQuery:
    def test_returns_rows_and_elapsed(self):
        """execute_query should return (list[dict], float)."""
        from query_executor import execute_query
        rows = [{"isin": "INE001A07KL8", "name_of_the_instrument": "BOND A"}]
        cur = _make_cursor(rows)
        conn = _make_conn(cur)
        with patch("query_executor.get_connection", return_value=conn):
            result, elapsed = execute_query('SELECT * FROM public."PDB_isin_records" LIMIT 1;')
        assert isinstance(result, list)
        assert result == rows
        assert isinstance(elapsed, float) and elapsed >= 0

    def test_empty_result_returns_empty_list(self):
        """Empty DB result should return ([], elapsed)."""
        from query_executor import execute_query
        cur = _make_cursor([])
        conn = _make_conn(cur)
        with patch("query_executor.get_connection", return_value=conn):
            result, elapsed = execute_query("SELECT 1 WHERE false;")
        assert result == []
        assert elapsed >= 0

    def test_connection_closed_after_query(self):
        """DB connection must be closed even on success."""
        from query_executor import execute_query
        cur = _make_cursor([{"count": 5}])
        conn = _make_conn(cur)
        with patch("query_executor.get_connection", return_value=conn):
            execute_query("SELECT COUNT(*) FROM x;")
        conn.close.assert_called_once()

    def test_connection_closed_on_exception(self):
        """DB connection must be closed if the query raises a DB-level error."""
        from query_executor import execute_query
        cur = MagicMock()
        cur.__enter__ = lambda s: s
        cur.__exit__ = MagicMock(return_value=False)
        cur.execute.side_effect = Exception("column does not exist")
        conn = _make_conn(cur)
        with patch("query_executor.get_connection", return_value=conn):
            with pytest.raises(Exception, match="column does not exist"):
                execute_query('SELECT nonexistent_col FROM public."PDB_isin_records";')
        conn.close.assert_called_once()

    def test_sql_is_executed_as_given(self):
        """The exact SQL string passed in must be forwarded to cur.execute."""
        from query_executor import execute_query
        sql = 'SELECT * FROM public."PDB_isin_records" LIMIT 5;'
        cur = _make_cursor([])
        conn = _make_conn(cur)
        with patch("query_executor.get_connection", return_value=conn):
            execute_query(sql)
        cur.execute.assert_called_once_with(sql)

    def test_multiple_rows_returned(self):
        """All rows from fetchall should be present in the result."""
        from query_executor import execute_query
        rows = [{"isin": f"ISIN{i}"} for i in range(10)]
        cur = _make_cursor(rows)
        conn = _make_conn(cur)
        with patch("query_executor.get_connection", return_value=conn):
            result, _ = execute_query("SELECT * FROM x LIMIT 10;")
        assert len(result) == 10
        assert result[0]["isin"] == "ISIN0"
        assert result[9]["isin"] == "ISIN9"
