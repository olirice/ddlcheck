"""Tests for the logger module."""

import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest

from ddlcheck.logger import setup_logging


def test_setup_logging_basic():
    """Test basic setup of logging."""
    # Reset root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up logging with default parameters
    setup_logging()
    
    # Check that root logger has a handler
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0], logging.StreamHandler)
    assert root_logger.level == logging.INFO


def test_setup_logging_debug_level():
    """Test setting log level to DEBUG."""
    # Reset root logger
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up logging with DEBUG level
    setup_logging("DEBUG")
    
    # Check log level
    assert root_logger.level == logging.DEBUG


def test_setup_logging_invalid_level():
    """Test invalid log level."""
    # Should raise ValueError
    with pytest.raises(ValueError):
        setup_logging("INVALID_LEVEL")


def test_setup_logging_with_file():
    """Test logging to a file."""
    # Use a temporary directory for the log file
    with TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        
        # Reset root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set up logging with a file
        setup_logging("INFO", log_file)
        
        # Check that root logger has both handlers
        assert len(root_logger.handlers) == 2
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)
        assert isinstance(root_logger.handlers[1], logging.handlers.RotatingFileHandler)
        
        # Test logging to file
        test_message = "Test log message"
        logging.info(test_message)
        
        # Check that the message was written to the file
        with open(log_file, "r") as f:
            log_content = f.read()
            assert test_message in log_content


def test_setup_logging_nested_directory():
    """Test logging to a file in a nested directory."""
    # Use a temporary directory for the log file
    with TemporaryDirectory() as temp_dir:
        nested_dir = Path(temp_dir) / "nested" / "dir"
        log_file = nested_dir / "test.log"
        
        # Reset root logger
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set up logging with a file in a nested directory
        setup_logging("INFO", log_file)
        
        # Directory should be created
        assert nested_dir.exists()
        
        # Log something to create the file
        logging.info("Test log message")
        
        # Log file should exist
        assert log_file.exists()


def test_pglast_logger_level():
    """Test that pglast logger level is set to WARNING."""
    # Reset logging
    original_getLogger = logging.getLogger
    root_logger = original_getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create a mock for the pglast logger
    pglast_logger = MagicMock()
    
    # Mock the getLogger function without causing recursion
    def mock_get_logger(name=''):
        if name == "pglast":
            return pglast_logger
        return original_getLogger(name)
    
    with patch("logging.getLogger", side_effect=mock_get_logger):
        setup_logging()
    
    # Check that pglast logger level was set to WARNING
    pglast_logger.setLevel.assert_called_once_with(logging.WARNING) 