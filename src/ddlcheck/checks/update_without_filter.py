"""Check for UPDATE statements without WHERE clauses."""

from typing import Any, Dict, List

from ddlcheck.core import Check, has_where_clause, is_update_stmt
from ddlcheck.models import Issue, SeverityLevel


class UpdateWithoutFilterCheck(Check):
    """Check for UPDATE statements without WHERE clauses."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "update_without_filter"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects UPDATE statements without WHERE clauses"

    @property
    def severity(self) -> SeverityLevel:
        """Return the default severity level for issues found by this check."""
        return SeverityLevel.HIGH

    def check_statement(self, stmt: Dict[str, Any], line: int) -> List[Issue]:
        """Check a single SQL statement for issues.

        Args:
            stmt: The parsed SQL statement
            line: The line number where the statement begins

        Returns:
            List of issues found in the statement
        """
        issues = []

        if not is_update_stmt(stmt):
            return issues

        # Check if the statement has a WHERE clause
        if not has_where_clause(stmt):
            update_stmt = stmt["UpdateStmt"]

            # Get table name
            table_name = "unknown"
            if hasattr(update_stmt, "relation") and hasattr(update_stmt.relation, "relname"):
                table_name = update_stmt.relation.relname

            issues.append(
                Issue(
                    check_id=self.id,
                    message=f"UPDATE statement on table '{table_name}' without WHERE clause",
                    line=line,
                    severity=self.severity,
                    suggestion=(
                        "Add a WHERE clause to limit the rows affected by the update.\n"
                        "Updating all rows in a table can cause excessive I/O and blocking."
                    ),
                    context=f"UPDATE {table_name} SET ... (without WHERE)",
                )
            )

        return issues
