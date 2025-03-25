"""
Utilities for testing MCP Documentation Scraper components.

This module provides shared functionality for test cases.
"""

from unittest.mock import MagicMock
import tempfile
import os
import shutil
from pathlib import Path


class MockConfigManager:
    """A configurable mock for the ConfigManager class."""
    
    def __init__(self, config_data=None):
        """
        Initialize the mock config manager with optional config data.
        
        Args:
            config_data: Dictionary of configuration values
        """
        self.config_data = config_data or {}
        self._create_mock()
    
    def _create_mock(self):
        """Create the mock ConfigManager object."""
        self.mock = MagicMock()
        self.mock.get.side_effect = self._get
        self.mock.get_section.side_effect = self._get_section
    
    def _get(self, section, key, default=None):
        """Mock implementation of the get method."""
        if section in self.config_data and key in self.config_data[section]:
            return self.config_data[section][key]
        return default
    
    def _get_section(self, section):
        """Mock implementation of the get_section method."""
        return self.config_data.get(section, {})
    
    def update_config(self, section, key, value):
        """
        Update a configuration value.
        
        Args:
            section: Configuration section
            key: Configuration key
            value: New value
        """
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section][key] = value
    
    def update_section(self, section, section_data):
        """
        Update an entire configuration section.
        
        Args:
            section: Configuration section
            section_data: Dictionary of key-value pairs for the section
        """
        self.config_data[section] = section_data


class TestFileManager:
    """Utility for managing test files and directories."""
    
    def __init__(self):
        """Initialize the file manager."""
        self.temp_dirs = []
        self.temp_files = []
    
    def create_temp_dir(self):
        """
        Create a temporary directory.
        
        Returns:
            Path to the temporary directory
        """
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def create_temp_file(self, content="", suffix=".txt"):
        """
        Create a temporary file with the given content.
        
        Args:
            content: Content to write to the file
            suffix: File suffix
        
        Returns:
            Path to the temporary file
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(content.encode('utf-8'))
            temp_file_path = temp_file.name
        
        self.temp_files.append(temp_file_path)
        return temp_file_path
    
    def create_file_in_dir(self, directory, filename, content=""):
        """
        Create a file in the specified directory.
        
        Args:
            directory: Directory to create the file in
            filename: Name of the file
            content: Content to write to the file
        
        Returns:
            Path to the created file
        """
        file_path = Path(directory) / filename
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        return str(file_path)
    
    def cleanup(self):
        """Clean up all temporary files and directories."""
        for temp_file in self.temp_files:
            try:
                os.unlink(temp_file)
            except (OSError, FileNotFoundError):
                pass
        
        for temp_dir in self.temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except (OSError, FileNotFoundError):
                pass
        
        self.temp_files = []
        self.temp_dirs = []


# Default configuration for testing various components
DEFAULT_CONFIG = {
    "site": {
        "name": "ModelContextProtocol",
        "base_url": "https://example.com",
        "validation": {
            "enabled": True,
            "data_dir": "validation/data",
            "results_dir": "validation/results",
            "log_level": "INFO"
        }
    },
    "crawling": {
        "include_patterns": ["/docs/*"],
        "exclude_patterns": ["/blog/*"],
        "max_depth": 3,
        "rate_limit": 1
    },
    "extraction": {
        "content_selector": "main.content",
        "title_selector": "h1.title",
        "ignore_selectors": ["div.sidebar", "footer"]
    },
    "markdown": {
        "code_block_style": "fenced",
        "preserve_emphasis": True,
        "table_format": "pipe",
        "image_alt_text": True
    },
    "link_handling": {
        "internal_link_pattern": "^https?://example\\.com",
        "preserve_anchor_links": True,
        "image_handling": "download",
        "excluded_extensions": [".pdf", ".zip", ".exe"]
    },
    "output": {
        "base_dir": "TEST_DOCS",
        "file_prefix": "TEST_",
        "naming_convention": "UPPERCASE_WITH_UNDERSCORES"
    },
    "error_handling": {
        "log_level": "INFO",
        "max_retries": 3,
        "retry_delay": 1
    }
} 