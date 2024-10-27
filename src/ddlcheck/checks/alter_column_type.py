"""Check for ALTER COLUMN TYPE operations."""

from typing import Any, Dict, List

from pglast.enums import AlterTableType

from ddlcheck.core import (
    Check,
    get_alter_command_type,
    get_alter_table_commands,
    is_alter_table_stmt,
)
from ddlcheck.models import Issue, SeverityLevel


class AlterColumnTypeCheck(Check):
    """Check for ALTER COLUMN TYPE operations."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "alter_column_type"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects ALTER COLUMN TYPE operations that require table rewrites"

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

        if not is_alter_table_stmt(stmt):
            return issues

        # Check each command in the ALTER TABLE statement
        for cmd in get_alter_table_commands(stmt):
            cmd_type = get_alter_command_type(cmd)

            # Check if this is an ALTER COLUMN TYPE command
            if cmd_type == AlterTableType.AT_AlterColumnType:
                alter_cmd = cmd["AlterTableCmd"]
                col_name = getattr(alter_cmd, "name", "unknown")
                table_name = stmt["AlterTableStmt"].relation.relname

                # Get target type if available
                target_type = ""
                if hasattr(alter_cmd, "def_") and hasattr(alter_cmd.def_, "typeName"):
                    type_name = alter_cmd.def_.typeName
                    if hasattr(type_name, "names") and type_name.names:
                        # Get the names list
                        type_parts = []
                        for name_part in type_name.names:
                            if hasattr(name_part, "val") and hasattr(name_part.val, "sval"):
                                type_parts.append(name_part.val.sval)
                        if type_parts:
                            target_type = ".".join(type_parts)

                issues.append(
                    Issue(
                        check_id=self.id,
                        message=(
                            f"Column type change for '{col_name}' in table '{table_name}'"
                            + (f" to '{target_type}'" if target_type else "")
                        ),
                        line=line,
                        severity=self.severity,
                        suggestion=(
                            "Altering column types requires a table rewrite and locks the table.\n"
                            "Consider using a multi-step approach:\n"
                            "1. Add a new column with the desired type\n"
                            "2. Copy/transform data from old column to new column\n"
                            "3. Drop the old column\n"
                            "4. Rename the new column to the original name"
                        ),
                        context=f"ALTER TABLE {table_name} ALTER COLUMN {col_name} TYPE ...",
                    )
                )

        return issues
