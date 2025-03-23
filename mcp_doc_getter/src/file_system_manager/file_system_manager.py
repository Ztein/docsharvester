"""
File system manager implementation.

This module provides the FileSystemManager class for saving processed content to the file system.
"""

import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class FileSystemManager:
    """
    Manages saving content to the file system.

    This class is responsible for handling the storage of processed content,
    including creating directories, saving files, and managing assets like images.
    """

    def __init__(self, config_manager):
        """
        Initialize the FileSystemManager.

        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.output_config = self.config_manager.get_section("output")
        self.link_config = self.config_manager.get_section("link_handling")

        # Base directory for output
        self.base_dir = Path(self.output_config.get("base_dir", "MCP_DOCS"))

        # Image directory
        self.image_dir = self.base_dir / "images"

        # Set to track processed files to avoid duplicates
        self.processed_files: Set[str] = set()

        logger.debug(
            f"Initialized FileSystemManager with base directory: {self.base_dir}"
        )

        # Initialize the directory structure
        self._init_directory_structure()

    def _init_directory_structure(self) -> None:
        """
        Initialize the directory structure for output.

        Creates the base directory and subdirectories as needed.
        """
        # Create base directory
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"Created output directory: {self.base_dir}")

        # Create images directory if downloading images
        if self.link_config.get("image_handling", "reference") == "download":
            os.makedirs(self.image_dir, exist_ok=True)
            logger.info(f"Created images directory: {self.image_dir}")

    def save_content(self, content_data: Dict[str, Any], url: str) -> Optional[Path]:
        """
        Save processed content to disk.

        Args:
            content_data: Dictionary containing processed content
                {
                    'title': The page title,
                    'content': The processed Markdown content,
                    'url': The original URL,
                    'metadata': Additional metadata,
                    'format': 'markdown',
                    'linked_files': List of files this document links to
                }
            url: The URL of the content

        Returns:
            Path to the saved file, or None if saving failed
        """
        try:
            # Determine the filename
            file_path = self._get_file_path(url)

            # Check if this file has already been processed
            file_str = str(file_path)
            if file_str in self.processed_files:
                logger.warning(f"Skipping already processed file: {file_path}")
                return file_path

            # Save the content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content_data["content"])

            # Add to processed files
            self.processed_files.add(file_str)

            logger.info(f"Saved content to {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error saving content for {url}: {e}")
            return None

    def save_image(self, image_url: str, image_data: bytes) -> Optional[Path]:
        """
        Save an image to disk.

        Args:
            image_url: The URL of the image
            image_data: The binary image data

        Returns:
            Path to the saved image, or None if saving failed
        """
        try:
            # Extract the filename from the URL
            parsed_url = urlparse(image_url)
            image_filename = Path(parsed_url.path).name

            # Handle case where filename might be empty or invalid
            if not image_filename or len(image_filename) < 3:
                # Generate a filename based on the URL
                image_filename = f"image_{hash(image_url) % 10000}.png"

            # Create the full path
            image_path = self.image_dir / image_filename

            # Save the image
            with open(image_path, "wb") as f:
                f.write(image_data)

            logger.info(f"Saved image to {image_path}")
            return image_path

        except Exception as e:
            logger.error(f"Error saving image {image_url}: {e}")
            return None

    def _get_file_path(self, url: str) -> Path:
        """
        Determine the file path for a URL.

        Args:
            url: The URL to determine the file path for

        Returns:
            Path object for the file
        """
        parsed_url = urlparse(url)

        # Extract path and strip leading/trailing slashes
        path = parsed_url.path.strip("/")

        # Handle root or empty path
        if not path:
            path = "index"

        # Convert path to filename using naming convention
        file_name = self._get_file_name(path)

        # Create full path
        file_path = self.base_dir / file_name

        return file_path

    def _get_file_name(self, path: str) -> str:
        """
        Get the file name for a path.

        Args:
            path: The URL path

        Returns:
            The file name
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

    def cleanup(self) -> None:
        """
        Clean up temporary files and resources.

        This should be called when scraping is complete.
        """
        # Nothing to clean up at the moment
        pass
