"""
Tests for the Error Handler module.

These tests verify the functionality of error handling and logging.
"""

import unittest
from unittest.mock import MagicMock, patch
import logging
import io
import os
import tempfile
from pathlib import Path

from mcp_doc_getter.src.error_handler.error_handler import setup_error_handling, ErrorHandler, retry_on_exception


class TestErrorHandler(unittest.TestCase):
    """Test cases for the ErrorHandler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a StringIO to capture log output
        self.log_capture = io.StringIO()
        
        # Configure a basic handler that writes to our StringIO
        self.handler = logging.StreamHandler(self.log_capture)
        self.handler.setLevel(logging.DEBUG)
        
        # Create a formatter and set it on the handler
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        
        # Get the root logger and add our handler
        self.logger = logging.getLogger()
        self.logger.addHandler(self.handler)
        
        # Store the original level to restore later
        self.original_level = self.logger.level
        self.logger.setLevel(logging.DEBUG)
        
        # Mock the ConfigManager
        self.mock_config = MagicMock()
        self.mock_config.get.side_effect = self._mock_config_get
        self.mock_config.get_section.side_effect = self._mock_config_get_section
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove our handler and restore original level
        self.logger.removeHandler(self.handler)
        self.logger.setLevel(self.original_level)
        
    def _mock_config_get(self, section, key, default=None):
        """Mock implementation for ConfigManager.get method."""
        config = {
            "error_handling": {
                "log_level": "INFO",
                "max_retries": 3,
                "retry_delay": 1
            }
        }
        
        if section in config and key in config[section]:
            return config[section][key]
        return default
    
    def _mock_config_get_section(self, section):
        """Mock implementation for ConfigManager.get_section method."""
        config = {
            "error_handling": {
                "log_level": "INFO",
                "max_retries": 3,
                "retry_delay": 1
            }
        }
        
        return config.get(section, {})
    
    @patch('mcp_doc_getter.src.error_handler.error_handler.logging.basicConfig')
    def test_setup_error_handling(self, mock_basic_config):
        """Test setting up error handling."""
        # Call setup_error_handling
        setup_error_handling(self.mock_config)
        
        # Check that basicConfig was called with the correct arguments
        mock_basic_config.assert_called_once()
        args, kwargs = mock_basic_config.call_args
        self.assertEqual(kwargs['level'], logging.INFO)
        self.assertIn('format', kwargs)
        self.assertIn('handlers', kwargs)
    
    def test_error_handler_log_error(self):
        """Test logging an error with ErrorHandler."""
        # Instantiate ErrorHandler
        error_handler = ErrorHandler(self.mock_config)
        error_handler.log_error("Test module", "This is a test error", Exception("Test exception"))
        
        # Check that the error was logged
        log_output = self.log_capture.getvalue()
        self.assertIn("ERROR", log_output)
        self.assertIn("Test module", log_output)
        self.assertIn("This is a test error", log_output)
        self.assertIn("Test exception", log_output)
    
    def test_error_handler_log_warning(self):
        """Test logging a warning with ErrorHandler."""
        # Instantiate ErrorHandler
        error_handler = ErrorHandler(self.mock_config)
        error_handler.log_warning("Test module", "This is a test warning")
        
        # Check that the warning was logged
        log_output = self.log_capture.getvalue()
        self.assertIn("WARNING", log_output)
        self.assertIn("Test module", log_output)
        self.assertIn("This is a test warning", log_output)
    
    def test_error_handler_log_info(self):
        """Test logging info with ErrorHandler."""
        # Instantiate ErrorHandler
        error_handler = ErrorHandler(self.mock_config)
        error_handler.log_info("Test module", "This is a test info message")
        
        # Check that the info was logged
        log_output = self.log_capture.getvalue()
        self.assertIn("INFO", log_output)
        self.assertIn("Test module", log_output)
        self.assertIn("This is a test info message", log_output)
    
    @patch('time.sleep')
    def test_retry_decorator(self, mock_sleep):
        """Test the retry decorator."""
        # Create a function that raises an exception the first two times
        mock_function = MagicMock()
        mock_function.side_effect = [ValueError("First error"), ValueError("Second error"), "Success"]
        
        # Decorate the function with retry_on_exception
        decorated_function = retry_on_exception(max_retries=3, exceptions=(ValueError,))(mock_function)
        
        # Call the decorated function
        result = decorated_function("test_arg", kwarg="test_kwarg")
        
        # Check that the function was called multiple times
        self.assertEqual(mock_function.call_count, 3)
        self.assertEqual(result, "Success")
        
        # Check that sleep was called between retries
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch('time.sleep')
    def test_retry_max_retries_exceeded(self, mock_sleep):
        """Test retry decorator when max retries is exceeded."""
        # Create a function that always raises an exception
        mock_function = MagicMock()
        mock_function.side_effect = ValueError("Persistent error")
        
        # Decorate the function with retry_on_exception
        decorated_function = retry_on_exception(max_retries=3, exceptions=(ValueError,))(mock_function)
        
        # Call the decorated function and expect it to raise an exception
        with self.assertRaises(ValueError):
            decorated_function()
        
        # Check that the function was called the maximum number of times
        self.assertEqual(mock_function.call_count, 4)  # Initial call + 3 retries
        
        # Check that sleep was called between retries
        self.assertEqual(mock_sleep.call_count, 3)
    
    def test_error_handler_with_file_logging(self):
        """Test error handler with file logging."""
        # Create a temporary file for logging
        with tempfile.NamedTemporaryFile(delete=False) as log_file:
            log_file_path = log_file.name
        
        try:
            # Override config to use file logging
            self.mock_config.get_section.side_effect = lambda section: {
                "error_handling": {
                    "log_level": "DEBUG",
                    "log_file": log_file_path,
                    "max_retries": 3,
                    "retry_delay": 1
                }
            }.get(section, {})
            
            # Setup error handling with file logging
            with patch('mcp_doc_getter.src.error_handler.error_handler.logging.basicConfig') as mock_basic_config:
                setup_error_handling(self.mock_config)
                
                # Check that basicConfig was called with a FileHandler
                mock_basic_config.assert_called_once()
                args, kwargs = mock_basic_config.call_args
                self.assertEqual(kwargs['level'], logging.DEBUG)
                self.assertIn('handlers', kwargs)
                self.assertEqual(len(kwargs['handlers']), 2)  # Console + File handlers
                
        finally:
            # Clean up the temporary file
            os.unlink(log_file_path)


if __name__ == "__main__":
    unittest.main() 