"""Tests for the CLI functionality."""

from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest
from typer.testing import CliRunner

from ddlcheck.cli import app


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file."""
    config_content = """
    # DDLCheck configuration
    excluded_checks = ["add_column", "truncate"]
    """
    with NamedTemporaryFile(suffix=".toml", mode="w", delete=False) as f:
        f.write(config_content)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    temp_path.unlink()


def test_version(runner):
    """Test the version command."""
    # Act
    result = runner.invoke(app, ["version"])

    # Assert
    assert result.exit_code == 0
    assert "DDLCheck version" in result.stdout


def test_list_checks(runner):
    """Test the list-checks command."""
    # Act
    result = runner.invoke(app, ["list-checks"])

    # Assert
    assert result.exit_code == 0
    assert "add_column" in result.stdout
    assert "create_index" in result.stdout
    assert "update_without_filter" in result.stdout


def test_check_with_issues(runner, risky_sql_file):
    """Test the check command with a file that has issues."""
    # Act
    result = runner.invoke(app, ["check", str(risky_sql_file)])

    # Assert
    assert result.exit_code == 1  # Exit code 1 for issues found
    assert "issues" in result.stdout.lower()


def test_check_with_exclude(runner, risky_sql_file):
    """Test the check command with excluded checks."""
    # Act
    # Exclude add_column check
    result = runner.invoke(app, ["check", "--exclude", "add_column", str(risky_sql_file)])

    # Assert
    assert "add_column" not in result.stdout


def test_check_with_config_file(runner, risky_sql_file, temp_config_file):
    """Test the check command with a configuration file."""
    # Act
    result = runner.invoke(app, ["check", "--config", str(temp_config_file), str(risky_sql_file)])

    # Assert
    assert result.exit_code == 1  # Exit code 1 for issues found
    assert "add_column" not in result.stdout
    assert "truncate" not in result.stdout


def test_check_directory(runner, test_sql_dir):
    """Test checking an entire directory of SQL files."""
    # Act
    result = runner.invoke(app, ["check", str(test_sql_dir)])

    # Assert
    assert result.exit_code == 1  # Exit code 1 for issues found
    assert "risky_operations.sql" in result.stdout


def test_no_sql_files(runner):
    """Test handling when no SQL files are found."""
    # Create a temporary directory with no SQL files
    with TemporaryDirectory() as temp_dir:
        # Act
        result = runner.invoke(app, ["check", temp_dir])

        # Assert
        assert result.exit_code == 1
        assert "No SQL files found" in result.stdout


def test_check_nonexistent_file(runner):
    """Test handling when the specified file doesn't exist."""
    # Act
    result = runner.invoke(app, ["check", "nonexistent.sql"])

    # Assert
    assert result.exit_code != 0
    assert "does not exist" in result.stdout
