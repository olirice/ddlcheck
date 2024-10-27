"""Tests for AddColumnCheck."""

import pytest

from ddlcheck.checks.add_column import AddColumnCheck
from ddlcheck.models import SeverityLevel

from .test_check_helpers import check_detects_issue, check_no_issue


def test_add_column_with_not_null_and_default():
    """Test that AddColumnCheck detects columns added with NOT NULL and DEFAULT."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        AddColumnCheck,
        "ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;",
        SeverityLevel.HIGH
    )


def test_add_column_with_just_not_null():
    """Test that AddColumnCheck allows columns added with NOT NULL and no DEFAULT."""
    # Arrange & Act & Assert
    assert check_no_issue(
        AddColumnCheck,
        "ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL;"
    )


def test_add_column_with_just_default():
    """Test that AddColumnCheck allows columns added with DEFAULT and no NOT NULL."""
    # Arrange & Act & Assert
    assert check_no_issue(
        AddColumnCheck,
        "ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;"
    )


def test_add_column_without_constraints():
    """Test that AddColumnCheck allows columns added without constraints."""
    # Arrange & Act & Assert
    assert check_no_issue(
        AddColumnCheck,
        "ALTER TABLE users ADD COLUMN email_verified BOOLEAN;"
    )


def test_add_multiple_columns():
    """Test that AddColumnCheck detects issues in multi-column statements."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        AddColumnCheck,
        """
        ALTER TABLE users 
        ADD COLUMN email_verified BOOLEAN DEFAULT FALSE,
        ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'active';
        """,
        SeverityLevel.HIGH
    )


def test_non_alter_statement():
    """Test that AddColumnCheck ignores non-ALTER statements."""
    # Arrange & Act & Assert
    assert check_no_issue(
        AddColumnCheck,
        "SELECT * FROM users;"
    ) 