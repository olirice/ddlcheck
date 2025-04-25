"""Tests for the models module."""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch, mock_open

import pytest

from ddlcheck.models import Config, SeverityLevel, Issue, CheckResult


def test_issue_repr():
    """Test the Issue.__repr__ method."""
    issue = Issue(
        check_id="test_check",
        message="Test message",
        line=10,
        severity=SeverityLevel.HIGH,
    )
    repr_str = repr(issue)
    assert "test_check" in repr_str
    assert "10" in repr_str
    assert "HIGH" in repr_str


def test_config_from_file_default_path():
    """Test Config.from_file with default path."""
    # Mock Path.cwd() to return a known path
    mock_cwd = Path("/mock/cwd")
    with patch("pathlib.Path.cwd", return_value=mock_cwd):
        # Mock Path.exists() to return False for the default config path
        with patch("pathlib.Path.exists", return_value=False):
            config = Config.from_file()
            # Should return default config
            assert config.excluded_checks == set()
            assert config.check_config == {}
            assert config.severity_overrides == {}


def test_config_from_file_default_path_exists():
    """Test Config.from_file with default path that exists."""
    # Create a mock config file content
    config_content = """
    excluded_checks = ["check1", "check2"]
    
    [severity]
    check3 = "HIGH"
    
    [check4]
    option1 = "value1"
    """
    
    # Mock Path.cwd() to return a known path
    mock_cwd = Path("/mock/cwd")
    mock_config_path = mock_cwd / ".ddlcheck"
    
    with patch("pathlib.Path.cwd", return_value=mock_cwd):
        # Mock Path.exists() to return True for the default config path
        with patch("pathlib.Path.exists", return_value=True):
            # Mock open to return our config content
            with patch("builtins.open", mock_open(read_data=config_content)):
                config = Config.from_file()
                
                # Should load config from the default path
                assert config.excluded_checks == {"check1", "check2"}
                assert config.severity_overrides == {"check3": SeverityLevel.HIGH}
                assert config.check_config == {"check4": {"option1": "value1"}}


def test_config_from_file_custom_path():
    """Test Config.from_file with a custom path."""
    # Create a temporary file with config content
    config_content = """
    excluded_checks = ["check1", "check2"]
    
    [severity]
    check3 = "HIGH"
    
    [check4]
    option1 = "value1"
    """
    
    with NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as temp_file:
        temp_file.write(config_content)
        temp_path = Path(temp_file.name)
    
    try:
        # Load config from the temporary file
        config = Config.from_file(temp_path)
        
        # Check that config was loaded correctly
        assert config.excluded_checks == {"check1", "check2"}
        assert config.severity_overrides == {"check3": SeverityLevel.HIGH}
        assert config.check_config == {"check4": {"option1": "value1"}}
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def test_config_from_file_invalid_format():
    """Test Config.from_file with invalid TOML format."""
    # Invalid TOML content
    config_content = """
    excluded_checks = ["check1", "check2"
    severity = {
    """
    
    with NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as temp_file:
        temp_file.write(config_content)
        temp_path = Path(temp_file.name)
    
    try:
        # Load config from the invalid file
        with patch("ddlcheck.models.logger") as mock_logger:
            config = Config.from_file(temp_path)
            
            # Should log a warning
            assert mock_logger.warning.called
            
            # Should return default config
            assert config.excluded_checks == set()
            assert config.check_config == {}
            assert config.severity_overrides == {}
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def test_config_from_file_invalid_excluded_checks():
    """Test Config.from_file with invalid excluded_checks format."""
    # Config with invalid excluded_checks
    config_content = """
    excluded_checks = "not_a_list"
    """
    
    with NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as temp_file:
        temp_file.write(config_content)
        temp_path = Path(temp_file.name)
    
    try:
        # Load config from the file
        with patch("ddlcheck.models.logger") as mock_logger:
            config = Config.from_file(temp_path)
            
            # Should log a warning
            assert mock_logger.warning.called
            
            # Should have empty excluded_checks
            assert config.excluded_checks == set()
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def test_config_from_file_invalid_severity():
    """Test Config.from_file with invalid severity level."""
    # Config with invalid severity level
    config_content = """
    [severity]
    check1 = "INVALID_LEVEL"
    """
    
    with NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as temp_file:
        temp_file.write(config_content)
        temp_path = Path(temp_file.name)
    
    try:
        # Load config from the file
        with patch("ddlcheck.models.logger") as mock_logger:
            config = Config.from_file(temp_path)
            
            # Should log a warning
            assert mock_logger.warning.called
            
            # Should have empty severity_overrides
            assert config.severity_overrides == {}
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def test_config_from_file_invalid_check_config():
    """Test Config.from_file with invalid check config."""
    # Config with invalid check config
    config_content = """
    check1 = "not_a_dict"
    """
    
    with NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as temp_file:
        temp_file.write(config_content)
        temp_path = Path(temp_file.name)
    
    try:
        # Load config from the file
        with patch("ddlcheck.models.logger") as mock_logger:
            config = Config.from_file(temp_path)
            
            # Should log a warning
            assert mock_logger.warning.called
            
            # Should have empty check_config
            assert "check1" not in config.check_config
    finally:
        # Clean up the temporary file
        os.unlink(temp_path)


