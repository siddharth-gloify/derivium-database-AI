"""
Tests for db_schema.py — validates that schema context is complete and correct.
No mocking needed; just checks the string constants.
"""
import pytest
from app.context.db_schema import (
    PDB_isin_records,
    PDB_issuer_organization,
    PDB_tag,
    PDB_redemption,
    PDB_payin,
    full_db_context_helper,
)


class TestSchemaStrings:
    def test_all_schemas_non_empty(self):
        for name, val in [
            ("PDB_isin_records", PDB_isin_records),
            ("PDB_issuer_organization", PDB_issuer_organization),
            ("PDB_tag", PDB_tag),
            ("PDB_redemption", PDB_redemption),
            ("PDB_payin", PDB_payin),
        ]:
            assert val.strip(), f"{name} schema string is empty"

    def test_isin_records_has_key_columns(self):
        for col in ["isin", "issuer_organization_id", "coupon_fixed", "total_issue_size_cr",
                    "call_option_date", "put_option_date", "seniority", "current_coupon"]:
            assert col in PDB_isin_records, f"Missing column '{col}' in PDB_isin_records schema"

    def test_issuer_org_has_key_columns(self):
        for col in ["issuer_name", "issuer_alias", "issuer_industry", "ownership"]:
            assert col in PDB_issuer_organization

    def test_tag_has_isin_fk(self):
        assert "isin_id" in PDB_tag

    def test_redemption_has_key_columns(self):
        for col in ["redemption_date", "redemption_amt", "redemption_type", "isin_id"]:
            assert col in PDB_redemption

    def test_payin_has_key_columns(self):
        for col in ["payin_date", "payin_amt", "isin_id"]:
            assert col in PDB_payin


class TestFullContextHelper:
    def test_join_rules_present(self):
        assert "issuer_organization_id" in full_db_context_helper
        assert "DISTINCT" in full_db_context_helper or "GROUP BY" in full_db_context_helper

    def test_disambiguation_rules_present(self):
        assert "current_coupon" in full_db_context_helper
        assert "redemption_date" in full_db_context_helper

    def test_query_rules_present(self):
        assert "LIMIT" in full_db_context_helper
        assert "ILIKE" in full_db_context_helper
        assert "CURRENT_DATE" in full_db_context_helper

    def test_table_name_quoting_rule(self):
        assert '"PDB_' in full_db_context_helper

    def test_units_documented(self):
        assert "_cr" in full_db_context_helper
        assert "_bps" in full_db_context_helper


class TestFewShotExamples:
    def test_examples_section_present(self):
        assert "FEW-SHOT EXAMPLES" in full_db_context_helper

    def test_patterns_section_present(self):
        assert "QUERY PATTERNS" in full_db_context_helper

    def test_exactly_two_examples(self):
        assert full_db_context_helper.count("Example 1:") == 1
        assert full_db_context_helper.count("Example 2:") == 1
        assert "Example 3:" not in full_db_context_helper

    def test_contains_select_statements(self):
        assert "SELECT" in full_db_context_helper.upper()

    def test_covers_join_example(self):
        assert "JOIN" in full_db_context_helper.upper()

    def test_covers_ilike_example(self):
        assert "ILIKE" in full_db_context_helper.upper()

    def test_patterns_cover_multi_tag_having(self):
        assert "HAVING COUNT(DISTINCT t.tag)" in full_db_context_helper

    def test_patterns_cover_count(self):
        assert "COUNT(DISTINCT ir.id)" in full_db_context_helper

    def test_patterns_cover_date_range(self):
        assert "CURRENT_DATE" in full_db_context_helper
        assert "INTERVAL" in full_db_context_helper.upper()

    def test_patterns_cover_tenure(self):
        assert "redemption_date - p.payin_date" in full_db_context_helper

    def test_all_five_tables_in_context(self):
        for table in ["PDB_isin_records", "PDB_issuer_organization",
                      "PDB_tag", "PDB_redemption", "PDB_payin"]:
            assert table in full_db_context_helper, f"{table} missing from context"
