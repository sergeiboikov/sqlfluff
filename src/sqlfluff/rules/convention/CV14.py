"""Implementation of Rule CV14."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV14(BaseRule):
    """FOREIGN KEY constraint names should use expected prefix.

    **Anti-pattern**

    .. code-block:: sql

        CREATE TABLE public.orders (
            order_id INT,
            customer_id INT,
            CONSTRAINT customer_order_fkey FOREIGN KEY (customer_id)
                REFERENCES public.customers(id)
        );

    **Best practice**

    .. code-block:: sql

        CREATE TABLE public.orders (
            order_id INT,
            customer_id INT,
            CONSTRAINT fk_customer_order FOREIGN KEY (customer_id)
                REFERENCES public.customers(id)
        );
    """

    name = "convention.constraint_name.foreign_key"
    code = "CV14"
    description = "Enforces FOREIGN KEY constraints to start with expected prefix."
    groups = ("all", "convention")
    config_keywords = []
    crawl_behaviour = SegmentSeekerCrawler({"table_constraint"})

    # The expected prefix for FOREIGN KEY constraint
    _DEFAULT_EXPECTED_PREFIX = "fk_"

    def __init__(self, code="CV14", description="", **kwargs):
        """Initialize the rule with configuration."""
        super().__init__(code=code, description=description, **kwargs)
        # Set default expected_prefix if not provided
        self.expected_prefix = kwargs.get(
            "expected_prefix", self._DEFAULT_EXPECTED_PREFIX
        )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Validate FOREIGN KEY constraint name prefixes."""
        try:
            segment = context.segment
            obj_ref = segment.get_child("object_reference")
            if not obj_ref:
                return None

            constraint_name = obj_ref.raw
            keywords = [
                keyword.raw.upper() for keyword in segment.get_children("keyword")
            ]

            # Check if this is a FOREIGN KEY constraint
            is_foreign_key = {"FOREIGN", "KEY"}.issubset(keywords)

            if is_foreign_key and not constraint_name.lower().startswith(
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
            f"FOREIGN KEY constraint '{constraint_name}' violates convention"
        )
        return LintResult(
            anchor=segment,
            description=(
                f"FOREIGN KEY constraint name '{constraint_name}' should start with "
                f"'{expected_prefix}'."
            ),
        )
