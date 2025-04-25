"""Helper functions for testing checks."""

from typing import List, Type

from pglast import parse_sql

from ddlcheck.core import Check
from ddlcheck.models import Issue, SeverityLevel


def run_check_on_sql(check_class: Type[Check], sql: str) -> List[Issue]:
    """Run a check on a SQL statement.

    Args:
        check_class: The check class to run
        sql: The SQL to check

    Returns:
        List of issues found by the check
    """
    # Create an instance of the check
    check = check_class()

    # Parse the SQL
    parsed = parse_sql(sql)

    # The first element is a RawStmt
    raw_stmt = parsed[0]

    # Extract the statement
    stmt_obj = raw_stmt.stmt

    # Get the statement type
    stmt_type = stmt_obj.__class__.__name__

    # Create a dict with the statement type as key
    stmt = {stmt_type: stmt_obj}

    # Run the check
    return check.check_statement(stmt, 1)


def check_detects_issue(check_class: Type[Check], sql: str, severity: SeverityLevel = None) -> bool:
    """Check if a SQL statement is detected as having an issue.

    Args:
        check_class: The check class to run
        sql: The SQL to check
        severity: Optional severity level to match

    Returns:
        True if an issue was found, False otherwise
    """
    issues = run_check_on_sql(check_class, sql)

    if not issues:
        return False

    if severity is not None:
        return any(issue.severity == severity for issue in issues)

    return True


def check_no_issue(check_class: Type[Check], sql: str) -> bool:
    """Check if a SQL statement has no issues.

    Args:
        check_class: The check class to run
        sql: The SQL to check

    Returns:
        True if no issues were found, False otherwise
    """
    issues = run_check_on_sql(check_class, sql)
    return len(issues) == 0
