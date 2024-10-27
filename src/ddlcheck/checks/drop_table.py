"""Check for DROP TABLE operations."""

from typing import Any, Dict, List

from pglast.enums import ObjectType

from ddlcheck.core import Check, is_drop_stmt
from ddlcheck.models import Issue, SeverityLevel


class DropTableCheck(Check):
    """Check for DROP TABLE operations."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "drop_table"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects DROP TABLE operations that could result in data loss"

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

        if not is_drop_stmt(stmt):
            return issues

        drop_stmt = stmt["DropStmt"]

        # Only check for table drops
        if not hasattr(drop_stmt, "removeType") or drop_stmt.removeType != ObjectType.OBJECT_TABLE:
            return issues

        # Get table names
        table_names = []
        if hasattr(drop_stmt, "objects") and drop_stmt.objects:
            for obj in drop_stmt.objects:
                if isinstance(obj, (list, tuple)):
                    # Each element in the list is a string part (e.g., schema, table)
                    parts = []
                    for part in obj:
                        if hasattr(part, "val") and hasattr(part.val, "sval"):
                            parts.append(part.val.sval)
                    if parts:
                        table_names.append(".".join(parts))

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
                message=f"DROP TABLE operation on {table_str}",
                line=line,
                suggestion=(
                    "Dropping tables is a destructive operation that cannot be easily recovered from.\n"
                    "Consider renaming the table instead (e.g., with a '_bak' suffix) and dropping\n"
                    "it later after confirming that it's no longer needed."
                ),
                context={"tables": table_names},
            )
        )

        return issues
