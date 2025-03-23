"""
Link handler implementation.

This module provides the LinkHandler class for processing links in Markdown content.
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)


class LinkHandler:
    """
    Processes links in Markdown content.

    This class is responsible for handling links in Markdown content,
    including converting internal links to relative paths, managing anchor links,
    and ensuring images have the correct paths.
    """

    def __init__(self, config_manager):
        """
        Initialize the LinkHandler.

        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.link_config = self.config_manager.get_section("link_handling")
        self.output_config = self.config_manager.get_section("output")
        self.site_config = self.config_manager.get_section("site")

        # Regular expression pattern for internal links
        self.internal_link_pattern = self.link_config.get(
            "internal_link_pattern",
            f"^https?://{urlparse(self.site_config['base_url']).netloc}",
        )

        # Whether to preserve anchor links (e.g., #section-id)
        self.preserve_anchor_links = self.link_config.get("preserve_anchor_links", True)

        # How to handle images
        self.image_handling = self.link_config.get("image_handling", "reference")

        logger.debug(f"Initialized LinkHandler with config: {self.link_config}")

    def process_links(
        self, content_data: Dict[str, Any], base_url: str
    ) -> Dict[str, Any]:
        """
        Process links in the Markdown content.

        Args:
            content_data: Dictionary containing markdown content
                {
                    'title': The page title,
                    'content': The Markdown content,
                    'url': The original URL,
                    'metadata': Additional metadata,
                    'format': 'markdown'
                }
            base_url: The base URL of the current page

        Returns:
            Dictionary with the same structure but with links processed
        """
        logger.info(f"Processing links for {content_data['url']}")

        try:
            # Extract content from the dictionary
            markdown_content = content_data["content"]

            # Process markdown links [text](url)
            processed_content = self._process_markdown_links(markdown_content, base_url)

            # Process image links ![alt](url)
            processed_content = self._process_image_links(processed_content, base_url)

            # Track which files this document links to
            linked_files = self._extract_linked_files(processed_content)

            # Update the content data dictionary
            result = content_data.copy()
            result["content"] = processed_content
            result["linked_files"] = linked_files

            logger.debug(f"Successfully processed links for {base_url}")
            return result

        except Exception as e:
            logger.error(f"Error processing links: {e}")
            # Return the original content with an error note
            result = content_data.copy()
            result["error"] = str(e)
            return result

    def _process_markdown_links(self, markdown_content: str, base_url: str) -> str:
        """
        Process Markdown links.

        Args:
            markdown_content: The Markdown content
            base_url: The base URL of the current page

        Returns:
            Markdown content with processed links
        """
        # Regular expression for Markdown links
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"

        def replace_link(match):
            text = match.group(1)
            url = match.group(2)

            # Skip anchor links within the same page
            if url.startswith("#"):
                return f"[{text}]({url})" if self.preserve_anchor_links else f"[{text}]"

            # Process the URL
            new_url = self._convert_url(url, base_url)
            return f"[{text}]({new_url})"

        return re.sub(link_pattern, replace_link, markdown_content)

    def _process_image_links(self, markdown_content: str, base_url: str) -> str:
        """
        Process image links.

        Args:
            markdown_content: The Markdown content
            base_url: The base URL of the current page

        Returns:
            Markdown content with processed image links
        """
        # Regular expression for Markdown image links
        image_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

        def replace_image(match):
            alt_text = match.group(1)
            image_url = match.group(2)

            # Process the image URL
            new_image_url = self._convert_image_url(image_url, base_url)
            return f"![{alt_text}]({new_image_url})"

        return re.sub(image_pattern, replace_image, markdown_content)

    def _convert_url(self, url: str, base_url: str) -> str:
        """
        Convert a URL to its appropriate form.

        Args:
            url: The URL to convert
            base_url: The base URL of the current page

        Returns:
            The converted URL
        """
        # Handle empty URLs
        if not url or url.isspace():
            return "#"

        # Parse the URL
        parsed_url = urlparse(url)

        # If it's an absolute URL
        if parsed_url.scheme:
            # Check if it's an internal link
            if re.match(self.internal_link_pattern, url):
                # Convert internal absolute URL to file reference
                return self._internal_url_to_file_reference(url)
            else:
                # External URL, keep as is
                return url
        else:
            # Relative URL, resolve against base URL and then convert
            full_url = urljoin(base_url, url)
            return self._internal_url_to_file_reference(full_url)

    def _convert_image_url(self, url: str, base_url: str) -> str:
        """
        Convert an image URL to its appropriate form.

        Args:
            url: The image URL to convert
            base_url: The base URL of the current page

        Returns:
            The converted image URL
        """
        # Parse the URL
        parsed_url = urlparse(url)

        # If the URL is already absolute
        if parsed_url.scheme:
            # For "reference" mode, keep external images as is
            if self.image_handling == "reference":
                return url
            # For "download" mode, we'd handle downloading the image elsewhere
            # and return the local path
            else:
                # Convert to a local path (this would be handled by the file system manager)
                image_name = Path(parsed_url.path).name
                return f"./images/{image_name}"
        else:
            # Relative URL
            full_url = urljoin(base_url, url)

            if self.image_handling == "reference":
                # Keep the full URL for reference
                return full_url
            else:
                # Convert to local path
                image_name = Path(parsed_url.path).name
                return f"./images/{image_name}"

    def _internal_url_to_file_reference(self, url: str) -> str:
        """
        Convert an internal URL to a file reference.

        Args:
            url: The internal URL

        Returns:
            File reference for the URL
        """
        parsed_url = urlparse(url)

        # Extract path and strip leading/trailing slashes
        path = parsed_url.path.strip("/")

        # Handle root or empty path
        if not path:
            return f"./{self.output_config['file_prefix']}INDEX.md"

        # Convert path to filename using naming convention
        file_name = self._path_to_filename(path)

        # Include anchor if present and configured to preserve
        anchor = ""
        if parsed_url.fragment and self.preserve_anchor_links:
            anchor = f"#{parsed_url.fragment}"

        return f"./{file_name}{anchor}"

    def _path_to_filename(self, path: str) -> str:
        """
        Convert a URL path to a filename using the configured naming convention.

        Args:
            path: The URL path

        Returns:
            The filename
        """
        # Remove file extension if present
        path = Path(path).stem

        # Replace slashes with underscores
        path = path.replace("/", "_")

        # Apply naming convention
        naming_convention = self.output_config.get(
            "naming_convention", "UPPERCASE_WITH_UNDERSCORES"
        )

        if naming_convention == "UPPERCASE_WITH_UNDERSCORES":
            path = path.upper().replace("-", "_").replace(" ", "_")
        elif naming_convention == "lowercase_with_underscores":
            path = path.lower().replace("-", "_").replace(" ", "_")
        elif naming_convention == "CamelCase":
            # Convert to camel case
            words = re.findall(r"[a-zA-Z0-9]+", path)
            path = "".join(word.capitalize() for word in words)

        # Add prefix and extension
        file_prefix = self.output_config.get("file_prefix", "")
        return f"{file_prefix}{path}.md"

    def _extract_linked_files(self, markdown_content: str) -> List[str]:
        """
        Extract a list of linked files from the Markdown content.

        Args:
            markdown_content: The Markdown content

        Returns:
            List of linked files
        """
        linked_files = []

        # Find all links to local markdown files
        link_pattern = r"\[([^\]]+)\]\(\.\/([^)#]+)(?:#[^)]*)?\)"
        for match in re.finditer(link_pattern, markdown_content):
            linked_file = match.group(2)
            if linked_file not in linked_files:
                linked_files.append(linked_file)

        return linked_files
