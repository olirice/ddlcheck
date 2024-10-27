"""Check for potentially risky column additions."""

from typing import Any, Dict, List

from pglast.enums import AlterTableType, ConstrType

from ddlcheck.core import (
    Check,
    get_alter_command_type,
    get_alter_table_commands,
    is_alter_table_stmt,
)
from ddlcheck.models import Issue, SeverityLevel


class AddColumnCheck(Check):
    """Check for columns added with NOT NULL and DEFAULT."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "add_column"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects when columns are added with NOT NULL constraints and DEFAULT values"

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

            # Check if this is an ADD COLUMN command
            if cmd_type == AlterTableType.AT_AddColumn:
                alter_cmd = cmd["AlterTableCmd"]

                # Access the column definition
                def_elem = alter_cmd.def_
                if not def_elem or not hasattr(def_elem, "constraints"):
                    continue

                # Check if the column has a NOT NULL constraint and DEFAULT
                has_not_null = False
                has_default = False

                # Check constraints for NOT NULL
                if hasattr(def_elem, "constraints") and def_elem.constraints:
                    for constraint in def_elem.constraints:
                        if hasattr(constraint, "contype"):
                            if constraint.contype == ConstrType.CONSTR_NOTNULL:
                                has_not_null = True
                            elif constraint.contype == ConstrType.CONSTR_DEFAULT:
                                has_default = True

                # If both are present, we have an issue
                if has_not_null and has_default:
                    table_name = stmt["AlterTableStmt"].relation.relname
                    col_name = def_elem.colname if hasattr(def_elem, "colname") else "unknown"

                    issues.append(
                        Issue(
                            check_id=self.id,
                            message=f"Column '{col_name}' added to table '{table_name}' with NOT NULL and DEFAULT",
                            line=line,
                            severity=self.severity,
                            suggestion=(
                                "Consider using two separate migrations:\n"
                                "1. First add the column with a DEFAULT but as nullable\n"
                                "2. After data has been populated, add the NOT NULL constraint"
                            ),
                            context=f"ALTER TABLE {table_name} ADD COLUMN {col_name} ... NOT NULL DEFAULT ...",
                        )
                    )

        return issues
