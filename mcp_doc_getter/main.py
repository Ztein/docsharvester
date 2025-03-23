#!/usr/bin/env python3
"""
MCP Documentation Scraper - Main Entry Point

This module serves as the main entry point for the MCP documentation scraper.
It orchestrates the scraping process using the various components.
"""

import argparse
import logging
import sys
from pathlib import Path

# Import the ConfigManager from its package
from mcp_doc_getter.src.config_manager import ConfigManager
from mcp_doc_getter.src.web_crawler import WebCrawler
from mcp_doc_getter.src.content_extractor import ContentExtractor
from mcp_doc_getter.src.markdown_converter import MarkdownConverter
from mcp_doc_getter.src.link_handler import LinkHandler
from mcp_doc_getter.src.file_system_manager import FileSystemManager

# These imports will be implemented as the project progresses
# from mcp_doc_getter.src.error_handler import setup_error_handling


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("mcp_scraper.log")],
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape documentation from ModelContextProtocol.io and convert to Markdown"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="mcp_doc_getter/config/mcp_config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the scraper."""
    args = parse_args()
    setup_logging(args.log_level)

    logging.info("Starting MCP Documentation Scraper")

    try:
        # Use the ConfigManager instead of directly loading the YAML
        config_manager = ConfigManager(args.config)
        logging.info(f"Configuration loaded and validated from {args.config}")

        # Initialize components
        web_crawler = WebCrawler(config_manager)
        content_extractor = ContentExtractor(config_manager)
        markdown_converter = MarkdownConverter(config_manager)
        link_handler = LinkHandler(config_manager)
        file_system_manager = FileSystemManager(config_manager)

        # Crawl the website and get URLs
        urls = web_crawler.crawl()

        # Process each URL
        for url in urls:
            html_content = web_crawler.get_content(url)
            extracted_content = content_extractor.extract(html_content, url)
            markdown_content = markdown_converter.convert(extracted_content)
            processed_content = link_handler.process_links(markdown_content, url)
            file_system_manager.save_content(processed_content, url)

            logging.info(f"Processed {url}")

        logging.info("Scraping completed successfully")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
