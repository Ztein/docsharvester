"""
Tests for the WebCrawler module.

These tests verify the functionality of the web crawler component.
"""

import unittest
from unittest.mock import MagicMock, patch
import time
from pathlib import Path

from mcp_doc_getter.src.web_crawler.web_crawler import WebCrawler
from mcp_doc_getter.src.config_manager.config_manager import ConfigManager


class TestWebCrawler(unittest.TestCase):
    """Test cases for the WebCrawler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the ConfigManager
        self.mock_config = MagicMock(spec=ConfigManager)
        
        # Set up default config values
        self.mock_config.get.side_effect = self._mock_config_get
        self.mock_config.get_section.side_effect = self._mock_config_get_section
        
        # Create a WebCrawler instance with the mock config
        self.crawler = WebCrawler(self.mock_config)
    
    def _mock_config_get(self, section, key, default=None):
        """Mock implementation for ConfigManager.get method."""
        config = {
            'site': {
                'base_url': 'https://example.com',
            },
            'crawling': {
                'rate_limit': 1,
                'max_depth': 3,
            },
            'error_handling': {
                'max_retries': 3,
                'retry_delay': 1,
            }
        }
        
        if section in config and key in config[section]:
            return config[section][key]
        return default
    
    def _mock_config_get_section(self, section):
        """Mock implementation for ConfigManager.get_section method."""
        config = {
            'site': {
                'base_url': 'https://example.com',
                'name': 'Example Site',
            },
            'crawling': {
                'rate_limit': 1,
                'max_depth': 3,
                'include_patterns': ['/docs/*'],
                'exclude_patterns': ['/blog/*'],
            },
            'error_handling': {
                'max_retries': 3,
                'retry_delay': 1,
                'log_level': 'INFO',
            }
        }
        
        return config.get(section, {})
    
    @patch('mcp_doc_getter.src.web_crawler.web_crawler.requests.get')
    def test_fetch_url_success(self, mock_get):
        """Test successful URL fetching."""
        # Set up the mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><a href="/docs/page1">Link 1</a></body></html>'
        mock_get.return_value = mock_response
        
        # Call fetch_url
        response = self.crawler.fetch_url('https://example.com/docs/')
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, '<html><body><a href="/docs/page1">Link 1</a></body></html>')
        
        # Verify that get was called with the correct URL
        mock_get.assert_called_once_with('https://example.com/docs/', timeout=10)
    
    @patch('mcp_doc_getter.src.web_crawler.web_crawler.requests.get')
    @patch('time.sleep')
    def test_fetch_url_retry(self, mock_sleep, mock_get):
        """Test URL fetching with retries."""
        # Mock get to fail twice, then succeed
        mock_fail_response = MagicMock()
        mock_fail_response.status_code = 500
        
        mock_success_response = MagicMock()
        mock_success_response.status_code = 200
        mock_success_response.text = '<html><body>Success</body></html>'
        
        mock_get.side_effect = [mock_fail_response, mock_fail_response, mock_success_response]
        
        # Call fetch_url
        response = self.crawler.fetch_url('https://example.com/docs/')
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        
        # Verify that get was called multiple times
        self.assertEqual(mock_get.call_count, 3)
        
        # Verify that sleep was called between retries
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch('mcp_doc_getter.src.web_crawler.web_crawler.requests.get')
    def test_robots_txt_parsing(self, mock_get):
        """Test parsing of robots.txt."""
        # Mock robots.txt response
        mock_robots_response = MagicMock()
        mock_robots_response.status_code = 200
        mock_robots_response.text = """
        User-agent: *
        Disallow: /private/
        Disallow: /admin/
        Allow: /docs/
        """
        mock_get.return_value = mock_robots_response
        
        # Initialize the WebCrawler to parse robots.txt
        self.crawler.initialize()
        
        # Test URL permission checking
        self.assertTrue(self.crawler.is_url_allowed('https://example.com/docs/page1'))
        self.assertFalse(self.crawler.is_url_allowed('https://example.com/private/page'))
        self.assertFalse(self.crawler.is_url_allowed('https://example.com/admin/dashboard'))
    
    @patch('mcp_doc_getter.src.web_crawler.web_crawler.requests.get')
    def test_url_filtering(self, mock_get):
        """Test URL filtering based on include/exclude patterns."""
        # Test URLs
        test_urls = [
            'https://example.com/docs/page1',  # Should be included
            'https://example.com/blog/post1',  # Should be excluded
            'https://example.com/docs/api/v1', # Should be included
            'https://example.com/about',       # Not matching any pattern
        ]
        
        # Check filtering
        included_urls = [url for url in test_urls if self.crawler.should_crawl_url(url)]
        
        # Verify filtering results
        self.assertIn('https://example.com/docs/page1', included_urls)
        self.assertIn('https://example.com/docs/api/v1', included_urls)
        self.assertNotIn('https://example.com/blog/post1', included_urls)
        
    @patch('mcp_doc_getter.src.web_crawler.web_crawler.requests.get')
    @patch('mcp_doc_getter.src.web_crawler.web_crawler.time.sleep')
    def test_rate_limiting(self, mock_sleep, mock_get):
        """Test rate limiting functionality."""
        # Set up mock responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<html><body>Content</body></html>'
        mock_get.return_value = mock_response
        
        # Make multiple requests
        for _ in range(3):
            self.crawler.fetch_url('https://example.com/docs/page')
        
        # Verify sleep was called between requests for rate limiting
        self.assertEqual(mock_sleep.call_count, 2)  # Called after 1st and 2nd requests
    
    @patch('mcp_doc_getter.src.web_crawler.web_crawler.requests.get')
    def test_extract_links(self, mock_get):
        """Test link extraction from HTML content."""
        # Set up a mock response with links
        html_content = """
        <html>
            <body>
                <a href="/docs/page1">Page 1</a>
                <a href="https://example.com/docs/page2">Page 2</a>
                <a href="https://another-site.com/page">External Link</a>
                <a href="/blog/post1">Blog Post</a>
            </body>
        </html>
        """
        
        # Extract links
        links = self.crawler.extract_links(html_content, 'https://example.com/docs/')
        
        # Verify extracted links
        self.assertIn('https://example.com/docs/page1', links)
        self.assertIn('https://example.com/docs/page2', links)
        self.assertIn('https://another-site.com/page', links)
        self.assertIn('https://example.com/blog/post1', links)
        
    @patch('mcp_doc_getter.src.web_crawler.web_crawler.requests.get')
    def test_crawl(self, mock_get):
        """Test the crawl functionality."""
        # Mock responses for different URLs
        responses = {
            'https://example.com/robots.txt': MagicMock(
                status_code=200,
                text='User-agent: *\nAllow: /'
            ),
            'https://example.com/docs/': MagicMock(
                status_code=200,
                text='<html><body><a href="/docs/page1">Page 1</a></body></html>'
            ),
            'https://example.com/docs/page1': MagicMock(
                status_code=200,
                text='<html><body><a href="/docs/page2">Page 2</a></body></html>'
            ),
            'https://example.com/docs/page2': MagicMock(
                status_code=200,
                text='<html><body>Content</body></html>'
            ),
        }
        
        mock_get.side_effect = lambda url, **kwargs: responses.get(url, MagicMock(status_code=404))
        
        # Call crawl
        result = self.crawler.crawl('https://example.com/docs/')
        
        # Verify crawl results
        self.assertIn('https://example.com/docs/', result)
        self.assertIn('https://example.com/docs/page1', result)
        self.assertIn('https://example.com/docs/page2', result)
        
        # Verify number of calls to get
        self.assertEqual(mock_get.call_count, 4)  # robots.txt + 3 pages


if __name__ == '__main__':
    unittest.main() 