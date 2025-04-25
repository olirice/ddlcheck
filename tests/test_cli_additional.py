"""Additional tests for the CLI functionality."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from ddlcheck.cli import app, display_results, find_sql_files, format_severity
from ddlcheck.models import CheckResult, Issue, SeverityLevel


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


def test_format_severity():
    """Test format_severity function."""
    # Test all severity levels
    high = format_severity(SeverityLevel.HIGH)
    medium = format_severity(SeverityLevel.MEDIUM)
    low = format_severity(SeverityLevel.LOW)
    info = format_severity(SeverityLevel.INFO)
    
    # Check text content
    assert high.plain == "HIGH"
    assert medium.plain == "MEDIUM"
    assert low.plain == "LOW"
    assert info.plain == "INFO"
    
    # Check styling (styles are part of Rich objects)
    assert "bold red" in high.style
    assert "bold yellow" in medium.style
    assert "bold blue" in low.style
    assert "bold green" in info.style


def test_find_sql_files_single_file():
    """Test find_sql_files with a single file."""
    # Create a temporary SQL file
    with NamedTemporaryFile(suffix=".sql", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    
    try:
        # Test with single file
        files = find_sql_files(temp_path)
        assert len(files) == 1
        assert files[0] == temp_path
    finally:
        # Clean up
        os.unlink(temp_path)


def test_find_sql_files_non_sql_file():
    """Test find_sql_files with a non-SQL file."""
    # Create a temporary non-SQL file
    with NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
    
    try:
        # Test with non-SQL file
        files = find_sql_files(temp_path)
        assert len(files) == 0
    finally:
        # Clean up
        os.unlink(temp_path)


def test_find_sql_files_directory():
    """Test find_sql_files with a directory."""
    # Create a temporary directory with SQL files
    with TemporaryDirectory() as temp_dir:
        # Create SQL files
        sql_file1 = Path(temp_dir) / "file1.sql"
        sql_file2 = Path(temp_dir) / "file2.sql"
        non_sql_file = Path(temp_dir) / "file3.txt"
        
        # Create nested directory with SQL file
        nested_dir = Path(temp_dir) / "nested"
        os.makedirs(nested_dir)
        nested_sql_file = nested_dir / "nested.sql"
        
        # Write to files
        sql_file1.write_text("SELECT 1;")
        sql_file2.write_text("SELECT 2;")
        non_sql_file.write_text("Not SQL")
        nested_sql_file.write_text("SELECT 3;")
        
        # Test find_sql_files
        files = find_sql_files(Path(temp_dir))
        
        # Should find 3 SQL files
        assert len(files) == 3
        
        # Convert to set of Path names for easier comparison
        file_names = {str(f.name) for f in files}
        assert file_names == {"file1.sql", "file2.sql", "nested.sql"}


def test_display_results_no_issues():
    """Test display_results with no issues."""
    # Create a check result with no issues
    result = CheckResult(Path("test.sql"))
    
    # Mock console.print
    with patch("ddlcheck.cli.console.print") as mock_print:
        display_results([result])
        
        # Should print "No issues found"
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "No issues found" in args


def test_display_results_with_issues():
    """Test display_results with issues."""
    # Create a check result with issues
    result = CheckResult(Path("test.sql"))
    issue = Issue(
        check_id="test_check",
        message="Test message",
        line=10,
        severity=SeverityLevel.HIGH,
    )
    result.add_issue(issue)
    
    # Mock console.print
    with patch("ddlcheck.cli.console.print") as mock_print:
        display_results([result])
        
        # Should print the table with issues
        assert mock_print.call_count >= 2
        
        # Check if file path is in output
        file_path_call = False
        table_call = False
        
        for call in mock_print.call_args_list:
            arg = str(call[0][0])
            if "test.sql" in arg:
                file_path_call = True
            if "Table" in str(type(call[0][0])):
                table_call = True
        
        assert file_path_call
        assert table_call


def test_display_results_with_suggestion():
    """Test display_results with suggestion."""
    # Create a check result with an issue that has a suggestion
    result = CheckResult(Path("test.sql"))
    issue = Issue(
        check_id="test_check",
        message="Test message",
        line=10,
        severity=SeverityLevel.HIGH,
        suggestion="Test suggestion",
    )
    result.add_issue(issue)
    
    # Mock console.print
    with patch("ddlcheck.cli.console.print") as mock_print:
        display_results([result])
        
        # Should print suggestion panel
        panel_call = False
        
        for call in mock_print.call_args_list:
            if "Panel" in str(type(call[0][0])):
                panel_call = True
                # We can't easily check the Panel's content as a string
                # So we just check that there was a panel call
        
        assert panel_call


def test_cli_version(runner):
    """Test the version command."""
    with patch("ddlcheck.cli.__version__", "1.2.3"):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "DDLCheck version 1.2.3" in result.stdout


def test_cli_check_invalid_path(runner):
    """Test check command with an invalid path."""
    result = runner.invoke(app, ["check", "/nonexistent/path"])
    assert result.exit_code != 0
    assert "does not exist" in result.stdout


def test_cli_check_file_handler(runner):
    """Test check command with a log file."""
    # Create a temporary directory for the log file
    with TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Create a temporary SQL file
        with NamedTemporaryFile(suffix=".sql", mode="w", delete=False) as temp_file:
            temp_file.write("SELECT 1;")
            temp_path = Path(temp_file.name)
        
        try:
            # Run check with log file
            result = runner.invoke(app, ["check", "--log-file", str(log_file), str(temp_path)])
            
            # Command should succeed
            assert result.exit_code == 0
            
            # Log file should be created
            assert log_file.exists()
            
            # Log file should contain log messages
            log_content = log_file.read_text()
            assert "Found 1 SQL files to check" in log_content
        finally:
            # Clean up
            os.unlink(temp_path)


def test_cli_list_checks(runner):
    """Test list-checks command."""
    result = runner.invoke(app, ["list-checks"])
    assert result.exit_code == 0
    
    # Should list all checks
    assert "add_column" in result.stdout
    assert "HIGH" in result.stdout  # Severity level
    assert "MEDIUM" in result.stdout  # Severity level 