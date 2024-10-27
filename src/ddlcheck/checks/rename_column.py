"""Check for RENAME COLUMN operations."""

from typing import Any, Dict, List

from pglast.enums import ObjectType

from ddlcheck.core import Check, is_rename_stmt
from ddlcheck.models import Issue, SeverityLevel


class RenameColumnCheck(Check):
    """Check for RENAME COLUMN operations."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "rename_column"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects RENAME COLUMN operations that break dependent objects"

    @property
    def severity(self) -> SeverityLevel:
        """Return the default severity level for issues found by this check."""
        return SeverityLevel.MEDIUM

    def check_statement(self, stmt: Dict[str, Any], line: int) -> List[Issue]:
        """Check a single SQL statement for issues.

        Args:
            stmt: The parsed SQL statement
            line: The line number where the statement begins

        Returns:
            List of issues found in the statement
        """
        issues = []

        # Check if this is a RENAME statement for a column
        if is_rename_stmt(stmt):
            rename_stmt = stmt["RenameStmt"]

            # Check if this is a column rename
            if (
                hasattr(rename_stmt, "renameType")
                and rename_stmt.renameType == ObjectType.OBJECT_COLUMN
            ):

                # Get table name
                table_name = "unknown"
                if hasattr(rename_stmt, "relation") and hasattr(rename_stmt.relation, "relname"):
                    table_name = rename_stmt.relation.relname

                # Get old and new column names
                old_name = getattr(rename_stmt, "subname", "old_name")
                new_name = getattr(rename_stmt, "newname", "new_name")

                issues.append(
                    Issue(
                        check_id=self.id,
                        message=f"Rename column '{old_name}' to '{new_name}' in table '{table_name}'",
                        line=line,
                        severity=self.severity,
                        suggestion=(
                            "Renaming columns can break dependent objects like views, functions, and triggers.\n"
                            "Consider these safer approaches:\n"
                            "1. Add a new column with the desired name and keep both until all dependencies are updated\n"
                            "2. Verify all dependencies are identified and updated in the same migration\n"
                            "3. Use a view to maintain backward compatibility"
                        ),
                        context=f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}",
                    )
                )

        return issues
