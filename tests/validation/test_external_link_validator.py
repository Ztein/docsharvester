"""
Tests for the External Link Validator module.

These tests verify the functionality of validating external links in documentation.
"""

import unittest
from unittest.mock import MagicMock, patch
from requests.exceptions import RequestException
import requests

from mcp_doc_getter.src.validation.external_link_validator import ExternalLinkValidator


class TestExternalLinkValidator(unittest.TestCase):
    """Test cases for the ExternalLinkValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the ConfigManager
        self.mock_config = MagicMock()
        self.mock_config.get.side_effect = self._mock_config_get
        self.mock_config.get_section.side_effect = self._mock_config_get_section
        
        # Create an ExternalLinkValidator instance
        self.validator = ExternalLinkValidator(self.mock_config)
        
        # Sample content dict
        self.sample_content = {
            "links": [
                "https://example.com/valid",
                "https://example.com/invalid",
                "https://api.example.com/docs",
                "https://example.com/api/v1",
                "#section"
            ]
        }
    
    def _mock_config_get(self, section, key, default=None):
        """Mock implementation for ConfigManager.get method."""
        config = {
            "site": {
                "base_url": "https://modelcontextprotocol.io",
                "name": "Model Context Protocol"
            },
            "validation": {
                "request_timeout": 5
            },
            "link_handling": {
                "internal_link_pattern": "^https?://modelcontextprotocol\\.io"
            }
        }
        
        if section in config and key in config[section]:
            return config[section][key]
        return default
    
    def _mock_config_get_section(self, section):
        """Mock implementation for ConfigManager.get_section method."""
        config = {
            "site": {
                "base_url": "https://modelcontextprotocol.io",
                "name": "Model Context Protocol"
            },
            "validation": {
                "request_timeout": 5
            },
            "link_handling": {
                "internal_link_pattern": "^https?://modelcontextprotocol\\.io"
            }
        }
        
        return config.get(section, {})
    
    def test_is_external_link(self):
        """Test external link detection."""
        # Test external links
        self.assertTrue(self.validator.is_external_link("https://example.com"))
        self.assertTrue(self.validator.is_external_link("https://api.example.com"))
        
        # Test internal links
        self.assertFalse(self.validator.is_external_link("https://modelcontextprotocol.io/docs"))
        self.assertFalse(self.validator.is_external_link("https://modelcontextprotocol.io/api"))
        
        # Test edge cases
        self.assertFalse(self.validator.is_external_link(""))
        self.assertFalse(self.validator.is_external_link("#section"))
    
    def test_is_api_link(self):
        """Test identifying API documentation links."""
        # Test API links
        self.assertTrue(self.validator.is_api_link("https://example.com/api/v1"))
        self.assertTrue(self.validator.is_api_link("https://api.example.com/docs"))
        
        # Test non-API links
        self.assertFalse(self.validator.is_api_link("https://example.com"))
        self.assertFalse(self.validator.is_api_link("https://example.com/docs"))
    
    @patch('requests.head')
    @patch('requests.get')
    def test_validate_link(self, mock_get, mock_head):
        """Test validating individual links."""
        # Test successful HEAD request
        mock_head.return_value.status_code = 200
        result = self.validator.validate_link("https://example.com/valid")
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["status_code"], 200)
        
        # Test failed HEAD request but successful GET request
        mock_head.return_value.status_code = 404
        mock_get.return_value.status_code = 200
        result = self.validator.validate_link("https://example.com/head-fails")
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["status_code"], 200)
        
        # Test failed request
        mock_head.return_value.status_code = 404
        mock_get.return_value.status_code = 404
        result = self.validator.validate_link("https://example.com/invalid")
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["status_code"], 404)
        
        # Test exception handling
        mock_head.side_effect = requests.exceptions.RequestException("Connection error")
        result = self.validator.validate_link("https://example.com/error")
        self.assertFalse(result["is_valid"])
        self.assertEqual(result["error"], "Connection error")
    
    @patch('requests.head')
    @patch('requests.get')
    def test_validate_links(self, mock_get, mock_head):
        """Test validating all links in content."""
        # Configure mock responses
        def mock_request(*args, **kwargs):
            url = args[0]
            response = MagicMock()
            
            if 'invalid' in url:
                response.status_code = 404
            elif 'api.example.com' in url or '/api/' in url:
                response.status_code = 200  # API links are valid
            elif 'valid' in url:
                response.status_code = 200
            else:
                response.status_code = 404
                
            return response
        
        mock_head.side_effect = mock_request
        mock_get.side_effect = mock_request
        
        # Validate links
        results = self.validator.validate_links(self.sample_content)
        
        # Check metrics
        self.assertEqual(results["total_links"], 5)
        self.assertEqual(results["valid_links"], 3)  # 1 regular external + 2 API links
        self.assertEqual(results["invalid_links_count"], 1)
        self.assertEqual(results["api_links_count"], 2)
        
        # Check external links (non-API)
        self.assertEqual(len(results["external_links"]), 1)
        self.assertEqual(results["external_links"][0]["url"], "https://example.com/valid")
        self.assertTrue(results["external_links"][0]["is_valid"])
        
        # Check invalid links
        self.assertEqual(len(results["invalid_links"]), 1)
        self.assertEqual(results["invalid_links"][0]["url"], "https://example.com/invalid")
        self.assertFalse(results["invalid_links"][0]["is_valid"])
        
        # Check API links
        self.assertEqual(len(results["api_links"]), 2)
        api_urls = [link["url"] for link in results["api_links"]]
        self.assertIn("https://api.example.com/docs", api_urls)
        self.assertIn("https://example.com/api/v1", api_urls)
        for api_link in results["api_links"]:
            self.assertTrue(api_link["is_valid"])
    
    def test_generate_report(self):
        """Test generating validation report."""
        # Add some test data
        self.validator.metrics["total_external_links"] = 10
        self.validator.metrics["valid_links"] = 8
        self.validator.metrics["invalid_links"] = 2
        self.validator.metrics["api_links"] = 3
        
        self.validator.validation_results = [
            {
                "source_url": "https://example.com/page1",
                "external_links": [{"text": "Link 1", "url": "https://valid1.com"}],
                "api_links": [{"text": "API 1", "url": "https://api1.com"}],
                "invalid_links": [{"text": "Invalid 1", "url": "https://invalid1.com", "error": "404"}]
            }
        ]
        
        # Generate report
        report = self.validator.generate_report()
        
        # Check report structure
        self.assertIn("metrics", report)
        self.assertIn("results", report)
        
        # Check metrics
        self.assertEqual(report["metrics"]["total_external_links"], 10)
        self.assertEqual(report["metrics"]["valid_links"], 8)
        self.assertEqual(report["metrics"]["invalid_links"], 2)
        self.assertEqual(report["metrics"]["api_links"], 3)
        
        # Check results
        self.assertEqual(len(report["results"]), 1)
        self.assertEqual(len(report["results"][0]["external_links"]), 1)
        self.assertEqual(len(report["results"][0]["api_links"]), 1)
        self.assertEqual(len(report["results"][0]["invalid_links"]), 1)


if __name__ == "__main__":
    unittest.main() 