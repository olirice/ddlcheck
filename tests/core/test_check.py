"""Tests for the Check class."""

from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, mock_open, patch

from pglast.parser import ParseError

from ddlcheck.core.check import Check
from ddlcheck.models import Config, Issue, SeverityLevel


class MockCheck(Check):
    """Test implementation of Check for testing."""

    @property
    def id(self) -> str:
        return "test_check"

    @property
    def description(self) -> str:
        return "Test check description"

    @property
    def severity(self) -> SeverityLevel:
        return SeverityLevel.MEDIUM

    def check_statement(self, stmt: Dict[str, Any], line: int) -> List[Issue]:
        """Implement check_statement for testing."""
        # Test implementation to match different test cases
        if "AlterTableStmt" in stmt:
            return [self.create_issue("Test issue", line)]
        elif "error" in str(stmt):
            raise ValueError("Test error in statement check")
        return []


def test_check_init():
    """Test Check initialization."""
    # Test with default config
    check = MockCheck()
    assert check.config is not None

    # Test with provided config
    config = Config(excluded_checks={"some_check"})
    check = MockCheck(config)
    assert check.config == config


def test_effective_severity():
    """Test effective_severity property."""
    # No override
    check = MockCheck()
    assert check.effective_severity == SeverityLevel.MEDIUM

    # With override
    config = Config()
    config.severity_overrides["test_check"] = SeverityLevel.HIGH
    check = MockCheck(config)
    assert check.effective_severity == SeverityLevel.HIGH


def test_enabled():
    """Test enabled property."""
    # Check is enabled by default
    check = MockCheck()
    assert check.enabled is True

    # Check is disabled via config
    config = Config(excluded_checks={"test_check"})
    check = MockCheck(config)
    assert check.enabled is False


def test_get_config_option():
    """Test get_config_option method."""
    # Config option not set
    check = MockCheck()
    assert check.get_config_option("test_option") is None
    assert check.get_config_option("test_option", "default") == "default"

    # Config option set
    config = Config()
    config.check_config["test_check"] = {"test_option": "test_value"}
    check = MockCheck(config)
    assert check.get_config_option("test_option") == "test_value"


def test_create_issue():
    """Test create_issue method."""
    check = MockCheck()

    # Basic issue
    issue = check.create_issue("Test message", 10)
    assert issue.check_id == "test_check"
    assert issue.message == "Test message"
    assert issue.line == 10
    assert issue.severity == SeverityLevel.MEDIUM
    assert issue.suggestion is None
    assert issue.context is None

    # Issue with all options
    issue = check.create_issue(
        "Test message", 10, suggestion="Test suggestion", context={"test": "value"}
    )
    assert issue.suggestion == "Test suggestion"
    assert issue.context == {"test": "value"}


def test_check_file_parse_error():
    """Test check_file method with parse error."""
    check = MockCheck()

    # Mock ParseError
    parse_error = ParseError("syntax error", None)
    parse_error.location = MagicMock()
    parse_error.location.lineno = 5

    with patch("builtins.open", mock_open(read_data="SELECT * FROM;")):
        with patch("ddlcheck.core.check.parse_sql", side_effect=parse_error):
            result = check.check_file(Path("test.sql"))

    assert len(result.issues) == 1
    assert "Failed to parse SQL" in result.issues[0].message
    assert result.issues[0].line == 5


def test_check_file_statement_error():
    """Test check_file method with statement check error."""
    check = MockCheck()

    # Create a mock parsed result with a statement that will trigger an error
    mock_stmt = MagicMock()
    mock_stmt.stmt.__class__.__name__ = "error"
    mock_parsed = [mock_stmt]

    with patch("builtins.open", mock_open(read_data="SELECT * FROM error;")):
        with patch("ddlcheck.core.check.parse_sql", return_value=mock_parsed):
            result = check.check_file(Path("test.sql"))

    assert len(result.issues) == 1
    assert "Error checking statement" in result.issues[0].message


def test_check_file_line_number_error():
    """Test check_file method with line number determination error."""
    check = MockCheck()

    # Create a mock that causes an error when trying to determine line number
    mock_stmt = MagicMock()
    mock_stmt.stmt.__class__.__name__ = "TestStmt"
    mock_parsed = [mock_stmt]

    with patch("builtins.open", mock_open(read_data="SELECT 1;")):
        with patch("ddlcheck.core.check.parse_sql", return_value=mock_parsed):
            with patch("ddlcheck.core.check.prettify", side_effect=Exception("Test error")):
                result = check.check_file(Path("test.sql"))

    # Should still work even if line number determination fails
    assert len(result.issues) == 0


def test_check_file_empty():
    """Test check_file method with empty file."""
    check = MockCheck()

    with patch("builtins.open", mock_open(read_data="")):
        result = check.check_file(Path("test.sql"))

    assert len(result.issues) == 0


def test_check_file_disabled():
    """Test check_file method when check is disabled."""
    config = Config(excluded_checks={"test_check"})
    check = MockCheck(config)

    # Check should be skipped entirely
    result = check.check_file(Path("test.sql"))
    assert len(result.issues) == 0


def test_check_file_file_error():
    """Test check_file method with file open error."""
    check = MockCheck()

    with patch("builtins.open", side_effect=FileNotFoundError("Test error")):
        result = check.check_file(Path("nonexistent.sql"))

    assert len(result.issues) == 1
    assert "Failed to check file" in result.issues[0].message
