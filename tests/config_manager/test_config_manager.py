"""
Tests for the ConfigManager module.
"""

import os
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import pytest
import yaml

from mcp_doc_getter.src.config_manager.config_manager import ConfigManager


class TestConfigManager(TestCase):
    """Tests for the ConfigManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary YAML file with valid configuration
        self.valid_config = {
            "site": {
                "name": "TestSite",
                "base_url": "https://example.com"
            },
            "crawling": {
                "include_patterns": ["/docs/*"],
                "exclude_patterns": ["/blog/*"],
                "max_depth": 5,
                "rate_limit": 1
            },
            "extraction": {
                "content_selector": "main.content",
                "title_selector": "h1.title"
            },
            "output": {
                "base_dir": "TEST_DOCS",
                "file_prefix": "TEST_"
            }
        }
        
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp_dir.name) / "test_config.yaml"
        
        with open(self.config_path, "w") as f:
            yaml.dump(self.valid_config, f)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file."""
        config_manager = ConfigManager(str(self.config_path))
        
        # Verify the configuration was loaded
        self.assertEqual(config_manager.config["site"]["name"], "TestSite")
        self.assertEqual(config_manager.config["site"]["base_url"], "https://example.com")
    
    def test_get_existing_config_value(self):
        """Test getting an existing configuration value."""
        config_manager = ConfigManager(str(self.config_path))
        
        # Get existing values
        self.assertEqual(config_manager.get("site", "name"), "TestSite")
        self.assertEqual(config_manager.get("crawling", "max_depth"), 5)
    
    def test_get_nonexistent_config_value(self):
        """Test getting a nonexistent configuration value."""
        config_manager = ConfigManager(str(self.config_path))
        
        # Get nonexistent values with default
        self.assertEqual(config_manager.get("nonexistent", "key", "default"), "default")
        self.assertEqual(config_manager.get("site", "nonexistent", 42), 42)
    
    def test_get_section(self):
        """Test getting an entire configuration section."""
        config_manager = ConfigManager(str(self.config_path))
        
        # Get existing section
        site_section = config_manager.get_section("site")
        self.assertEqual(site_section["name"], "TestSite")
        self.assertEqual(site_section["base_url"], "https://example.com")
        
        # Get nonexistent section
        nonexistent_section = config_manager.get_section("nonexistent")
        self.assertEqual(nonexistent_section, {})
    
    def test_missing_config_file(self):
        """Test handling a missing configuration file."""
        with self.assertRaises(FileNotFoundError):
            ConfigManager("nonexistent_file.yaml")
    
    def test_invalid_yaml(self):
        """Test handling invalid YAML."""
        invalid_yaml_path = Path(self.temp_dir.name) / "invalid.yaml"
        
        with open(invalid_yaml_path, "w") as f:
            f.write("invalid: yaml: value")
        
        with self.assertRaises(yaml.YAMLError):
            ConfigManager(str(invalid_yaml_path))
    
    def test_missing_required_section(self):
        """Test validation of missing required section."""
        # Create config missing the 'output' section
        invalid_config = self.valid_config.copy()
        del invalid_config["output"]
        
        invalid_config_path = Path(self.temp_dir.name) / "invalid_config.yaml"
        
        with open(invalid_config_path, "w") as f:
            yaml.dump(invalid_config, f)
        
        with self.assertRaises(ValueError) as context:
            ConfigManager(str(invalid_config_path))
        
        self.assertIn("Missing required section", str(context.exception))
    
    def test_missing_required_site_keys(self):
        """Test validation of missing required keys in site section."""
        # Create config missing the 'base_url' in site section
        invalid_config = self.valid_config.copy()
        invalid_config["site"] = {"name": "TestSite"}  # Missing base_url
        
        invalid_config_path = Path(self.temp_dir.name) / "invalid_site_config.yaml"
        
        with open(invalid_config_path, "w") as f:
            yaml.dump(invalid_config, f)
        
        with self.assertRaises(ValueError) as context:
            ConfigManager(str(invalid_config_path))
        
        self.assertIn("Site section must contain", str(context.exception)) 