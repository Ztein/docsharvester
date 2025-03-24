"""
Content extractor implementation.

This module provides the ContentExtractor class for extracting content from HTML pages.
"""

import logging
import sys
import traceback
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class ContentExtractor:
    """
    Extracts content from HTML pages.
    
    This class is responsible for extracting meaningful content from HTML pages
    while preserving the structure. It uses BeautifulSoup for HTML parsing and
    follows the configuration provided by the configuration manager.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the ContentExtractor.
        
        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.extraction_config = self.config_manager.get_extraction_config()
        logger.debug(f"Initialized ContentExtractor with config: {self.extraction_config}")
    
    def extract(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extract content from HTML.
        
        Args:
            html_content: The HTML content to extract from
            url: The URL of the page
        
        Returns:
            A dictionary containing the extracted content:
            {
                'title': The page title,
                'content': The extracted HTML content,
                'url': The original URL
            }
        """
        logger.info(f"Extracting content from {url}")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            title = self._extract_title(soup)
            content = self._extract_main_content(soup)
            metadata = self._extract_metadata(soup, url)
            
            result = {
                'url': url,
                'title': title,
                'content': content,
                'metadata': metadata
            }
            
            logger.debug(f"Extracted content from {url} with title: {result['title']}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            # Return a minimal result with error information
            return {
                'url': url,
                'title': self._fallback_title(soup) if 'soup' in locals() else "Unknown Title",
                'content': "<p>Error extracting content</p>",
                'metadata': {
                    'error': str(e)
                }
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        Extract the title from the HTML.
        
        Args:
            soup: The BeautifulSoup object
        
        Returns:
            The page title
        """
        title_selector = self.extraction_config.get('title_selector', 'h1.title')
        title_element = soup.select_one(title_selector)
        
        if title_element:
            return title_element.get_text(strip=True)
        
        # Fallback to document title
        return self._fallback_title(soup)
    
    def _fallback_title(self, soup: BeautifulSoup) -> str:
        """
        Get a fallback title if the main title selector fails.
        
        Args:
            soup: The BeautifulSoup object
        
        Returns:
            The fallback title
        """
        if soup.title:
            return soup.title.get_text(strip=True)
        
        # Fallback to the first h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)
        
        # Last resort fallback
        return "Untitled Page"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from the HTML.
        
        Args:
            soup: The BeautifulSoup object
        
        Returns:
            The extracted HTML content as a string
        """
        content_selector = self.extraction_config.get('content_selector', 'main.content, article, .content, #content, .main')
        content_element = soup.select_one(content_selector)
        
        if not content_element:
            logger.warning(f"Could not find content using selector '{content_selector}', falling back to body")
            content_element = soup.body or soup
        
        # Create a copy of the content by parsing it again
        content_html = str(content_element)
        content = BeautifulSoup(content_html, 'html.parser')
        
        # Extract the main element from the new soup
        if content.body:
            content = content.body.contents[0]
            
        # Filter out elements that should be ignored
        filtered_content = self._filter_elements(content)
        
        # Handle special elements
        self._handle_code_blocks(filtered_content)
        self._handle_tables(filtered_content)
        
        return str(filtered_content)
    
    def _filter_elements(self, content: Tag) -> Tag:
        """
        Filter out elements that should be ignored.
        
        Args:
            content: The content element
        
        Returns:
            The filtered content
        """
        ignore_selectors = self.extraction_config.get('ignore_selectors', [])
        
        for selector in ignore_selectors:
            for element in content.select(selector):
                element.decompose()
        
        return content
    
    def _handle_code_blocks(self, content: Tag) -> None:
        """
        Process code blocks to ensure they are properly formatted.
        
        Args:
            content: The content element
        """
        # Find all code blocks
        for pre in content.find_all('pre'):
            # Add a class for the markdown converter to recognize
            pre['class'] = pre.get('class', []) + ['code-block']
            
            # If there's a language hint in a class, preserve it
            code_tag = pre.find('code')
            if code_tag and code_tag.get('class'):
                for cls in code_tag.get('class', []):
                    if cls.startswith('language-'):
                        pre['data-language'] = cls.replace('language-', '')
                        break
    
    def _handle_tables(self, content: Tag) -> None:
        """
        Process tables to ensure they are properly formatted.
        
        Args:
            content: The content element
        """
        # Find all tables
        for table in content.find_all('table'):
            # Add a class for the markdown converter to recognize
            table['class'] = table.get('class', []) + ['table']
            
            # Ensure all tables have thead and tbody
            if not table.find('thead') and table.find('tr'):
                first_row = table.find('tr')
                if first_row and first_row.find('th'):
                    # Create thead and move the first row into it
                    new_soup = BeautifulSoup("<thead></thead>", "html.parser")
                    thead = new_soup.thead
                    thead.append(first_row.extract())
                    table.insert(0, thead)
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Extract metadata from the HTML.
        
        Args:
            soup: The BeautifulSoup object
            url: The URL of the page
        
        Returns:
            A dictionary containing metadata
        """
        metadata = {
            'path': urlparse(url).path,
            'description': self._get_meta_content(soup, 'description'),
            'keywords': self._get_meta_content(soup, 'keywords'),
        }
        
        return metadata
    
    def _get_meta_content(self, soup: BeautifulSoup, name: str) -> Optional[str]:
        """
        Get content from a meta tag.
        
        Args:
            soup: The BeautifulSoup object
            name: The name of the meta tag
        
        Returns:
            The content of the meta tag, or None if not found
        """
        meta = soup.find('meta', attrs={'name': name})
        if meta:
            return meta.get('content')
        
        return None 