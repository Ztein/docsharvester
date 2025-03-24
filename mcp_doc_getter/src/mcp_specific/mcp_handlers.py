"""
MCP-specific content handlers and utilities.

This module provides specialized handlers for ModelContextProtocol.io documentation content.
"""

from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup, Tag
import logging

logger = logging.getLogger(__name__)


class MCPContentHandler:
    """
    Handler for ModelContextProtocol.io specific content processing.
    
    This class provides methods for handling MCP-specific content structures, elements,
    and formatting to ensure high-quality extraction and conversion.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the MCPContentHandler.
        
        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.extraction_config = config_manager.get_section('extraction')
    
    def preprocess_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Preprocess the HTML for MCP-specific content.
        
        Args:
            soup: The BeautifulSoup object
            
        Returns:
            The preprocessed BeautifulSoup object
        """
        # MCP specific preprocessing steps
        self._handle_header_navigation(soup)
        self._clean_sidebar(soup)
        self._handle_dark_theme_elements(soup)
        
        return soup
    
    def _handle_header_navigation(self, soup: BeautifulSoup) -> None:
        """
        Handle the header and navigation elements in MCP documentation.
        
        Args:
            soup: The BeautifulSoup object
        """
        # Remove navigation elements that should not be included in documentation
        nav_elements = soup.select('header nav, .mobile-nav, .nav-wrapper')
        for nav in nav_elements:
            nav.decompose()
    
    def _clean_sidebar(self, soup: BeautifulSoup) -> None:
        """
        Clean up sidebar elements in MCP documentation.
        
        Args:
            soup: The BeautifulSoup object
        """
        # Remove sidebar elements
        sidebar_elements = soup.select('.sidebar, .doc-sidebar, aside')
        for sidebar in sidebar_elements:
            sidebar.decompose()
    
    def _handle_dark_theme_elements(self, soup: BeautifulSoup) -> None:
        """
        Handle dark theme elements in MCP documentation.
        
        Args:
            soup: The BeautifulSoup object
        """
        # Remove theme switchers and other UI elements
        theme_elements = soup.select('.theme-switch, .color-mode-toggle')
        for element in theme_elements:
            element.decompose()
    
    def process_code_blocks(self, content: Tag) -> None:
        """
        Process MCP-specific code blocks.
        
        Args:
            content: The content element
        """
        # Find all code blocks and apply MCP-specific processing
        for pre in content.find_all('pre'):
            # Add specific classes for MCP code blocks
            pre['class'] = pre.get('class', []) + ['mcp-code-block']
            
            # Handle language tabs if present
            language_tabs = pre.find_previous_sibling('.language-tabs')
            if language_tabs:
                # Extract the selected language
                selected_tab = language_tabs.select_one('.active')
                if selected_tab:
                    language = selected_tab.get_text(strip=True).lower()
                    pre['data-language'] = language
            
            # Otherwise, try to detect language from class
            elif not pre.get('data-language'):
                code_tag = pre.find('code')
                if code_tag and code_tag.get('class'):
                    for cls in code_tag.get('class', []):
                        if cls.startswith('language-'):
                            pre['data-language'] = cls.replace('language-', '')
                            break
    
    def process_tables(self, content: Tag) -> None:
        """
        Process MCP-specific tables.
        
        Args:
            content: The content element
        """
        # Find all tables and apply MCP-specific processing
        for table in content.find_all('table'):
            # Add specific classes for MCP tables
            table['class'] = table.get('class', []) + ['mcp-table']
            
            # Handle responsive tables with wrappers
            parent = table.parent
            if parent and 'table-wrapper' in parent.get('class', []):
                parent['class'] = parent.get('class', []) + ['mcp-table-wrapper']
    
    def process_links(self, content: Tag, base_url: str) -> None:
        """
        Process MCP-specific links.
        
        Args:
            content: The content element
            base_url: The base URL of the website
        """
        # Process internal documentation links
        for link in content.find_all('a'):
            href = link.get('href', '')
            
            # Handle MCP-specific link formats
            if href.startswith('/docs/'):
                # Mark as internal documentation link
                link['data-internal'] = 'true'
                
            # Handle API references
            elif '/api/' in href:
                # Mark as API reference link
                link['data-api-ref'] = 'true'
    
    def postprocess_markdown(self, markdown_content: str) -> str:
        """
        Postprocess the Markdown content for MCP-specific elements.
        
        Args:
            markdown_content: The Markdown content
            
        Returns:
            The postprocessed Markdown content
        """
        # Add MCP-specific formatting or fixes to the markdown content
        
        # Fix code block language specifiers
        lines = markdown_content.splitlines()
        in_code_block = False
        
        for i, line in enumerate(lines):
            if line.startswith('```') and not in_code_block:
                in_code_block = True
                # If there's no language specified, add 'python' as default for MCP
                if line == '```':
                    lines[i] = '```python'
            elif line.startswith('```') and in_code_block:
                in_code_block = False
        
        return '\n'.join(lines) 