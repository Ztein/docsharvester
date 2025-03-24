import unittest
from unittest.mock import patch, MagicMock
import os
from pathlib import Path
from bs4 import BeautifulSoup

from mcp_doc_getter.src.content_extractor import ContentExtractor


class TestContentExtractor(unittest.TestCase):
    """Test case for the ContentExtractor class."""

    def setUp(self):
        """Set up the test case."""
        self.config = MagicMock()
        self.config.get_extraction_config.return_value = {
            'content_selector': 'main.content',
            'title_selector': 'h1.title',
            'ignore_selectors': ['div.sidebar', 'footer']
        }
        self.extractor = ContentExtractor(self.config)
        
        # Test HTML content
        self.test_html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <header>
        <h1 class="title">Test Title</h1>
    </header>
    <div class="sidebar">
        <ul>
            <li>Link 1</li>
            <li>Link 2</li>
        </ul>
    </div>
    <main class="content">
        <h2>Section 1</h2>
        <p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
        <pre><code>def hello_world():
    print("Hello, World!")
        </code></pre>
        <h2>Section 2</h2>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <table>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
            </tr>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
        </table>
    </main>
    <footer>
        <p>Footer text</p>
    </footer>
</body>
</html>"""

    def test_extract_content(self):
        """Test extracting content from HTML."""
        result = self.extractor.extract(self.test_html, 'https://example.com/test-page')
        
        # Check that the result is a dictionary with the expected keys
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIn('content', result)
        self.assertIn('url', result)
        
        # Check the title
        self.assertEqual(result['title'], 'Test Title')
        
        # Check the content
        soup = BeautifulSoup(result['content'], 'html.parser')
        
        # Check that the main content is included
        self.assertIsNotNone(soup.find('h2', string='Section 1'))
        self.assertIsNotNone(soup.find('pre'))
        self.assertIsNotNone(soup.find('table'))
        
        # Check that ignored elements are not included
        self.assertIsNone(soup.find('div', class_='sidebar'))
        self.assertIsNone(soup.find('footer'))
        
    def test_extract_title(self):
        """Test extracting title from HTML."""
        soup = BeautifulSoup(self.test_html, 'html.parser')
        
        title = self.extractor._extract_title(soup)
        self.assertEqual(title, 'Test Title')
        
    def test_extract_content_missing_selectors(self):
        """Test extraction with missing selectors."""
        # Create a new config with missing selectors
        config = MagicMock()
        config.get_extraction_config.return_value = {
            'content_selector': 'main.nonexistent',
            'title_selector': 'h1.nonexistent',
            'ignore_selectors': ['div.sidebar', 'footer']
        }
        extractor = ContentExtractor(config)
        
        # Should not raise an exception, but return fallback content
        result = extractor.extract(self.test_html, 'https://example.com/test-page')
        
        # Check that we have default title and some content
        self.assertEqual(result['title'], 'Test Page')
        self.assertIsNotNone(result['content'])
        
    def test_filter_elements(self):
        """Test filtering elements based on ignore selectors."""
        soup = BeautifulSoup(self.test_html, 'html.parser')
        main_content = soup.find('main', class_='content')
        
        # Add an element that should be ignored
        sidebar = soup.new_tag('div', attrs={'class': 'sidebar'})
        sidebar.string = 'This should be removed'
        main_content.append(sidebar)
        
        # Filter the elements
        filtered_content = self.extractor._filter_elements(main_content)
        
        # Check that the sidebar was removed
        self.assertIsNone(filtered_content.find('div', class_='sidebar'))
        
    def test_handle_code_blocks(self):
        """Test special handling for code blocks."""
        result = self.extractor.extract(self.test_html, 'https://example.com/test-page')
        soup = BeautifulSoup(result['content'], 'html.parser')
        
        # Check that code blocks are preserved
        code_block = soup.find('pre')
        self.assertIsNotNone(code_block)
        self.assertIn('def hello_world():', code_block.text)


if __name__ == '__main__':
    unittest.main() 