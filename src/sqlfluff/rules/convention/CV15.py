"""Implementation of Rule CV15."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV15(BaseRule):
    """CHECK constraint names should use expected prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE TABLE public.employee (
            employee_id INT,
            salary DECIMAL(10,2),
            CONSTRAINT salary_positive CHECK (salary > 0)
        );

    **Best practice**

    .. code-block:: sql

        CREATE TABLE public.employee (
            employee_id INT,
            salary DECIMAL(10,2),
            CONSTRAINT chk_salary_positive CHECK (salary > 0)
        );
    """

    name = "convention.constraint_name.check"
    code = "CV15"
    description = "Enforces CHECK constraints to start with expected prefix."
    groups = ("all", "convention")
    config_keywords = []  # Intentionally empty to bypass validation
    crawl_behaviour = SegmentSeekerCrawler({"table_constraint"})

    # The expected prefix for CHECK constraint
    _DEFAULT_EXPECTED_PREFIX = "chk_"

    def __init__(self, code="CV15", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get(
            "expected_prefix", self._DEFAULT_EXPECTED_PREFIX
        )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate CHECK constraint name prefixes."""
        try:
            segment = context.segment
            obj_ref = segment.get_child("object_reference")
            if not obj_ref:
                return None

            constraint_name = obj_ref.raw
            keywords = [
                keyword.raw.upper() for keyword in segment.get_children("keyword")
            ]

            # Check if this is a CHECK constraint
            is_check = "CHECK" in keywords

            if is_check and not constraint_name.lower().startswith(
                self.expected_prefix
            ):
                return self._create_lint_result(
                    segment, constraint_name, self.expected_prefix
                )
            return None
        except Exception as e:
            self.logger.error(f"Exception in constraint naming rule: {str(e)}")
            return None

    def _create_lint_result(
        self, segment, constraint_name: str, expected_prefix: str
    ) -> LintResult:
        """Create a lint result for a constraint naming violation.

        Args:
            segment: The segment to anchor the lint result to
            constraint_name: The name of the constraint
            expected_prefix: The expected prefix for the constraint

        Returns:
            LintResult: The lint result object
        """
        self.logger.debug(
            f"CHECK constraint '{constraint_name}' violates naming convention"
        )
        return LintResult(
            anchor=segment,
            description=(
                f"CHECK constraint name '{constraint_name}' should start with "
                f"'{expected_prefix}'."
            ),
        )
