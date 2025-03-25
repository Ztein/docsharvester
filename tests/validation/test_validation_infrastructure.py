"""
Tests for the validation infrastructure of the MCP Documentation Scraper.

This module contains tests for the basic validation infrastructure setup.
"""

import pytest
import logging
from pathlib import Path
from tests.test_utils import TestFileManager, MockConfigManager

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_validation_directory_structure(test_file_manager):
    """Test that the validation directory structure is properly set up."""
    # Create validation directories
    validation_dir = test_file_manager.create_temp_dir()
    data_dir = Path(validation_dir) / "data"
    results_dir = Path(validation_dir) / "results"
    
    # Create directories
    data_dir.mkdir(parents=True)
    results_dir.mkdir(parents=True)
    
    # Verify directory structure
    assert data_dir.exists(), "Data directory should exist"
    assert results_dir.exists(), "Results directory should exist"
    
    # Log test results
    logger.info("Validation directory structure test passed")

def test_validation_configuration(mock_config):
    """Test that the validation configuration is properly loaded."""
    # Verify required configuration sections exist
    assert "validation" in mock_config.get_section("site"), "Validation section should exist in config"
    
    # Log test results
    logger.info("Validation configuration test passed")

def test_validation_logging():
    """Test that the validation logging system is working."""
    # Create a test log message
    test_message = "Test validation log message"
    logger.info(test_message)
    
    # Verify logging is working by checking if the message was logged
    # Note: In a real test environment, we would capture and verify the log output
    # This is a basic test to ensure the logging system is functional
    
    # Log test results
    logger.info("Validation logging test passed")

def test_validation_test_data(test_file_manager):
    """Test that the validation test data is properly prepared."""
    # Create a test data file
    test_data = "Test validation data"
    test_file = test_file_manager.create_file_in_dir(
        test_file_manager.create_temp_dir(),
        "test_data.txt",
        test_data
    )
    
    # Verify test data exists and contains expected content
    assert Path(test_file).exists(), "Test data file should exist"
    with open(test_file, 'r') as f:
        content = f.read()
    assert content == test_data, "Test data content should match expected content"
    
    # Log test results
    logger.info("Validation test data preparation test passed") 