"""Tests for the CV16 rule (UNIQUE constraint naming)."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig


@pytest.fixture
def uc_linter():
    """Create a linter with the UNIQUE constraint rule enabled."""
    config = FluffConfig(
        configs={
            "core": {"dialect": "postgres"},
            "rules": {"CV16": {"enabled": True}},
            "include_rules": ["CV16"],
            "exclude_rules": ["all"],
        }
    )
    return Linter(config=config)


def test_unique_constraint_valid(uc_linter):
    """Test that a valid unique constraint name passes when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        email VARCHAR(255),
        CONSTRAINT uc_person_email UNIQUE (email)
    );
    """
    result = uc_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV16"]
    assert len(violations) == 0


def test_unique_constraint_invalid(uc_linter):
    """Test that an invalid unique constraint name fails when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        email VARCHAR(255),
        CONSTRAINT unique_email UNIQUE (email)
    );
    """
    result = uc_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV16"]
    assert len(violations) == 1
    assert "should start with 'uc_'" in violations[0].description.lower()


def test_inline_unique_constraint(uc_linter):
    """Test inline unique constraint with valid name when creating a table."""
    sql = """
    CREATE TABLE public.person (
        person_id INT,
        email VARCHAR(255) CONSTRAINT uc_person_email UNIQUE
    );
    """
    result = uc_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV16"]
    assert len(violations) == 0


def test_add_unique_valid(uc_linter):
    """Test that a valid unique constraint name passes when altering a table."""
    sql = """
    ALTER TABLE public.person
    ADD CONSTRAINT uc_person_email UNIQUE (email);
    """
    result = uc_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV16"]
    assert len(violations) == 0


def test_add_unique_invalid(uc_linter):
    """Test that an invalid unique constraint name fails when altering a table."""
    sql = """
    ALTER TABLE public.person
    ADD CONSTRAINT unique_email UNIQUE (email);
    """
    result = uc_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV16"]
    assert len(violations) == 1
    assert "should start with 'uc_'" in violations[0].description.lower()
