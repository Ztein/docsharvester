"""
Web Crawler Module for MCP Documentation Scraper

This module provides functionality to crawl documentation websites,
respecting robots.txt and other constraints.
"""

import logging
import re
import time
from collections import deque
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import fnmatch

from mcp_doc_getter.src.config_manager.config_manager import ConfigManager


class WebCrawler:
    """
    A web crawler for documentation sites.
    
    Provides functionality to systematically traverse a website,
    respecting robots.txt directives and other constraints.
    """
    
    def __init__(self, config: ConfigManager) -> None:
        """
        Initialize the web crawler.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.base_url = config.get('site', 'base_url')
        self.rate_limit = config.get('crawling', 'rate_limit', 1)  # requests per second
        self.max_depth = config.get('crawling', 'max_depth', 5)
        self.max_retries = config.get('error_handling', 'max_retries', 3)
        self.retry_delay = config.get('error_handling', 'retry_delay', 2)
        
        # Get include and exclude patterns
        crawling_config = config.get_section('crawling')
        self.include_patterns = crawling_config.get('include_patterns', [])
        self.exclude_patterns = crawling_config.get('exclude_patterns', [])
        
        # Set up internal state
        self.visited_urls: Set[str] = set()
        self.robots_rules: Dict[str, List[str]] = {'allow': [], 'disallow': []}
        self.last_request_time = 0
        
        logging.info(f"Initialized WebCrawler for {self.base_url}")
    
    def initialize(self) -> None:
        """
        Initialize the crawler by fetching robots.txt.
        """
        self._fetch_robots_txt()
        logging.info("WebCrawler initialized")
    
    def _fetch_robots_txt(self) -> None:
        """
        Fetch and parse robots.txt from the website.
        """
        robots_url = urljoin(self.base_url, "/robots.txt")
        try:
            response = self.fetch_url(robots_url)
            if response.status_code == 200:
                self._parse_robots_txt(response.text)
            else:
                logging.warning(f"Failed to fetch robots.txt: {response.status_code}")
        except Exception as e:
            logging.error(f"Error fetching robots.txt: {e}")
    
    def _parse_robots_txt(self, text: str) -> None:
        """
        Parse robots.txt content.
        
        Args:
            text: The content of robots.txt
        """
        current_agent = None
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.lower().startswith('user-agent:'):
                agent = line.split(':', 1)[1].strip()
                if agent == '*' or agent.lower() == 'python-requests':
                    current_agent = agent
                else:
                    current_agent = None
            elif current_agent and line.lower().startswith('allow:'):
                path = line.split(':', 1)[1].strip()
                self.robots_rules['allow'].append(path)
            elif current_agent and line.lower().startswith('disallow:'):
                path = line.split(':', 1)[1].strip()
                self.robots_rules['disallow'].append(path)
        
        logging.info(f"Parsed robots.txt: {len(self.robots_rules['allow'])} allow rules, "
                     f"{len(self.robots_rules['disallow'])} disallow rules")
    
    def is_url_allowed(self, url: str) -> bool:
        """
        Check if a URL is allowed according to robots.txt.
        
        Args:
            url: The URL to check
        
        Returns:
            True if the URL is allowed, False otherwise
        """
        parsed = urlparse(url)
        path = parsed.path
        
        # Check disallow rules
        for rule in self.robots_rules['disallow']:
            if path.startswith(rule):
                return False
        
        # Check allow rules
        for rule in self.robots_rules['allow']:
            if path.startswith(rule):
                return True
        
        # By default, allow if there's no matching rule
        return True
    
    def should_crawl_url(self, url: str) -> bool:
        """
        Check if a URL should be crawled based on include/exclude patterns.
        
        Args:
            url: The URL to check
        
        Returns:
            True if the URL should be crawled, False otherwise
        """
        parsed = urlparse(url)
        path = parsed.path
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path, pattern):
                logging.debug(f"URL excluded by pattern: {url} (matched {pattern})")
                return False
        
        # Check include patterns
        if not self.include_patterns:
            # If no include patterns, crawl everything that's not excluded
            return True
        
        for pattern in self.include_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        
        logging.debug(f"URL not matched by any include pattern: {url}")
        return False
    
    def fetch_url(self, url: str, timeout: int = 10) -> requests.Response:
        """
        Fetch a URL with rate limiting and retries.
        
        Args:
            url: The URL to fetch
            timeout: Timeout in seconds
        
        Returns:
            The response object
        
        Raises:
            requests.RequestException: If the request fails after max retries
        """
        # Apply rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0 / self.rate_limit:
            sleep_time = (1.0 / self.rate_limit) - elapsed
            logging.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        # Fetch with retries
        retries = 0
        while retries <= self.max_retries:
            try:
                logging.debug(f"Fetching URL: {url}")
                response = requests.get(url, timeout=timeout)
                self.last_request_time = time.time()
                
                if 200 <= response.status_code < 300 or response.status_code == 404:
                    return response
                
                if retries == self.max_retries:
                    logging.warning(f"Failed to fetch {url}: status {response.status_code}")
                    return response
                
                logging.warning(f"Attempt {retries+1}/{self.max_retries+1} failed: {response.status_code}")
                retries += 1
                time.sleep(self.retry_delay)
            
            except requests.RequestException as e:
                if retries == self.max_retries:
                    logging.error(f"Failed to fetch {url} after {retries+1} attempts: {e}")
                    raise
                
                logging.warning(f"Attempt {retries+1}/{self.max_retries+1} failed: {e}")
                retries += 1
                time.sleep(self.retry_delay)
        
        # This should not be reached, but return a dummy response to satisfy type checking
        return requests.Response()
    
    def extract_links(self, html_content: str, source_url: str) -> List[str]:
        """
        Extract links from HTML content.
        
        Args:
            html_content: HTML content
            source_url: The URL of the page containing the links
        
        Returns:
            List of absolute URLs
        """
        links = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for anchor in soup.find_all('a'):
                href = anchor.get('href')
                if href:
                    # Convert to absolute URL
                    absolute_url = urljoin(source_url, href)
                    links.append(absolute_url)
        except Exception as e:
            logging.error(f"Error extracting links from {source_url}: {e}")
        
        return links
    
    def crawl(self, start_url: str) -> List[str]:
        """
        Crawl a website starting from a given URL.
        
        Args:
            start_url: The URL to start crawling from
        
        Returns:
            List of discovered URLs
        """
        # Initialize the crawler if not already initialized
        if not self.robots_rules['allow'] and not self.robots_rules['disallow']:
            self.initialize()
        
        to_visit = deque([(start_url, 0)])  # (url, depth)
        self.visited_urls = set()
        discovered_urls = []
        
        while to_visit:
            url, depth = to_visit.popleft()
            
            # Skip if already visited or too deep
            if url in self.visited_urls or depth > self.max_depth:
                continue
            
            # Mark as visited
            self.visited_urls.add(url)
            
            # Check if allowed by robots.txt
            if not self.is_url_allowed(url):
                logging.info(f"Skipping URL not allowed by robots.txt: {url}")
                continue
            
            # Check if should be crawled based on patterns
            if not self.should_crawl_url(url):
                logging.debug(f"Skipping URL not matching include/exclude patterns: {url}")
                continue
            
            # Fetch the URL
            try:
                response = self.fetch_url(url)
                if response.status_code != 200:
                    logging.warning(f"Failed to fetch {url}: status {response.status_code}")
                    continue
                
                # Add to discovered URLs
                discovered_urls.append(url)
                
                # Extract links and add to queue
                if depth < self.max_depth:
                    links = self.extract_links(response.text, url)
                    for link in links:
                        # Only crawl URLs from the same domain
                        if urlparse(link).netloc == urlparse(self.base_url).netloc:
                            to_visit.append((link, depth + 1))
            
            except Exception as e:
                logging.error(f"Error crawling {url}: {e}")
        
        logging.info(f"Crawling completed. Discovered {len(discovered_urls)} URLs")
        return discovered_urls 