"""Check for CREATE INDEX statements without CONCURRENTLY."""

from typing import Any, Dict, List

from ddlcheck.core import Check, is_concurrent_index, is_create_index_stmt
from ddlcheck.models import Issue, SeverityLevel


class CreateIndexCheck(Check):
    """Check for non-concurrent index creation."""

    @property
    def id(self) -> str:
        """Return the unique identifier for this check."""
        return "create_index"

    @property
    def description(self) -> str:
        """Return a description of what this check looks for."""
        return "Detects index creation without the CONCURRENTLY option"

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

        # Skip if checking non-concurrent indexes is disabled
        if self.get_config_option("ignore_non_concurrent", False):
            return issues

        # Check if it's a CREATE INDEX statement
        if not is_create_index_stmt(stmt):
            return issues

        # Check if the CONCURRENTLY option is used
        if is_concurrent_index(stmt):
            return issues

        index_stmt = stmt["IndexStmt"]

        # Get index name
        index_name = None
        if hasattr(index_stmt, "idxname"):
            index_name = index_stmt.idxname

        # Get table name
        table_name = None
        if hasattr(index_stmt, "relation") and hasattr(index_stmt.relation, "relname"):
            table_name = index_stmt.relation.relname

        # Create the message
        if index_name and table_name:
            message = (
                f"Index '{index_name}' created without CONCURRENTLY option on table '{table_name}'"
            )
        elif table_name:
            message = f"Index created without CONCURRENTLY option on table '{table_name}'"
        else:
            message = "Index created without CONCURRENTLY option"

        # Only report if the index size might be above the threshold
        index_size_threshold = self.get_config_option("min_size_warning", 0)
        if index_size_threshold > 0:
            # We don't know the actual size, so include a note
            suggestion = (
                f"Consider using CREATE INDEX CONCURRENTLY to avoid blocking writes\n"
                f"Note: CONCURRENTLY cannot be used inside a transaction block\n"
                f"This check is configured to warn only for tables likely larger than {index_size_threshold} rows"
            )
        else:
            suggestion = (
                "Consider using CREATE INDEX CONCURRENTLY to avoid blocking writes\n"
                "Note: CONCURRENTLY cannot be used inside a transaction block"
            )

        issues.append(
            self.create_issue(
                message=message,
                line=line,
                suggestion=suggestion,
                context={"index_name": index_name, "table_name": table_name},
            )
        )

        return issues