def test_is_check_enabled():
    """Test Config.is_check_enabled method."""
    # Create config with excluded checks
    config = Config(excluded_checks={"check1", "check2"})
    
    # Check if enabled
    assert config.is_check_enabled("check1") is False
    assert config.is_check_enabled("check2") is False
    assert config.is_check_enabled("check3") is True


def test_get_check_config():
    """Test Config.get_check_config method."""
    # Create config with check configs
    config = Config()
    config.check_config["check1"] = {"option1": "value1"}
    
    # Get check config
    assert config.get_check_config("check1") == {"option1": "value1"}
    assert config.get_check_config("nonexistent") == {}


def test_get_severity_override():
    """Test Config.get_severity_override method."""
    # Create config with severity overrides
    config = Config()
    config.severity_overrides["check1"] = SeverityLevel.HIGH
    
    # Get severity override
    assert config.get_severity_override("check1") == SeverityLevel.HIGH
    assert config.get_severity_override("nonexistent") is None


def test_check_result_init_and_add_issue():
    """Test CheckResult initialization and add_issue method."""
    # Create CheckResult
    file_path = Path("test.sql")
    result = CheckResult(file_path)
    
    # Should have no issues initially
    assert result.issues == []
    assert result.has_issues() is False
    
    # Add an issue
    issue = Issue(
        check_id="test_check",
        message="Test message",
        line=10,
        severity=SeverityLevel.HIGH,
    )
    result.add_issue(issue)
    
    # Should have one issue now
    assert len(result.issues) == 1
    assert result.issues[0] == issue
    assert result.has_issues() is True


def test_check_result_init_with_issues():
    """Test CheckResult initialization with issues."""
    # Create issues
    issues = [
        Issue(
            check_id="test_check",
            message="Test message 1",
            line=10,
            severity=SeverityLevel.HIGH,
        ),
        Issue(
            check_id="test_check",
            message="Test message 2",
            line=20,
            severity=SeverityLevel.MEDIUM,
        ),
    ]
    
    # Create CheckResult with issues
    file_path = Path("test.sql")
    result = CheckResult(file_path, issues)
    
    # Should have the issues
    assert len(result.issues) == 2
    assert result.issues == issues
    assert result.has_issues() is True


def test_check_result_repr():
    """Test CheckResult.__repr__ method."""
    # Create CheckResult with issues
    file_path = Path("test.sql")
    issues = [
        Issue(
            check_id="test_check",
            message="Test message",
            line=10,
            severity=SeverityLevel.HIGH,
        ),
    ]
    result = CheckResult(file_path, issues)
    
    # Check representation
    repr_str = repr(result)
    assert "test.sql" in repr_str
    assert "1" in repr_str  # Number of issues 