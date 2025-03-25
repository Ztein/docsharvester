"""
MCP-specific content extractor.

This module provides a specialized content extractor for ModelContextProtocol.io documentation.
"""

import logging
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup

from mcp_doc_getter.src.content_extractor import ContentExtractor
from .mcp_handlers import MCPContentHandler

logger = logging.getLogger(__name__)


class MCPContentExtractor(ContentExtractor):
    """
    Specialized content extractor for ModelContextProtocol.io documentation.
    
    This class extends the base ContentExtractor with MCP-specific functionality.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the MCPContentExtractor.
        
        Args:
            config_manager: The configuration manager instance
        """
        super().__init__(config_manager)
        self.mcp_handler = MCPContentHandler(config_manager)
        logger.debug("Initialized MCPContentExtractor")
    
    def extract(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Extract content from MCP HTML.
        
        This method overrides the base extract method to add MCP-specific processing.
        
        Args:
            html_content: The HTML content to extract from
            url: The URL of the page
        
        Returns:
            A dictionary containing the extracted content
        """
        logger.info(f"Extracting MCP-specific content from {url}")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Apply MCP-specific preprocessing
            soup = self.mcp_handler.preprocess_html(soup)
            
            title = self._extract_title(soup)
            content = self._extract_main_content(soup)
            metadata = self._extract_metadata(soup, url)
            
            # Add MCP-specific metadata
            metadata.update(self._extract_mcp_metadata(soup, url))
            
            result = {
                'url': url,
                'title': title,
                'content': content,
                'metadata': metadata
            }
            
            logger.debug(f"Extracted MCP content from {url} with title: {result['title']}")
            return result
            
        except Exception as e:
            logger.error(f"Error extracting MCP content from {url}: {e}")
            # Return a minimal result with error information
            return {
                'url': url,
                'title': self._fallback_title(soup) if 'soup' in locals() else "Unknown Title",
                'content': "<p>Error extracting content</p>",
                'metadata': {
                    'error': str(e)
                }
            }
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract the main content from MCP HTML with specialized handling.
        
        Args:
            soup: The BeautifulSoup object
        
        Returns:
            The extracted HTML content as a string
        """
        # Use MCP-specific selector if available, otherwise fall back to base behavior
        content_selector = self.extraction_config.get('mcp_content_selector', 
                                                      self.extraction_config.get('content_selector'))
        
        content_element = soup.select_one(content_selector)
        
        if not content_element:
            logger.warning(f"Could not find content using selector '{content_selector}', falling back to default")
            # Try common MCP content selectors
            for selector in ['.doc-content', 'main .content', 'article.content', '#documentation']:
                content_element = soup.select_one(selector)
                if content_element:
                    break
        
        if not content_element:
            logger.warning("All MCP-specific selectors failed, falling back to body")
            content_element = soup.body or soup
        
        # Create a copy of the content by parsing it again
        content_html = str(content_element)
        content = BeautifulSoup(content_html, 'html.parser')
        
        # Extract the main element from the new soup
        if content.body:
            content = content.body.contents[0]
            
        # Filter out elements that should be ignored
        filtered_content = self._filter_elements(content)
        
        # Apply MCP-specific processing
        self.mcp_handler.process_code_blocks(filtered_content)
        self.mcp_handler.process_tables(filtered_content)
        self.mcp_handler.process_links(filtered_content, self.config_manager.get('site', 'base_url'))
        
        return str(filtered_content)
    
    def _extract_mcp_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """
        Extract MCP-specific metadata from the HTML.
        
        Args:
            soup: The BeautifulSoup object
            url: The URL of the page
        
        Returns:
            A dictionary containing MCP-specific metadata
        """
        mcp_metadata = {
            'mcp_version': self._get_mcp_version(soup),
            'mcp_section': self._get_mcp_section(url),
        }
        
        return mcp_metadata
    
    def _get_mcp_version(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Get the MCP version information from the page.
        
        Args:
            soup: The BeautifulSoup object
        
        Returns:
            The MCP version or None if not found
        """
        # Try to find version information in various locations
        version_element = soup.select_one('.version-info, .doc-version, .version')
        if version_element:
            return version_element.get_text(strip=True)
        
        return None
    
    def _get_mcp_section(self, url: str) -> str:
        """
        Determine the MCP documentation section from the URL.
        
        Args:
            url: The URL of the page
        
        Returns:
            The MCP section name
        """
        # Extract section from URL path
        from urllib.parse import urlparse
        
        path = urlparse(url).path
        
        if '/docs/' in path:
            # Get the first segment after /docs/
            segments = path.strip('/').split('/')
            if len(segments) > 1 and segments[0] == 'docs':
                return segments[1]
        
        return "general" 