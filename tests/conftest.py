"""Pytest configuration for DDLCheck."""

import os
from pathlib import Path

import pytest

from ddlcheck.models import Config


@pytest.fixture
def test_sql_dir() -> Path:
    """Path to the test SQL files directory."""
    return Path(__file__).parent / "test_sql"


@pytest.fixture
def risky_sql_file(test_sql_dir: Path) -> Path:
    """Path to a SQL file with risky operations."""
    return test_sql_dir / "risky_operations.sql"


@pytest.fixture
def empty_config() -> Config:
    """Empty configuration."""
    return Config() 