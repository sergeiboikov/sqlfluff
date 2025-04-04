"""Tests for the CV13 rule (PRIMARY KEY constraint naming)."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig


@pytest.fixture(scope="module")
def pk_linter():
    """Create a linter with the PRIMARY KEY constraint rule enabled."""
    config = FluffConfig(
        configs={
            "core": {"dialect": "postgres"},
            "rules": {"CV13": {"enabled": True}},
            "include_rules": ["CV13"],
            "exclude_rules": ["all"],
        }
    )
    return Linter(config=config)


def test_primary_key_valid(pk_linter):
    """Test that a valid primary key constraint name passes when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        CONSTRAINT pk_person PRIMARY KEY (person_id)
    );
    """
    result = pk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV13"]
    assert len(violations) == 0


def test_primary_key_invalid(pk_linter):
    """Test that an invalid primary key constraint name passes when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        CONSTRAINT person_pk PRIMARY KEY (person_id)
    );
    """
    result = pk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV13"]
    assert len(violations) == 1
    assert "should start with 'pk_'" in violations[0].description.lower()


def test_add_primary_key_valid(pk_linter):
    """Test that a valid primary key constraint name passes when altering a table."""
    sql = """
    ALTER TABLE public.person
    ADD CONSTRAINT pk_person PRIMARY KEY (person_id);
    """
    result = pk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV13"]
    assert len(violations) == 0


def test_add_primary_key_invalid(pk_linter):
    """Test that an invalid primary key constraint name passes when altering a table."""
    sql = """
    ALTER TABLE public.person
    ADD CONSTRAINT person_pk PRIMARY KEY (person_id);
    """
    result = pk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV13"]
    assert len(violations) == 1
    assert "should start with 'pk_'" in violations[0].description.lower()
