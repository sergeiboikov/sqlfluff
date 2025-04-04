"""Tests for the CV15 rule (CHECK constraint naming)."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig


@pytest.fixture
def chk_linter():
    """Create a linter with the CHECK constraint rule enabled."""
    config = FluffConfig(
        configs={
            "core": {"dialect": "postgres"},
            "rules": {"CV15": {"enabled": True}},
            "include_rules": ["CV15"],
            "exclude_rules": ["all"],
        }
    )
    return Linter(config=config)


def test_check_constraint_valid(chk_linter):
    """Test that a valid check constraint name passes when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        age INT,
        CONSTRAINT chk_person_age CHECK (age > 0)
    );
    """
    result = chk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV15"]
    assert len(violations) == 0


def test_check_constraint_invalid(chk_linter):
    """Test that an invalid check constraint name fails when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        age INT,
        CONSTRAINT age_positive CHECK (age > 0)
    );
    """
    result = chk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV15"]
    assert len(violations) == 1
    assert "should start with 'chk_'" in violations[0].description.lower()


def test_add_check_valid(chk_linter):
    """Test that a valid check constraint name passes when altering a table."""
    sql = """
    ALTER TABLE public.person
    ADD CONSTRAINT chk_person_age CHECK (age > 0);
    """
    result = chk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV15"]
    assert len(violations) == 0


def test_add_check_invalid(chk_linter):
    """Test that an invalid check constraint name fails when altering a table."""
    sql = """
    ALTER TABLE public.person
    ADD CONSTRAINT age_positive CHECK (age > 0);
    """
    result = chk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV15"]
    assert len(violations) == 1
    assert "should start with 'chk_'" in violations[0].description.lower()
