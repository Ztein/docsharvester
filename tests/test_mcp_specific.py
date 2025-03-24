"""
Tests for MCP-specific implementation.

This module contains tests for the MCP-specific components.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from bs4 import BeautifulSoup

from mcp_doc_getter.src.mcp_specific.mcp_handlers import MCPContentHandler
from mcp_doc_getter.src.mcp_specific.mcp_extractor import MCPContentExtractor


class TestMCPContentHandler(unittest.TestCase):
    """Test the MCPContentHandler class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = MagicMock()
        self.mock_config.get_section.return_value = {
            'mcp_content_selector': 'main .doc-content',
            'ignore_selectors': ['.sidebar', 'nav', 'footer']
        }
        self.handler = MCPContentHandler(self.mock_config)
        
        # Sample HTML content for testing
        self.sample_html = """
        <html>
            <head>
                <title>MCP Test Page</title>
            </head>
            <body>
                <header>
                    <nav>Navigation</nav>
                    <div class="theme-switch">Theme</div>
                </header>
                <div class="sidebar">Sidebar</div>
                <main>
                    <div class="doc-content">
                        <h1>Test Heading</h1>
                        <p>Test paragraph</p>
                        <pre><code class="language-python">print("Hello")</code></pre>
                        <div class="language-tabs">
                            <div class="active">python</div>
                            <div>javascript</div>
                        </div>
                        <pre><code>console.log("Hello")</code></pre>
                        <table class="parameters">
                            <tr><th>Parameter</th><th>Description</th></tr>
                            <tr><td>param1</td><td>Description 1</td></tr>
                        </table>
                        <a href="/docs/guide">Internal Link</a>
                        <a href="https://external.site">External Link</a>
                        <a href="/api/method">API Link</a>
                    </div>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        self.soup = BeautifulSoup(self.sample_html, 'html.parser')
        
    def test_preprocess_html(self):
        """Test the preprocess_html method."""
        processed_soup = self.handler.preprocess_html(self.soup)
        
        # Check that navigation was removed
        self.assertIsNone(processed_soup.select_one('nav'))
        
        # Check that sidebar was removed
        self.assertIsNone(processed_soup.select_one('.sidebar'))
        
        # Check that theme switch was removed
        self.assertIsNone(processed_soup.select_one('.theme-switch'))
        
        # Check that main content remains
        self.assertIsNotNone(processed_soup.select_one('.doc-content'))
    
    def test_process_code_blocks(self):
        """Test the process_code_blocks method."""
        content = self.soup.select_one('main')
        self.handler.process_code_blocks(content)
        
        # Check that code blocks have been processed
        code_blocks = content.select('pre')
        self.assertTrue('mcp-code-block' in code_blocks[0].get('class', []))
        self.assertEqual(code_blocks[0].get('data-language'), 'python')
        
        # Check that the second code block has language from tabs
        self.assertTrue('mcp-code-block' in code_blocks[1].get('class', []))
        
    def test_process_tables(self):
        """Test the process_tables method."""
        content = self.soup.select_one('main')
        self.handler.process_tables(content)
        
        # Check that tables have been processed
        tables = content.select('table')
        self.assertTrue('mcp-table' in tables[0].get('class', []))
    
    def test_process_links(self):
        """Test the process_links method."""
        content = self.soup.select_one('main')
        self.handler.process_links(content, 'https://modelcontextprotocol.io')
        
        # Check that links have been processed
        links = content.select('a')
        self.assertEqual(links[0].get('data-internal'), 'true')
        self.assertIsNone(links[1].get('data-internal'))
        self.assertEqual(links[2].get('data-api-ref'), 'true')
    
    def test_postprocess_markdown(self):
        """Test the postprocess_markdown method."""
        markdown = """
# Test

```
print("Hello")
```

Some text

```python
def test():
    return True
```
        """
        
        processed = self.handler.postprocess_markdown(markdown)
        
        # Check that the first code block now has a language specifier
        self.assertIn('```python', processed)
        self.assertNotIn('```\nprint', processed)


class TestMCPContentExtractor(unittest.TestCase):
    """Test the MCPContentExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_config = MagicMock()
        self.mock_config.get_extraction_config.return_value = {
            'mcp_content_selector': 'main .doc-content',
            'title_selector': 'h1.title, h1',
            'ignore_selectors': ['.sidebar', 'nav', 'footer']
        }
        self.mock_config.get.return_value = 'https://modelcontextprotocol.io'
        self.mock_config.get_section.return_value = {
            'mcp_content_selector': 'main .doc-content',
            'ignore_selectors': ['.sidebar', 'nav', 'footer']
        }
        
        self.extractor = MCPContentExtractor(self.mock_config)
        
        # Sample HTML content for testing
        self.sample_html = """
        <html>
            <head>
                <title>MCP Test Page</title>
                <meta name="description" content="Test description">
            </head>
            <body>
                <header>
                    <nav>Navigation</nav>
                </header>
                <div class="sidebar">Sidebar</div>
                <main>
                    <h1 class="title">Test Title</h1>
                    <div class="doc-content">
                        <p>Test paragraph</p>
                        <pre><code class="language-python">print("Hello")</code></pre>
                        <footer class="version">v1.0.0</footer>
                    </div>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """
    
    def test_extract(self):
        """Test the extract method."""
        url = 'https://modelcontextprotocol.io/docs/core/intro'
        result = self.extractor.extract(self.sample_html, url)
        
        # Check basic extraction results
        self.assertEqual(result['url'], url)
        self.assertEqual(result['title'], 'Test Title')
        self.assertIn('Test paragraph', result['content'])
        
        # Check MCP-specific metadata
        self.assertEqual(result['metadata']['mcp_section'], 'core')
        
    def test_extract_main_content(self):
        """Test the _extract_main_content method."""
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        content = self.extractor._extract_main_content(soup)
        
        # Check that content was extracted correctly
        self.assertIn('Test paragraph', content)
        self.assertIn('print("Hello")', content)
        
        # Check that irrelevant content was removed
        self.assertNotIn('Navigation', content)
        self.assertNotIn('Sidebar', content)
        
    def test_extract_mcp_metadata(self):
        """Test the _extract_mcp_metadata method."""
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        url = 'https://modelcontextprotocol.io/docs/python/client'
        metadata = self.extractor._extract_mcp_metadata(soup, url)
        
        # Check MCP-specific metadata
        self.assertEqual(metadata['mcp_section'], 'python')
        self.assertEqual(metadata['mcp_version'], 'v1.0.0')


if __name__ == '__main__':
    unittest.main() 