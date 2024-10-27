"""Check for DROP COLUMN operations."""

from typing import Any, Dict, List

from pglast.enums import AlterTableType

from ddlcheck.core import (
    Check,
    get_alter_command_type,
    get_alter_table_commands,
    is_alter_table_stmt,
)
from ddlcheck.models import Issue, SeverityLevel


class DropColumnCheck(Check):
    """Check for DROP COLUMN operations."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "drop_column"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects DROP COLUMN operations that require table rewrites"

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

            # Check if this is a DROP COLUMN command
            if cmd_type == AlterTableType.AT_DropColumn:
                alter_cmd = cmd["AlterTableCmd"]
                col_name = getattr(alter_cmd, "name", "unknown")
                table_name = stmt["AlterTableStmt"].relation.relname

                issues.append(
                    Issue(
                        check_id=self.id,
                        message=f"DROP COLUMN '{col_name}' from table '{table_name}'",
                        line=line,
                        severity=self.severity,
                        suggestion=(
                            "Dropping columns requires a table rewrite in PostgreSQL.\n"
                            "For large tables, consider these options:\n"
                            "1. Use a database with pg_repack for online column drops\n"
                            "2. Mark the column as unused instead (ALTER TABLE ... ALTER COLUMN ... SET UNUSED)\n"
                            "3. Perform the drop during maintenance windows"
                        ),
                        context=f"ALTER TABLE {table_name} DROP COLUMN {col_name}",
                    )
                )

        return issues
