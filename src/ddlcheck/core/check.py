"""Base class for all DDLCheck checks."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from pglast import parse_sql, prettify
from pglast.parser import ParseError

from ddlcheck.models import CheckResult, Config, Issue, SeverityLevel

# Set up logging
logger = logging.getLogger(__name__)


class Check(ABC):
    """Base class for all checks."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize a Check.

        Args:
            config: Configuration for the check
        """
        self.config = config or Config()

    @property
    @abstractmethod
    def id(self) -> str:
        """Return the unique identifier for this check."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what this check looks for."""
        pass

    @property
    @abstractmethod
    def severity(self) -> SeverityLevel:
        """Return the default severity level for issues found by this check."""
        pass

    @property
    def effective_severity(self) -> SeverityLevel:
        """Return the effective severity level, considering any config overrides.

        Returns:
            Severity level to use for this check
        """
        override = self.config.get_severity_override(self.id)
        return override if override is not None else self.severity

    @property
    def enabled(self) -> bool:
        """Check if this check is enabled.

        Returns:
            True if enabled, False otherwise
        """
        return self.config.is_check_enabled(self.id)

    def get_config_option(self, option: str, default: Any = None) -> Any:
        """Get a configuration option for this check.

        Args:
            option: Name of the configuration option
            default: Default value if option is not set

        Returns:
            Value of the option
        """
        check_config = self.config.get_check_config(self.id)
        return check_config.get(option, default)

    @abstractmethod
    def check_statement(self, stmt: Dict[str, Any], line: int) -> List[Issue]:
        """Check a single SQL statement for issues.

        Args:
            stmt: The parsed SQL statement
            line: The line number where the statement begins

        Returns:
            List of issues found in the statement
        """
        pass

    def create_issue(
        self,
        message: str,
        line: int,
        suggestion: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Issue:
        """Create an issue with this check's ID and severity.

        Args:
            message: The issue message
            line: The line number
            suggestion: Optional suggestion to fix the issue
            context: Optional context information

        Returns:
            A new Issue object
        """
        return Issue(
            check_id=self.id,
            message=message,
            line=line,
            severity=self.effective_severity,
            suggestion=suggestion,
            context=context,
        )

    def check_file(self, file_path: Path) -> CheckResult:
        """Check a SQL file for issues.

        Args:
            file_path: Path to the SQL file to check

        Returns:
            Result of the check
        """
        result = CheckResult(file_path)

        if not self.enabled:
            return result

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                sql = f.read()

            # Skip empty files
            if not sql.strip():
                logger.debug(f"Skipping empty file: {file_path}")
                return result

            # Parse the SQL into an AST
            try:
                # Parse the SQL string
                parsed = parse_sql(sql)

                # Check each statement
                for stmt_idx, raw_stmt in enumerate(parsed):
                    # Skip empty statements (can happen with bare semicolons)
                    if not raw_stmt or not hasattr(raw_stmt, "stmt"):
                        logger.debug(f"Skipping empty statement at index {stmt_idx}")
                        continue

                    # Extract the actual statement from the RawStmt object
                    # In pglast, RawStmt objects have a 'stmt' attribute
                    stmt_obj = raw_stmt.stmt

                    # Skip null statements
                    if stmt_obj is None:
                        logger.debug(f"Skipping null statement at index {stmt_idx}")
                        continue

                    # For our check functions, we need to convert the stmt object to a dict
                    # We'll do this by getting the node type and creating a dict with that type as key
                    stmt_type = stmt_obj.__class__.__name__
                    stmt = {stmt_type: stmt_obj}

                    # Get line number by prettifying the SQL up to this statement
                    # This is a bit of a hack but works for finding approximate line numbers
                    try:
                        if stmt_idx > 0:
                            # Convert the statements to SQL for line counting - one statement at a time
                            parts = []
                            for i in range(stmt_idx):
                                try:
                                    stmt_sql = prettify(parsed[i])
                                    parts.append(stmt_sql)
                                except Exception as e:
                                    # Skip errors in prettifying
                                    logger.debug(f"Error prettifying statement {i}: {e}")
                                    pass
                            prefix_sql = "\n".join(parts)
                        else:
                            prefix_sql = ""

                        line = prefix_sql.count("\n") + 1
                    except Exception as e:
                        # If we can't determine the line number, use a default
                        logger.debug(f"Error determining line number: {e}")
                        line = 1

                    # Check the statement
                    try:
                        issues = self.check_statement(stmt, line)
                        for issue in issues:
                            result.add_issue(issue)
                    except Exception as e:
                        # If a check fails, log it and continue with other checks
                        logger.warning(f"Error checking statement at line {line}: {e}")
                        result.add_issue(
                            self.create_issue(
                                message=f"Error checking statement: {str(e)}", line=line
                            )
                        )

            except ParseError as e:
                # If we can't parse the SQL, add an issue
                result.add_issue(
                    self.create_issue(
                        message=f"Failed to parse SQL: {str(e)}",
                        line=e.location.lineno if hasattr(e, "location") else 1,
                    )
                )

        except Exception as e:
            # If we can't open the file or something else goes wrong, add an issue
            result.add_issue(self.create_issue(message=f"Failed to check file: {str(e)}", line=1))

        return result
