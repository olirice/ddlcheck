"""Check for TRUNCATE operations."""

from typing import Any, Dict, List

from ddlcheck.core import Check, is_truncate_stmt
from ddlcheck.models import Issue, SeverityLevel


class TruncateCheck(Check):
    """Check for TRUNCATE operations."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "truncate"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects TRUNCATE operations which can cause data loss and locks"

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

        if not is_truncate_stmt(stmt):
            return issues

        truncate_stmt = stmt["TruncateStmt"]

        # Get table names
        table_names = []
        if hasattr(truncate_stmt, "relations") and truncate_stmt.relations:
            for relation in truncate_stmt.relations:
                if hasattr(relation, "relname"):
                    table_names.append(relation.relname)

        # If we couldn't get table names, use a generic message
        if not table_names:
            table_str = "tables"
        elif len(table_names) == 1:
            table_str = f"table '{table_names[0]}'"
        else:
            quoted_names = [f"'{name}'" for name in table_names]
            table_str = f"tables {', '.join(quoted_names)}"

        issues.append(
            self.create_issue(
                message=f"TRUNCATE operation on {table_str}",
                line=line,
                suggestion=(
                    "TRUNCATE is a destructive operation that cannot be easily rolled back.\n"
                    "It also acquires an ACCESS EXCLUSIVE lock on the table.\n"
                    "Consider using DELETE with a WHERE clause if you need to remove specific data,\n"
                    "or ensure that this operation is only run during maintenance windows."
                ),
                context={"tables": table_names},
            )
        )

        return issues
