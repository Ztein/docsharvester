"""
External link validator implementation.

This module provides functionality for validating external links in documentation.
"""

import logging
import re
from typing import Dict, List, Set, Tuple
from urllib.parse import urlparse
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class ExternalLinkValidator:
    """
    Validates external links in documentation.
    
    This class is responsible for:
    - Identifying external links
    - Validating external link accessibility
    - Collecting validation metrics
    - Generating validation reports
    """
    
    def __init__(self, config_manager):
        """
        Initialize the ExternalLinkValidator.
        
        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.site_config = self.config_manager.get_section("site")
        self.validation_config = self.config_manager.get_section("validation")
        
        # Regular expression pattern for internal links
        self.internal_link_pattern = self.config_manager.get(
            "link_handling",
            "internal_link_pattern",
            f"^https?://{urlparse(self.site_config['base_url']).netloc}"
        )
        
        # Initialize metrics
        self.metrics = {
            "total_external_links": 0,
            "valid_links": 0,
            "invalid_links": 0,
            "unreachable_links": 0,
            "api_links": 0
        }
        
        # Track processed links to avoid rechecking
        self.processed_links: Set[str] = set()
        
        # Track validation results
        self.validation_results: List[Dict] = []
        
        # Request timeout in seconds
        self.timeout = self.validation_config.get("request_timeout", 10)
        
        logger.debug("Initialized ExternalLinkValidator")
    
    def is_external_link(self, url: str) -> bool:
        """
        Check if a URL is an external link.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL is external, False otherwise
        """
        # Skip empty URLs and anchor links
        if not url or url.startswith('#'):
            return False
            
        # Parse the URL
        try:
            parsed = urlparse(url)
            # Skip URLs without a netloc (relative paths, anchors, etc.)
            if not parsed.netloc:
                return False
            # Check if it matches the internal pattern
            return not bool(re.match(self.internal_link_pattern, url))
        except Exception:
            return False
    
    def is_api_link(self, url: str) -> bool:
        """
        Check if a URL is an API documentation link.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL is an API link, False otherwise
        """
        try:
            parsed = urlparse(url)
            # Check for /api/ in path or api. in hostname
            return '/api/' in parsed.path or parsed.netloc.startswith('api.')
        except Exception:
            return False
    
    def validate_link(self, url: str) -> Dict:
        """
        Validate a single link.
        
        Args:
            url: The URL to validate
            
        Returns:
            Dictionary containing validation result
        """
        try:
            # Try HEAD request first
            response = requests.head(url, timeout=self.timeout)
            
            # If HEAD fails, try GET request
            if response.status_code >= 400:
                response = requests.get(url, timeout=self.timeout)
                
            return {
                "url": url,
                "is_valid": response.status_code < 400,
                "status_code": response.status_code
            }
            
        except Exception as e:
            return {
                "url": url,
                "is_valid": False,
                "error": str(e)
            }
    
    def validate_links(self, content):
        """Validate all links in the content and return results."""
        links = content.get("links", [])
        results = {
            "external_links": [],
            "invalid_links": [],
            "api_links": [],
            "total_links": len(links),
            "valid_links": 0,
            "invalid_links_count": 0,
            "api_links_count": 0
        }

        for link in links:
            if not link or link.startswith("#"):
                continue

            validation_result = self.validate_link(link)
            
            if self.is_api_link(link):
                results["api_links"].append(validation_result)
                results["api_links_count"] += 1
                if validation_result["is_valid"]:
                    results["valid_links"] += 1
                else:
                    results["invalid_links_count"] += 1
            elif self.is_external_link(link):
                if validation_result["is_valid"]:
                    results["external_links"].append(validation_result)
                    results["valid_links"] += 1
                else:
                    results["invalid_links"].append(validation_result)
                    results["invalid_links_count"] += 1

        return results
    
    def generate_report(self) -> Dict:
        """
        Generate a validation report.
        
        Returns:
            Dictionary containing validation metrics and results
        """
        return {
            "metrics": self.metrics,
            "results": self.validation_results
        } 