"""
Markdown converter implementation.

This module provides the MarkdownConverter class for converting HTML content to Markdown.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

import html2text
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class MarkdownConverter:
    """
    Converts HTML content to Markdown.

    This class is responsible for converting HTML content to well-formatted Markdown,
    preserving the structure, code blocks, tables, and other important elements.
    """

    def __init__(self, config_manager):
        """
        Initialize the MarkdownConverter.

        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.conversion_config = self.config_manager.get_conversion_config()
        logger.debug(
            f"Initialized MarkdownConverter with config: {self.conversion_config}"
        )

        # Configure html2text
        self.h2t = html2text.HTML2Text()
        self.h2t.body_width = 0  # Don't wrap text
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.escape_snob = False
        self.h2t.wrap_links = False
        self.h2t.inline_links = True
        self.h2t.protect_links = True
        self.h2t.unicode_snob = True
        self.h2t.tables = True
        self.h2t.single_line_break = True

        # Configure any custom settings from the config
        for key, value in self.conversion_config.get("html2text_options", {}).items():
            if hasattr(self.h2t, key):
                setattr(self.h2t, key, value)

    def convert(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert HTML content to Markdown.

        Args:
            content_data: Dictionary containing extracted content
                {
                    'title': The page title,
                    'content': The extracted HTML content,
                    'url': The original URL,
                    'metadata': Additional metadata
                }

        Returns:
            Dictionary with the same structure but with content converted to Markdown
        """
        logger.info(f"Converting content from {content_data['url']} to Markdown")

        try:
            # Extract content from the dictionary
            html_content = content_data["content"]
            url = content_data["url"]

            # Pre-process HTML for better markdown conversion
            processed_html = self._preprocess_html(html_content)

            # Convert to Markdown
            markdown_content = self._convert_to_markdown(processed_html)

            # Post-process Markdown for final formatting
            final_markdown = self._postprocess_markdown(markdown_content, url)

            # Create title
            title_markdown = f"# {content_data['title']}\n\n"

            # Create metadata section if configured to include it
            metadata_markdown = ""
            if self.conversion_config.get("include_metadata", True):
                metadata_markdown = self._format_metadata(content_data["metadata"])

            # Create the complete markdown document
            complete_markdown = title_markdown + metadata_markdown + final_markdown

            # Update the content data dictionary
            result = content_data.copy()
            result["content"] = complete_markdown
            result["format"] = "markdown"

            logger.debug(f"Successfully converted content from {url} to Markdown")
            return result

        except Exception as e:
            logger.error(f"Error converting content to Markdown: {e}")
            # Return the original content with an error note
            result = content_data.copy()
            result["content"] = (
                f"# {content_data['title']}\n\n> **Error:** Failed to convert HTML to Markdown\n\n"
            )
            result["format"] = "markdown"
            result["error"] = str(e)
            return result

    def _preprocess_html(self, html_content: str) -> str:
        """
        Preprocess HTML before conversion to Markdown.

        Args:
            html_content: The HTML content to preprocess

        Returns:
            Preprocessed HTML content
        """
        soup = BeautifulSoup(html_content, "html.parser")

        # Handle code blocks - they require special attention
        self._preprocess_code_blocks(soup)

        # Handle tables - ensure they have proper structure
        self._preprocess_tables(soup)

        # Handle images - ensure they have alt text
        self._preprocess_images(soup)

        # Special handling for blockquotes or other elements
        self._preprocess_blockquotes(soup)

        return str(soup)

    def _preprocess_code_blocks(self, soup: BeautifulSoup) -> None:
        """
        Prepare code blocks for Markdown conversion.

        Args:
            soup: The BeautifulSoup object
        """
        for pre in soup.find_all("pre"):
            # Check if there's a language specified
            code_tag = pre.find("code")
            language = None

            if pre.get("data-language"):
                language = pre.get("data-language")
            elif code_tag and code_tag.get("class"):
                for cls in code_tag.get("class", []):
                    if cls.startswith("language-"):
                        language = cls.replace("language-", "")
                        break

            # Convert to format suitable for html2text
            if language:
                pre["data-language-marker"] = f"```{language}"
            else:
                pre["data-language-marker"] = "```"

            # Add a special class that html2text can detect
            pre["class"] = pre.get("class", []) + ["html2text-pre"]

    def _preprocess_tables(self, soup: BeautifulSoup) -> None:
        """
        Prepare tables for Markdown conversion.

        Args:
            soup: The BeautifulSoup object
        """
        for table in soup.find_all("table"):
            # Ensure tables have thead and tbody for proper markdown conversion
            if not table.find("thead") and table.find("tr"):
                first_row = table.find("tr")
                if first_row and first_row.find("th"):
                    # Create thead and move the first row into it
                    thead = soup.new_tag("thead")
                    thead.append(first_row.extract())
                    table.insert(0, thead)

    def _preprocess_images(self, soup: BeautifulSoup) -> None:
        """
        Prepare images for Markdown conversion.

        Args:
            soup: The BeautifulSoup object
        """
        for img in soup.find_all("img"):
            # Ensure images have alt text
            if not img.get("alt"):
                img["alt"] = img.get("title", "Image")

    def _preprocess_blockquotes(self, soup: BeautifulSoup) -> None:
        """
        Prepare blockquotes for Markdown conversion.

        Args:
            soup: The BeautifulSoup object
        """
        # Ensure blockquotes are properly formatted
        for blockquote in soup.find_all("blockquote"):
            # Make sure each line in the blockquote is preceded by '>' in Markdown
            # This ensures proper conversion
            for p in blockquote.find_all("p"):
                p["class"] = p.get("class", []) + ["blockquote-p"]

    def _convert_to_markdown(self, html_content: str) -> str:
        """
        Convert HTML to Markdown using html2text.

        Args:
            html_content: The preprocessed HTML content

        Returns:
            Markdown content
        """
        # Use html2text to convert
        markdown = self.h2t.handle(html_content)

        return markdown

    def _postprocess_markdown(self, markdown_content: str, url: str) -> str:
        """
        Postprocess Markdown after conversion.

        Args:
            markdown_content: The converted Markdown content
            url: The original URL

        Returns:
            Postprocessed Markdown content
        """
        # Fix code blocks - ensure they have proper spacing
        markdown_content = self._fix_code_blocks(markdown_content)

        # Fix tables - ensure they have proper formatting
        markdown_content = self._fix_tables(markdown_content)

        # Fix links - ensure external links have proper formatting
        markdown_content = self._fix_links(markdown_content, url)

        # Fix headings - ensure they have proper spacing
        markdown_content = self._fix_headings(markdown_content)

        # Fix lists - ensure they have proper spacing
        markdown_content = self._fix_lists(markdown_content)

        return markdown_content

    def _fix_code_blocks(self, markdown_content: str) -> str:
        """
        Fix code blocks in Markdown.

        Args:
            markdown_content: The Markdown content

        Returns:
            Fixed Markdown content
        """
        # Ensure code blocks have proper spacing
        markdown_content = re.sub(r"```(\w*)\n", r"```\1\n", markdown_content)
        markdown_content = re.sub(r"\n```", r"\n\n```", markdown_content)

        return markdown_content

    def _fix_tables(self, markdown_content: str) -> str:
        """
        Fix tables in Markdown.

        Args:
            markdown_content: The Markdown content

        Returns:
            Fixed Markdown content
        """
        # Ensure tables have proper spacing before and after
        table_pattern = r"(\n\|[^\n]+\|[^\n]*\n\|[-:| ]+\|[^\n]*\n)"
        markdown_content = re.sub(table_pattern, r"\n\1", markdown_content)

        # Find the end of tables and add a newline
        markdown_content = re.sub(
            r"(\n\|[^\n]+\|[^\n]*\n)(?!\|)", r"\1\n", markdown_content
        )

        return markdown_content

    def _fix_links(self, markdown_content: str, base_url: str) -> str:
        """
        Fix links in Markdown.

        Args:
            markdown_content: The Markdown content
            base_url: The base URL for resolving relative links

        Returns:
            Fixed Markdown content
        """
        # External links should have proper protocol
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        def fix_link(match):
            text = match.group(1)
            link = match.group(2)

            # Check if the link is relative and make it absolute
            if not link.startswith(("http://", "https://", "mailto:", "#")):
                link = urljoin(base_url, link)

            return f"[{text}]({link})"

        return re.sub(link_pattern, fix_link, markdown_content)

    def _fix_headings(self, markdown_content: str) -> str:
        """
        Fix headings in Markdown.

        Args:
            markdown_content: The Markdown content

        Returns:
            Fixed Markdown content
        """
        # Ensure headings have proper spacing before and after
        for i in range(6, 0, -1):  # Start with h6 to avoid double processing
            heading_pattern = f"([^\n])\\n(#{{{i}}} )"
            markdown_content = re.sub(heading_pattern, f"\\1\n\n\\2", markdown_content)

            after_pattern = f"(#{{{i}}} [^\n]+)\\n([^\n#])"
            markdown_content = re.sub(after_pattern, f"\\1\n\n\\2", markdown_content)

        return markdown_content

    def _fix_lists(self, markdown_content: str) -> str:
        """
        Fix lists in Markdown.

        Args:
            markdown_content: The Markdown content

        Returns:
            Fixed Markdown content
        """
        # Ensure lists have proper spacing before and after
        markdown_content = re.sub(
            r"([^\n])\n(- |\d+\. )", r"\1\n\n\2", markdown_content
        )

        # Find the end of lists and add a newline
        markdown_content = re.sub(
            r"(- |\d+\. )([^\n]+)\n(?!- |\d+\. )", r"\1\2\n\n", markdown_content
        )

        return markdown_content

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """
        Format metadata as Markdown.

        Args:
            metadata: The metadata dictionary

        Returns:
            Markdown string with formatted metadata
        """
        if not metadata:
            return ""

        lines = ["<!-- Metadata"]

        for key, value in metadata.items():
            if value:
                lines.append(f"{key}: {value}")

        lines.append("-->\n\n")

        return "\n".join(lines)
