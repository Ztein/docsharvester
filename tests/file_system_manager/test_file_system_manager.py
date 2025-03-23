"""
Tests for the File System Manager module.

These tests verify the functionality of saving and managing files.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import shutil
from pathlib import Path

# Import the FileSystemManager class
from mcp_doc_getter.src.file_system_manager.file_system_manager import FileSystemManager


class TestFileSystemManager(unittest.TestCase):
    """Test cases for the FileSystemManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the ConfigManager
        self.mock_config = MagicMock()
        self.mock_config.get.side_effect = self._mock_config_get
        self.mock_config.get_section.side_effect = self._mock_config_get_section
        
        # Sample content dict (similar to what LinkHandler would produce)
        self.sample_content = {
            "title": "Sample Page",
            "content": "# Sample Page\n\nThis is some sample content.",
            "url": "https://example.com/docs/sample-page",
            "format": "markdown"
        }
        
        # Create FileSystemManager instance
        self.file_manager = FileSystemManager(self.mock_config)
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove the temporary directory after tests
        shutil.rmtree(self.temp_dir)
    
    def _mock_config_get(self, section, key, default=None):
        """Mock implementation for ConfigManager.get method."""
        config = {
            "output": {
                "base_dir": self.temp_dir,
                "file_prefix": "TEST_",
                "naming_convention": "UPPERCASE_WITH_UNDERSCORES"
            },
            "link_handling": {
                "image_handling": "download"
            }
        }
        
        if section in config and key in config[section]:
            return config[section][key]
        return default
    
    def _mock_config_get_section(self, section):
        """Mock implementation for ConfigManager.get_section method."""
        config = {
            "output": {
                "base_dir": self.temp_dir,
                "file_prefix": "TEST_",
                "naming_convention": "UPPERCASE_WITH_UNDERSCORES"
            },
            "link_handling": {
                "image_handling": "download"
            }
        }
        
        return config.get(section, {})
    
    def test_save_content(self):
        """Test saving content to a file."""
        # Save the content
        file_path = self.file_manager.save_content(self.sample_content, self.sample_content["url"])
        
        # Expected file path
        expected_file_path = Path(self.temp_dir) / "TEST_SAMPLE_PAGE.md"
        
        # Check that the file was created
        self.assertTrue(expected_file_path.exists())
        
        # Check that the content was written correctly
        with open(expected_file_path, "r") as f:
            content = f.read()
            self.assertEqual(content, self.sample_content["content"])
        
        # Check that the result matches the expected path
        self.assertEqual(file_path, expected_file_path)
    
    def test_create_directory_structure(self):
        """Test creating directory structure."""
        # Verify that the base directory was created
        self.assertTrue(Path(self.temp_dir).exists())
        
        # Verify that the images directory was created
        self.assertTrue((Path(self.temp_dir) / "images").exists())
    
    def test_filename_sanitization(self):
        """Test filename sanitization."""
        # Create content with special characters in the URL
        special_url = "https://example.com/docs/sample:page@with&special%characters"
        
        # Save the content
        file_path = self.file_manager.save_content(self.sample_content, special_url)
        
        # Check that the file was created with sanitized name
        self.assertTrue(file_path.exists())
        
        # Check the name doesn't contain special characters
        self.assertNotIn(":", file_path.name)
        self.assertNotIn("@", file_path.name)
        self.assertNotIn("&", file_path.name)
        self.assertNotIn("%", file_path.name)
    
    def test_filename_collision(self):
        """Test handling filename collisions."""
        # First save
        first_path = self.file_manager.save_content(self.sample_content, self.sample_content["url"])
        
        # Change the content but keep the same URL - this should be skipped
        modified_content = self.sample_content.copy()
        modified_content["content"] = "# Modified Content"
        
        # Try to save again with same URL
        second_path = self.file_manager.save_content(modified_content, self.sample_content["url"])
        
        # Paths should be the same
        self.assertEqual(first_path, second_path)
        
        # Check that the content was not overwritten
        with open(first_path, "r") as f:
            content = f.read()
            self.assertEqual(content, self.sample_content["content"])
    
    def test_different_naming_conventions(self):
        """Test different naming conventions."""
        # Override config to use lowercase_with_underscores
        self.mock_config.get_section.side_effect = lambda section: {
            "output": {
                "base_dir": self.temp_dir,
                "file_prefix": "test_",
                "naming_convention": "lowercase_with_underscores"
            },
            "link_handling": {
                "image_handling": "download"
            }
        }.get(section, {})
        
        # Create a new file manager with this config
        lowercase_file_manager = FileSystemManager(self.mock_config)
        
        # Save content
        file_path = lowercase_file_manager.save_content(self.sample_content, self.sample_content["url"])
        
        # Expected file name should be lowercase
        expected_name = "test_sample_page.md"
        self.assertEqual(file_path.name, expected_name)
        
        # Check that the file exists
        self.assertTrue(file_path.exists())
    
    def test_save_image(self):
        """Test saving an image."""
        # Create sample image data
        image_data = b"FAKE_IMAGE_DATA"
        image_url = "https://example.com/images/sample.png"
        
        # Save the image
        image_path = self.file_manager.save_image(image_url, image_data)
        
        # Expected image path
        expected_image_path = Path(self.temp_dir) / "images" / "sample.png"
        
        # Check that the image was saved
        self.assertEqual(image_path, expected_image_path)
        self.assertTrue(image_path.exists())
        
        # Check that the content is correct
        with open(image_path, "rb") as f:
            data = f.read()
            self.assertEqual(data, image_data)


if __name__ == "__main__":
    unittest.main() 