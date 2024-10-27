"""Tests for AlterColumnTypeCheck."""

import pytest

from ddlcheck.checks.alter_column_type import AlterColumnTypeCheck
from ddlcheck.models import SeverityLevel

from .test_check_helpers import check_detects_issue, check_no_issue


def test_alter_column_type():
    """Test that AlterColumnTypeCheck detects ALTER COLUMN TYPE."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        AlterColumnTypeCheck,
        "ALTER TABLE orders ALTER COLUMN status TYPE VARCHAR(100);",
        SeverityLevel.HIGH
    )


def test_alter_column_type_with_using():
    """Test that AlterColumnTypeCheck detects ALTER COLUMN TYPE with USING."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        AlterColumnTypeCheck,
        "ALTER TABLE orders ALTER COLUMN amount TYPE NUMERIC(10,2) USING amount::NUMERIC(10,2);",
        SeverityLevel.HIGH
    )


def test_alter_column_type_multiple_columns():
    """Test that AlterColumnTypeCheck detects multiple column type changes."""
    # Arrange & Act & Assert
    assert check_detects_issue(
        AlterColumnTypeCheck,
        """
        ALTER TABLE orders 
        ALTER COLUMN status TYPE VARCHAR(100),
        ALTER COLUMN reference TYPE VARCHAR(50);
        """,
        SeverityLevel.HIGH
    )


def test_alter_column_without_type_change():
    """Test that AlterColumnTypeCheck ignores ALTER COLUMN without type change."""
    # Arrange & Act & Assert
    assert check_no_issue(
        AlterColumnTypeCheck,
        "ALTER TABLE orders ALTER COLUMN status SET NOT NULL;"
    )


def test_add_column():
    """Test that AlterColumnTypeCheck ignores ADD COLUMN."""
    # Arrange & Act & Assert
    assert check_no_issue(
        AlterColumnTypeCheck,
        "ALTER TABLE orders ADD COLUMN reference VARCHAR(50);"
    )


def test_non_alter_statement():
    """Test that AlterColumnTypeCheck ignores non-ALTER statements."""
    # Arrange & Act & Assert
    assert check_no_issue(
        AlterColumnTypeCheck,
        "SELECT * FROM orders;"
    ) 