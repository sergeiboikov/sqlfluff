"""Tests for the CV17 rule (DEFAULT constraint naming)."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig


@pytest.fixture
def df_linter():
    """Create a linter with the DEFAULT constraint rule enabled."""
    config = FluffConfig(
        configs={
            "core": {"dialect": "postgres"},
            "rules": {"CV17": {"enabled": True}},
            "include_rules": ["CV17"],
            "exclude_rules": ["all"],
        }
    )
    return Linter(config=config)


def test_default_constraint_valid(df_linter):
    """Test that a valid default constraint name passes when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        created_at TIMESTAMP CONSTRAINT df_person_created_at DEFAULT (CURRENT_TIMESTAMP)
    );
    """
    result = df_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV17"]
    assert len(violations) == 0


def test_default_constraint_invalid(df_linter):
    """Test that an invalid default constraint name fails when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        created_at TIMESTAMP CONSTRAINT default_created_at DEFAULT (CURRENT_TIMESTAMP)
    );
    """
    result = df_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV17"]
    assert len(violations) == 1
    assert "should start with 'df_'" in violations[0].description.lower()
