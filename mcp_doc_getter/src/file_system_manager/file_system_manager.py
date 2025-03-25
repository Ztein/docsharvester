"""
File system manager implementation.

This module provides the FileSystemManager class for saving processed content to the file system.
"""

import logging
import os
import re
import json
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

    def __init__(self, base_dir: str):
        """Initialize the FileSystemManager with a base directory."""
        self.base_dir = Path(base_dir)
        
        # Create directory structure
        self.content_dir = self.base_dir / "content"
        self.images_dir = self.base_dir / "images"
        
        # Create directories if they don't exist
        self.content_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug(
            f"Initialized FileSystemManager with base directory: {self.base_dir}"
        )

    def save_content(self, content: Dict[str, str], url: str) -> Path:
        """Save content to a file in the content directory."""
        try:
            # Get base file path
            file_path = self._get_file_path(url)
            
            # Handle filename collisions
            counter = 1
            while file_path.exists():
                stem = file_path.stem
                # Remove any existing counter suffix
                if '_' in stem:
                    stem = stem.rsplit('_', 1)[0]
                file_path = file_path.with_name(f"{stem}_{counter}{file_path.suffix}")
                counter += 1
            
            # Save the content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content["content"])
                
            logger.info(f"Saved content to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving content: {e}")
            raise
            
    def save_image(self, image_data: bytes, url: str) -> Optional[Path]:
        """Save an image to the images directory."""
        try:
            # Extract filename from URL
            image_filename = url.split("/")[-1]
            
            # Create the full path
            image_path = self.images_dir / image_filename
            
            # Handle filename collisions
            counter = 1
            while image_path.exists():
                stem = image_path.stem
                # Remove any existing counter suffix
                if '_' in stem:
                    stem = stem.rsplit('_', 1)[0]
                image_path = image_path.with_name(f"{stem}_{counter}{image_path.suffix}")
                counter += 1
            
            # Save the image
            with open(image_path, "wb") as f:
                f.write(image_data)
                
            logger.info(f"Saved image to {image_path}")
            return image_path
            
        except Exception as e:
            logger.error(f"Error saving image {url}: {e}")
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
        file_path = self.content_dir / file_name

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

        # Replace slashes with underscores and sanitize path
        path = path.replace("/", "_")
        
        # Sanitize by removing special characters
        path = re.sub(r'[^a-zA-Z0-9_\-]', '', path)

        # Apply naming convention
        naming_convention = "UPPERCASE_WITH_UNDERSCORES"

        if naming_convention == "UPPERCASE_WITH_UNDERSCORES":
            path = path.upper().replace("-", "_").replace(" ", "_")
        elif naming_convention == "lowercase_with_underscores":
            path = path.lower().replace("-", "_").replace(" ", "_")
        elif naming_convention == "CamelCase":
            # Convert to camel case
            words = re.findall(r"[a-zA-Z0-9]+", path)
            path = "".join(word.capitalize() for word in words)

        # Add prefix and extension
        file_prefix = ""
        return f"{file_prefix}{path}.md"

    def cleanup(self) -> None:
        """
        Clean up temporary files and resources.

        This should be called when scraping is complete.
        """
        # Nothing to clean up at the moment
        pass
