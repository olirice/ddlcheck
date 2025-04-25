"""Tests for the drop_table check."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from ddlcheck.checks.drop_table import DropTableCheck
from ddlcheck.models import Config, SeverityLevel


def create_temp_sql_file(content):
    """Create a temporary SQL file with the given content."""
    temp_file = NamedTemporaryFile(suffix=".sql", delete=False)
    temp_file.write(content.encode("utf-8"))
    temp_file.close()
    return Path(temp_file.name)


@pytest.fixture
def basic_drop_table_sql_file():
    """SQL file with a basic DROP TABLE statement."""
    sql = """
    -- Drop a table
    DROP TABLE mytable;
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


@pytest.fixture
def if_exists_sql_file():
    """SQL file with DROP TABLE IF EXISTS statement."""
    sql = """
    -- Drop a table if it exists
    DROP TABLE IF EXISTS mytable;
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


@pytest.fixture
def cascade_sql_file():
    """SQL file with DROP TABLE CASCADE statement."""
    sql = """
    -- Drop a table with cascade
    DROP TABLE mytable CASCADE;
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


@pytest.fixture
def multiple_drop_tables_sql_file():
    """SQL file with multiple DROP TABLE statements."""
    sql = """
    -- Drop several tables
    DROP TABLE table1;
    DROP TABLE IF EXISTS table2;
    DROP TABLE table3 CASCADE;
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


@pytest.fixture
def multiple_statement_types_sql_file():
    """SQL file with mixed statement types."""
    sql = """
    -- Various statements
    CREATE TABLE test (id int);
    DROP TABLE oldtable;
    ALTER TABLE test ADD COLUMN name text;
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


def test_id_and_severity():
    """Test check ID and severity."""
    check = DropTableCheck()
    assert check.id == "drop_table"
    assert check.description != ""
    assert check.severity == SeverityLevel.HIGH


def test_basic_drop_table(basic_drop_table_sql_file):
    """Test detection of a basic DROP TABLE statement."""
    check = DropTableCheck()
    result = check.check_file(basic_drop_table_sql_file)

    # Should identify the issue
    assert result.has_issues()
    assert len(result.issues) == 1

    # Check issue details
    issue = result.issues[0]
    assert issue.check_id == "drop_table"
    assert "DROP TABLE operation" in issue.message
    assert "renaming the table" in issue.suggestion


def test_if_exists_drop_table(if_exists_sql_file):
    """Test detection of DROP TABLE IF EXISTS."""
    check = DropTableCheck()
    result = check.check_file(if_exists_sql_file)

    # The current implementation flags all DROP TABLE operations
    assert result.has_issues()
    assert len(result.issues) == 1
    assert "DROP TABLE operation" in result.issues[0].message


def test_cascade_drop_table(cascade_sql_file):
    """Test detection of DROP TABLE CASCADE."""
    check = DropTableCheck()
    result = check.check_file(cascade_sql_file)

    # Should identify the issue
    assert result.has_issues()
    assert len(result.issues) == 1

    # Check issue details
    issue = result.issues[0]
    assert issue.check_id == "drop_table"
    assert "DROP TABLE operation" in issue.message


def test_multiple_drop_tables(multiple_drop_tables_sql_file):
    """Test detection of multiple DROP TABLE statements."""
    check = DropTableCheck()
    result = check.check_file(multiple_drop_tables_sql_file)

    # Should identify issues for all DROP TABLE statements
    assert result.has_issues()
    assert len(result.issues) == 3


def test_multiple_statement_types(multiple_statement_types_sql_file):
    """Test mixed statement types."""
    check = DropTableCheck()
    result = check.check_file(multiple_statement_types_sql_file)

    # Should only identify the DROP TABLE issue
    assert result.has_issues()
    assert len(result.issues) == 1
    assert "DROP TABLE operation" in result.issues[0].message


def test_disabled_via_config():
    """Test check is disabled via config."""
    # Create config with this check excluded
    config = Config(excluded_checks={"drop_table"})
    check = DropTableCheck(config)

    # Check should be disabled
    assert not check.enabled


def test_severity_override():
    """Test severity override via config."""
    # Create config with severity override
    config = Config()
    config.severity_overrides["drop_table"] = SeverityLevel.MEDIUM
    check = DropTableCheck(config)

    # Check effective severity
    assert check.effective_severity == SeverityLevel.MEDIUM
