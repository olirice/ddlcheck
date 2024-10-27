"""Tests for TruncateCheck."""

import pytest

from ddlcheck.checks.truncate import TruncateCheck
from ddlcheck.models import SeverityLevel

from .test_check_helpers import check_detects_issue, check_no_issue


def test_truncate_single_table():
    """Test that TruncateCheck detects TRUNCATE on a single table."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        TruncateCheck,
        "TRUNCATE TABLE audit_logs;",
        SeverityLevel.HIGH
    )


def test_truncate_multiple_tables():
    """Test that TruncateCheck detects TRUNCATE on multiple tables."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        TruncateCheck,
        "TRUNCATE TABLE audit_logs, temp_records;",
        SeverityLevel.HIGH
    )


def test_truncate_without_table_keyword():
    """Test that TruncateCheck detects TRUNCATE without TABLE keyword."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        TruncateCheck,
        "TRUNCATE audit_logs;",
        SeverityLevel.HIGH
    )


def test_truncate_with_cascade():
    """Test that TruncateCheck detects TRUNCATE with CASCADE option."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        TruncateCheck,
        "TRUNCATE TABLE audit_logs CASCADE;",
        SeverityLevel.HIGH
    )


def test_truncate_with_restart_identity():
    """Test that TruncateCheck detects TRUNCATE with RESTART IDENTITY option."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        TruncateCheck,
        "TRUNCATE TABLE audit_logs RESTART IDENTITY;",
        SeverityLevel.HIGH
    )


def test_non_truncate_statement():
    """Test that TruncateCheck ignores non-TRUNCATE statements."""
    # Arrange & Act & Assert
    assert check_no_issue(
        TruncateCheck,
        "DELETE FROM audit_logs WHERE created_at < '2023-01-01';"
    ) 