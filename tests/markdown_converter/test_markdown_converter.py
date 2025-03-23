"""
Tests for the Markdown Converter module.

These tests verify the functionality of converting HTML content to Markdown.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
from pathlib import Path
from bs4 import BeautifulSoup

# Import the MarkdownConverter class
from mcp_doc_getter.src.markdown_converter.markdown_converter import MarkdownConverter


class TestMarkdownConverter(unittest.TestCase):
    """Test cases for the MarkdownConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the ConfigManager
        self.mock_config = MagicMock()
        self.mock_config.get_conversion_config.return_value = {
            "include_metadata": True,
            "html2text_options": {
                "body_width": 0,
                "unicode_snob": True,
                "tables": True,
                "single_line_break": True
            },
            "code_block_style": "fenced",
            "table_style": "pipe"
        }
        
        # Load the test HTML fixture
        fixtures_dir = Path(__file__).parent / "fixtures"
        with open(fixtures_dir / "sample_html.html", "r") as f:
            self.test_html = f.read()
        
        # Parse the HTML for validation
        self.soup = BeautifulSoup(self.test_html, "html.parser")
        
        # Sample extracted content dict (similar to what ContentExtractor would produce)
        self.sample_content = {
            "title": "Main Header",
            "content": self.test_html,
            "url": "https://example.com/docs/sample-page",
            "metadata": {"path": "/docs/sample-page", "description": "A sample page"}
        }
        
        # Create a MarkdownConverter instance
        self.converter = MarkdownConverter(self.mock_config)
        
    def _mock_config_get(self, section, key, default=None):
        """Mock implementation for ConfigManager.get method."""
        config = {
            "markdown": {
                "code_block_style": "fenced",
                "preserve_emphasis": True,
                "table_format": "pipe",
                "image_alt_text": True
            }
        }
        
        if section in config and key in config[section]:
            return config[section][key]
        return default
    
    def test_convert_headings(self):
        """Test converting HTML headings to Markdown headings."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check that headings are properly converted
        self.assertIn("# Main Header", markdown)
        self.assertIn("## Section 1", markdown)
        self.assertIn("## Section 2", markdown)
        self.assertIn("### Nested Section", markdown)
    
    def test_convert_paragraphs(self):
        """Test converting HTML paragraphs to Markdown paragraphs."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check that paragraphs are properly converted
        self.assertIn("This is a sample paragraph with", markdown)
        self.assertIn("This is the first section with a", markdown)
    
    def test_convert_lists(self):
        """Test converting HTML lists to Markdown lists."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check unordered lists - html2text uses * for bullets
        self.assertIn("* Item 1", markdown)
        self.assertIn("* Item 2", markdown)
        
        # Check ordered lists
        self.assertIn("1. First item", markdown)
        self.assertIn("2. Second item", markdown)
        self.assertIn("3. Third item", markdown)
    
    def test_convert_code_blocks(self):
        """Test converting HTML code blocks to Markdown code blocks."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check that code blocks are properly converted - indentation is preserved
        self.assertIn("def hello_world():", markdown)
        self.assertIn("print(\"Hello, World!\")", markdown)
        self.assertIn("return True", markdown)
    
    def test_convert_tables(self):
        """Test converting HTML tables to Markdown tables."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check that tables are properly converted - html2text uses a slightly different format
        self.assertIn("Header 1 | Header 2 | Header 3", markdown)
        self.assertIn("---|---|---", markdown)
        self.assertIn("Row 1, Cell 1 | Row 1, Cell 2 | Row 1, Cell 3", markdown)
        self.assertIn("Row 2, Cell 1 | Row 2, Cell 2 | Row 2, Cell 3", markdown)
    
    def test_convert_links(self):
        """Test converting HTML links to Markdown links."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check that external links are properly converted
        self.assertIn("[link to an external site]", markdown)
        
        # Check that internal links are preserved for later processing by LinkHandler
        self.assertIn("[an internal page]", markdown)
        
        # Check that anchor links are preserved
        self.assertIn("internal anchor link", markdown)
    
    def test_convert_images(self):
        """Test converting HTML images to Markdown images."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check that images are properly converted with alt text
        self.assertIn("![Sample Image]", markdown)
    
    def test_convert_emphasis(self):
        """Test converting HTML emphasis (bold, italic) to Markdown."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check that bold and italic text is preserved - html2text uses _ for italic
        self.assertIn("**bold**", markdown)
        self.assertIn("_italic_", markdown)
    
    def test_convert_blockquotes(self):
        """Test converting HTML blockquotes to Markdown blockquotes."""
        # Convert the HTML to Markdown
        result = self.converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Check that blockquotes are properly converted
        self.assertIn("> This is a blockquote with a nested list:", markdown)
        self.assertIn(">   * Nested item 1", markdown)
        self.assertIn(">   * Nested item 2", markdown)
    
    def test_convert_with_options(self):
        """Test conversion with different configuration options."""
        # Test with different options
        custom_config = MagicMock()
        custom_config.get_conversion_config.return_value = {
            "include_metadata": False,
            "html2text_options": {
                "body_width": 80,
                "unicode_snob": False,
                "tables": True,
                "single_line_break": False
            },
            "code_block_style": "indented",
            "table_style": "grid"
        }
        
        # Create a converter with custom config
        custom_converter = MarkdownConverter(custom_config)
        result = custom_converter.convert(self.sample_content)
        markdown = result["content"]
        
        # Verify the result has the format property set
        self.assertEqual(result["format"], "markdown")
        
        # We don't need to verify the exact output here since the formatting details
        # will depend on the html2text implementation, but we can verify basic structure
        self.assertTrue(markdown.startswith("# Main Header"))
        self.assertNotIn("<!-- Metadata", markdown)  # Metadata should be excluded


if __name__ == "__main__":
    unittest.main() 