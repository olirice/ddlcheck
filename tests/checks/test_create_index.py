"""Tests for the create_index check."""

from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from ddlcheck.checks.create_index import CreateIndexCheck
from ddlcheck.models import Config


def create_temp_sql_file(content):
    """Create a temporary SQL file with the given content."""
    temp_file = NamedTemporaryFile(suffix=".sql", delete=False)
    temp_file.write(content.encode("utf-8"))
    temp_file.close()
    return Path(temp_file.name)


@pytest.fixture
def basic_sql_file():
    """SQL file with a basic CREATE INDEX statement."""
    sql = """
    -- Create an index
    CREATE INDEX idx_test ON mytable (column1);
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


@pytest.fixture
def concurrent_sql_file():
    """SQL file with a CONCURRENTLY CREATE INDEX statement."""
    sql = """
    -- Create an index concurrently
    CREATE INDEX CONCURRENTLY idx_test ON mytable (column1);
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


@pytest.fixture
def multiple_indexes_sql_file():
    """SQL file with multiple CREATE INDEX statements."""
    sql = """
    -- Create several indexes
    CREATE INDEX idx_test1 ON mytable (column1);
    CREATE INDEX idx_test2 ON mytable (column2);
    CREATE INDEX CONCURRENTLY idx_test3 ON mytable (column3);
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


@pytest.fixture
def create_unique_index_sql_file():
    """SQL file with a CREATE UNIQUE INDEX statement."""
    sql = """
    -- Create a unique index
    CREATE UNIQUE INDEX idx_test ON mytable (column1);
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
    CREATE INDEX idx_test ON test (id);
    ALTER TABLE test ADD COLUMN name text;
    """
    file_path = create_temp_sql_file(sql)
    yield file_path
    file_path.unlink()


def test_id_and_severity():
    """Test check ID and severity."""
    check = CreateIndexCheck()
    assert check.id == "create_index"
    assert check.description != ""


def test_basic_create_index(basic_sql_file):
    """Test detection of a basic CREATE INDEX statement."""
    check = CreateIndexCheck()
    result = check.check_file(basic_sql_file)

    # Should identify the issue
    assert result.has_issues()
    assert len(result.issues) == 1

    # Check issue details
    issue = result.issues[0]
    assert issue.check_id == "create_index"
    assert "index" in issue.message.lower()
    assert "concurrently" in issue.suggestion.lower()


def test_concurrent_create_index(concurrent_sql_file):
    """Test that CONCURRENTLY CREATE INDEX passes."""
    check = CreateIndexCheck()
    result = check.check_file(concurrent_sql_file)

    # Should not identify any issues
    assert not result.has_issues()


def test_multiple_indexes(multiple_indexes_sql_file):
    """Test detection of multiple CREATE INDEX statements."""
    check = CreateIndexCheck()
    result = check.check_file(multiple_indexes_sql_file)

    # Should identify two issues (the non-concurrent ones)
    assert result.has_issues()
    assert len(result.issues) == 2


def test_create_unique_index(create_unique_index_sql_file):
    """Test detection of CREATE UNIQUE INDEX."""
    check = CreateIndexCheck()
    result = check.check_file(create_unique_index_sql_file)

    # Should identify the issue (unique indexes should also be concurrent)
    assert result.has_issues()
    assert len(result.issues) == 1


def test_multiple_statement_types(multiple_statement_types_sql_file):
    """Test mixed statement types."""
    check = CreateIndexCheck()
    result = check.check_file(multiple_statement_types_sql_file)

    # Should only identify the CREATE INDEX issue
    assert result.has_issues()
    assert len(result.issues) == 1


def test_disabled_via_config():
    """Test check is disabled via config."""
    # Create config with this check excluded
    config = Config(excluded_checks={"create_index"})
    check = CreateIndexCheck(config)

    # Check should be disabled
    assert not check.enabled


def test_default_config_is_enabled():
    """Test check is enabled with default config."""
    check = CreateIndexCheck()
    assert check.enabled
