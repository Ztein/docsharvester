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
import json
from datetime import datetime

# Import the FileSystemManager class
from mcp_doc_getter.src.file_system_manager.file_system_manager import FileSystemManager


class TestFileSystemManager(unittest.TestCase):
    """Test cases for the FileSystemManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.manager = FileSystemManager(self.test_dir)
        
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
        
    def test_save_content(self):
        """Test saving content to a file."""
        content = {
            "content": "# Test Content\n\nThis is a test.",
            "url": "https://example.com/test"
        }
        
        file_path = self.manager.save_content(content, content["url"])
        self.assertTrue(file_path.exists())
        with open(file_path) as f:
            saved_content = f.read()
        self.assertEqual(saved_content, content["content"])
        
    def test_save_image(self):
        """Test saving an image."""
        image_data = b"fake image data"
        image_url = "https://example.com/image.png"
        
        file_path = self.manager.save_image(image_data, image_url)
        self.assertTrue(file_path.exists())
        with open(file_path, "rb") as f:
            saved_data = f.read()
        self.assertEqual(saved_data, image_data)
        
    def test_filename_sanitization(self):
        """Test filename sanitization."""
        urls = [
            "https://example.com/test page",
            "https://example.com/test/page",
            "https://example.com/test?param=value",
            "https://example.com/test#section"
        ]
        
        for url in urls:
            file_path = self.manager._get_file_path(url)
            self.assertFalse(" " in str(file_path))
            self.assertTrue(file_path.suffix == ".md")
            
    def test_filename_collision(self):
        """Test handling of filename collisions."""
        content1 = {
            "content": "Content 1",
            "url": "https://example.com/test"
        }
        content2 = {
            "content": "Content 2",
            "url": "https://example.com/test"
        }
        
        path1 = self.manager.save_content(content1, content1["url"])
        path2 = self.manager.save_content(content2, content2["url"])
        
        self.assertNotEqual(path1, path2)
        self.assertTrue(path1.exists())
        self.assertTrue(path2.exists())
        
    def test_different_naming_conventions(self):
        """Test different naming conventions."""
        url = "https://example.com/test-page"
        file_path = self.manager._get_file_path(url)
        self.assertTrue("_" in str(file_path))
        self.assertFalse("-" in str(file_path))
        
    def test_create_directory_structure(self):
        """Test directory structure creation."""
        self.assertTrue(self.manager.content_dir.exists())
        self.assertTrue(self.manager.images_dir.exists())


if __name__ == "__main__":
    unittest.main() 