"""
Tests for the Link Handler module.

These tests verify the functionality of processing links in Markdown content.
"""

import unittest
import re
from unittest.mock import MagicMock, patch
import os
from pathlib import Path

# Import the LinkHandler class
from mcp_doc_getter.src.link_handler.link_handler import LinkHandler


class TestLinkHandler(unittest.TestCase):
    """Test cases for the LinkHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the ConfigManager
        self.mock_config = MagicMock()
        self.mock_config.get.side_effect = self._mock_config_get
        self.mock_config.get_section.side_effect = self._mock_config_get_section
        
        # Load the test Markdown fixture
        fixtures_dir = Path(__file__).parent / "fixtures"
        with open(fixtures_dir / "sample_markdown.md", "r") as f:
            self.test_markdown = f.read()
        
        # Sample content dict (similar to what MarkdownConverter would produce)
        self.sample_content = {
            "title": "Main Header",
            "content": self.test_markdown,
            "url": "https://example.com/docs/sample-page",
            "format": "markdown"
        }
        
        # Create a LinkHandler instance
        self.link_handler = LinkHandler(self.mock_config)
        
    def _mock_config_get(self, section, key, default=None):
        """Mock implementation for ConfigManager.get method."""
        config = {
            "site": {
                "base_url": "https://example.com",
                "name": "Example Site"
            },
            "link_handling": {
                "internal_link_pattern": "^https?://example\\.com",
                "preserve_anchor_links": True,
                "image_handling": "download"
            },
            "output": {
                "base_dir": "EXAMPLE_DOCS",
                "file_prefix": "EXAMPLE_",
                "naming_convention": "UPPERCASE_WITH_UNDERSCORES"
            }
        }
        
        if section in config and key in config[section]:
            return config[section][key]
        return default
    
    def _mock_config_get_section(self, section):
        """Mock implementation for ConfigManager.get_section method."""
        config = {
            "site": {
                "base_url": "https://example.com",
                "name": "Example Site"
            },
            "link_handling": {
                "internal_link_pattern": "^https?://example\\.com",
                "preserve_anchor_links": True,
                "image_handling": "download"
            },
            "output": {
                "base_dir": "EXAMPLE_DOCS",
                "file_prefix": "EXAMPLE_",
                "naming_convention": "UPPERCASE_WITH_UNDERSCORES"
            }
        }
        
        return config.get(section, {})
    
    def test_identify_internal_links(self):
        """Test identifying internal links based on configuration."""
        # Process links in the content
        processed_content = self.link_handler.process_links(self.sample_content, self.sample_content["url"])
        
        # Check that internal links are properly identified and converted
        self.assertIn("./EXAMPLE_ANOTHER_PAGE.md", processed_content["content"])
        # Check that external links are preserved
        self.assertIn("https://external.com", processed_content["content"])
    
    def test_handle_absolute_internal_links(self):
        """Test handling absolute internal links."""
        # Create a sample with absolute internal links
        content_with_absolute_links = self.sample_content.copy()
        content_with_absolute_links["content"] = content_with_absolute_links["content"].replace(
            "/docs/another-page",
            "https://example.com/docs/another-page"
        )
        
        # Process links in the content
        processed_content = self.link_handler.process_links(content_with_absolute_links, content_with_absolute_links["url"])
        
        # Check results
        self.assertIn("./EXAMPLE_ANOTHER_PAGE.md", processed_content["content"])
        self.assertNotIn("https://example.com/docs/another-page", processed_content["content"])
    
    def test_handle_relative_internal_links(self):
        """Test handling relative internal links."""
        # Create a sample with relative internal links
        content_with_relative_links = self.sample_content.copy()
        
        # Process links in the content
        processed_content = self.link_handler.process_links(content_with_relative_links, content_with_relative_links["url"])
        
        # Check results
        self.assertIn("./EXAMPLE_ANOTHER_PAGE.md", processed_content["content"])
        self.assertNotIn("/docs/another-page", processed_content["content"])
    
    def test_preserve_anchor_links(self):
        """Test preserving anchor links."""
        # Process links in the content
        processed_content = self.link_handler.process_links(self.sample_content, self.sample_content["url"])
        
        # Check results
        self.assertIn("#section-1", processed_content["content"])
    
    def test_handle_image_links(self):
        """Test handling image links with download option."""
        # Process links in the content
        processed_content = self.link_handler.process_links(self.sample_content, self.sample_content["url"])
        
        # Check results - images should be converted to local paths
        self.assertIn("./images/", processed_content["content"])
        self.assertNotIn("![Sample Image](/images/sample.png)", processed_content["content"])
    
    def test_image_reference_option(self):
        """Test handling image links with reference option."""
        # Create a mock config with reference option
        ref_config = MagicMock()
        ref_config.get_section.side_effect = lambda section: {
            "site": {
                "base_url": "https://example.com", 
                "name": "Example Site"
            },
            "link_handling": {
                "internal_link_pattern": "^https?://example\\.com",
                "preserve_anchor_links": True,
                "image_handling": "reference"
            },
            "output": {
                "base_dir": "EXAMPLE_DOCS",
                "file_prefix": "EXAMPLE_",
                "naming_convention": "UPPERCASE_WITH_UNDERSCORES"
            }
        }.get(section, {})
        
        # Create a new LinkHandler with the reference config
        link_handler_with_ref = LinkHandler(ref_config)
        processed_content = link_handler_with_ref.process_links(self.sample_content, self.sample_content["url"])
        
        # Check results - images should remain as absolute URLs
        self.assertIn("https://example.com/docs/EXAMPLE_SAMPLE.md", processed_content["content"])
    
    def test_link_to_anchor_in_another_page(self):
        """Test handling links to anchors in another page."""
        # Create a sample with links to anchors in another page
        content_with_anchor_links = self.sample_content.copy()
        content_with_anchor_links["content"] = content_with_anchor_links["content"].replace(
            "/docs/another-page",
            "/docs/another-page#section-2"
        )
        
        # Process links in the content
        processed_content = self.link_handler.process_links(content_with_anchor_links, content_with_anchor_links["url"])
        
        # Check results
        self.assertIn("./EXAMPLE_ANOTHER_PAGE.md#section-2", processed_content["content"])


if __name__ == "__main__":
    unittest.main() 