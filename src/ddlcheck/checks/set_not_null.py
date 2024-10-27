"""Check for SET NOT NULL operations."""

from typing import Any, Dict, List

from pglast.enums import AlterTableType

from ddlcheck.core import (
    Check,
    get_alter_command_type,
    get_alter_table_commands,
    is_alter_table_stmt,
)
from ddlcheck.models import Issue, SeverityLevel


class SetNotNullCheck(Check):
    """Check for SET NOT NULL operations."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "set_not_null"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects SET NOT NULL operations that require full table scans"

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

        if not is_alter_table_stmt(stmt):
            return issues

        # Check each command in the ALTER TABLE statement
        for cmd in get_alter_table_commands(stmt):
            cmd_type = get_alter_command_type(cmd)

            # Check if this is a SET NOT NULL command
            if cmd_type == AlterTableType.AT_SetNotNull:
                alter_cmd = cmd["AlterTableCmd"]
                col_name = getattr(alter_cmd, "name", "unknown")
                table_name = stmt["AlterTableStmt"].relation.relname

                issues.append(
                    Issue(
                        check_id=self.id,
                        message=f"SET NOT NULL constraint on column '{col_name}' in table '{table_name}'",
                        line=line,
                        severity=self.severity,
                        suggestion=(
                            "Adding a NOT NULL constraint requires a full table scan to verify the constraint.\n"
                            "For large tables, this can cause significant downtime.\n"
                            "Consider these alternatives:\n"
                            "1. First ensure all values are non-null with UPDATE statements\n"
                            "2. Add a CHECK constraint with a WHERE clause instead\n"
                            "3. Apply the constraint during low-traffic periods"
                        ),
                        context=f"ALTER TABLE {table_name} ALTER COLUMN {col_name} SET NOT NULL",
                    )
                )

        return issues
