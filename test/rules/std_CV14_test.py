"""Tests for the CV14 rule (FOREIGN KEY constraint naming)."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.config import FluffConfig


@pytest.fixture(scope="module")
def fk_linter():
    """Create a linter with the FOREIGN KEY constraint rule enabled."""
    config = FluffConfig(
        configs={
            "core": {"dialect": "postgres"},
            "rules": {"CV14": {"enabled": True}},
            "include_rules": ["CV14"],
            "exclude_rules": ["all"],
        }
    )
    return Linter(config=config)


def test_foreign_key_valid(fk_linter):
    """Test that a valid foreign key constraint name passes when creating a table."""
    sql = """
    CREATE TABLE public.orders (
        order_id INT,
        person_id INT,
        CONSTRAINT fk_orders_person FOREIGN KEY (person_id)
            REFERENCES public.person(person_id)
    );
    """
    result = fk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV14"]
    assert len(violations) == 0


def test_foreign_key_invalid(fk_linter):
    """Test that an invalid foreign key constraint name fails when creating a table."""
    sql = """
    CREATE TABLE public.orders (
        order_id INT,
        person_id INT,
        CONSTRAINT orders_person_fk FOREIGN KEY (person_id)
            REFERENCES public.person(person_id)
    );
    """
    result = fk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV14"]
    assert len(violations) == 1
    assert "should start with 'fk_'" in violations[0].description.lower()


def test_add_foreign_key_valid(fk_linter):
    """Test that a valid foreign key constraint name passes when altering a table."""
    sql = """
    ALTER TABLE public.orders
    ADD CONSTRAINT fk_orders_person FOREIGN KEY (person_id)
        REFERENCES public.person(person_id);
    """
    result = fk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV14"]
    assert len(violations) == 0


def test_add_foreign_key_invalid(fk_linter):
    """Test that an invalid foreign key constraint name fails when altering a table."""
    sql = """
    ALTER TABLE public.orders
    ADD CONSTRAINT orders_person_fk FOREIGN KEY (person_id)
        REFERENCES public.person(person_id);
    """
    result = fk_linter.lint_string(sql)
    violations = [v for v in result.violations if v.rule_code() == "CV14"]
    assert len(violations) == 1
    assert "should start with 'fk_'" in violations[0].description.lower()
