"""Implementation of Rule CV13."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV13(BaseRule):
    """PRIMARY KEY constraint names should use expected prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE TABLE public.person (
            person_id INT,
            CONSTRAINT person_pk PRIMARY KEY (person_id)
        );

    **Best practice**

    .. code-block:: sql

        CREATE TABLE public.person (
            person_id INT,
            CONSTRAINT pk_person PRIMARY KEY (person_id)
        );
    """

    name = "convention.constraint_name.primary_key"
    code = "CV13"
    description = "Enforces PRIMARY KEY constraints to start with expected prefix."
    groups = ("all", "convention")
    config_keywords = []
    crawl_behaviour = SegmentSeekerCrawler({"table_constraint"})

    # The expected prefix for PRIMARY KEY constraint
    _DEFAULT_EXPECTED_PREFIX = "pk_"

    def __init__(self, code="CV13", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get(
            "expected_prefix", self._DEFAULT_EXPECTED_PREFIX
        )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate PRIMARY KEY constraint name prefixes."""
        try:
            segment = context.segment
            obj_ref = segment.get_child("object_reference")
            if not obj_ref:
                return None

            constraint_name = obj_ref.raw
            keywords = [
                keyword.raw.upper() for keyword in segment.get_children("keyword")
            ]

            # Check if this is a PRIMARY KEY constraint
            is_primary_key = {"PRIMARY", "KEY"}.issubset(keywords)

            if is_primary_key and not constraint_name.lower().startswith(
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
            f"PRIMARY KEY constraint '{constraint_name}' violates convention"
        )
        return LintResult(
            anchor=segment,
            description=(
                f"PRIMARY KEY constraint name '{constraint_name}' should start with "
                f"'{expected_prefix}'."
            ),
        )
