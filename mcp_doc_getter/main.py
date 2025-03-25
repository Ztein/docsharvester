#!/usr/bin/env python3
"""
DocHarvester - Universal Documentation Scraper

This module serves as the main entry point for the DocHarvester universal documentation scraper.
It orchestrates the scraping process using the various components.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

# Import the ConfigManager from its package
from mcp_doc_getter.src.config_manager import ConfigManager
from mcp_doc_getter.src.web_crawler import WebCrawler
from mcp_doc_getter.src.content_extractor import ContentExtractor
from mcp_doc_getter.src.markdown_converter import MarkdownConverter
from mcp_doc_getter.src.link_handler import LinkHandler
from mcp_doc_getter.src.file_system_manager import FileSystemManager
from mcp_doc_getter.src.error_handler import setup_error_handling, ErrorHandler, MCP_Exception
from mcp_doc_getter.src.validation import ExternalLinkValidator

# Import MCP-specific components
from mcp_doc_getter.src.mcp_specific.mcp_extractor import MCPContentExtractor


def setup_logging(log_level: str = "INFO") -> None:
    """Set up logging configuration."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("docharvester.log")],
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DocHarvester - Universal Documentation Scraper that converts web documentation to Markdown"
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
    parser.add_argument(
        "--use-generic",
        action="store_true",
        help="Use generic extractor instead of MCP-specific extractor",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the scraper."""
    args = parse_args()
    setup_logging(args.log_level)

    logging.info("Starting DocHarvester Universal Documentation Scraper")

    try:
        # Use the ConfigManager instead of directly loading the YAML
        config_manager = ConfigManager(args.config)
        logging.info(f"Configuration loaded and validated from {args.config}")

        # Set up error handling
        setup_error_handling(config_manager)
        error_handler = ErrorHandler(config_manager)
        
        # Initialize components
        web_crawler = WebCrawler(config_manager)
        
        # Use MCP-specific extractor unless --use-generic is specified
        if args.use_generic:
            content_extractor = ContentExtractor(config_manager)
            logging.info("Using generic content extractor")
        else:
            content_extractor = MCPContentExtractor(config_manager)
            logging.info("Using MCP-specific content extractor")
            
        markdown_converter = MarkdownConverter(config_manager)
        link_handler = LinkHandler(config_manager)
        file_system_manager = FileSystemManager(config_manager)
        external_link_validator = ExternalLinkValidator(config_manager)

        # Get the base URL from the configuration and append /docs to target the documentation
        base_url = config_manager.get('site', 'base_url')
        docs_url = f"{base_url}/docs"
        
        # Add '/docs' to the WebCrawler's include patterns to ensure it's crawled
        if '/docs' not in web_crawler.include_patterns:
            web_crawler.include_patterns.append('/docs')
        
        # Crawl the website and get URLs
        error_handler.log_info("main", f"Starting to crawl from {docs_url}")
        urls = web_crawler.crawl(start_url=docs_url)
        error_handler.log_info("main", f"Found {len(urls)} pages to process")

        # Process each URL
        processed_count = 0
        failed_count = 0
        
        for url in urls:
            try:
                error_handler.log_info("main", f"Processing {url}")
                
                # Fetch the page
                response = web_crawler.fetch_url(url)
                html_content = response.text
                
                # Extract content
                extracted_content = content_extractor.extract(html_content, url)
                
                # Convert to markdown
                markdown_content = markdown_converter.convert(extracted_content)
                
                # If using MCP-specific extractor, apply its postprocessing to the markdown
                if not args.use_generic and hasattr(content_extractor, 'mcp_handler'):
                    markdown_content = content_extractor.mcp_handler.postprocess_markdown(markdown_content)
                
                # Process links
                processed_content = link_handler.process_links(markdown_content, url)
                
                # Validate external links
                validation_results = external_link_validator.validate_links(processed_content)
                
                # Add validation results to content metadata
                processed_content["validation"] = validation_results
                
                # Save to file system
                file_path = file_system_manager.save_content(processed_content, url)
                
                processed_count += 1
                error_handler.log_info("main", f"Successfully processed {url} -> {file_path}")
                
            except Exception as e:
                failed_count += 1
                error_handler.log_error("main", f"Failed to process {url}", e)
                error_handler.track_failure("processing", url, str(e))

        # Generate validation report
        validation_report = external_link_validator.generate_report()
        
        # Save validation report
        report_path = file_system_manager.save_validation_report(validation_report)
        error_handler.log_info("main", f"Validation report saved to {report_path}")

        # Summary
        error_handler.log_info(
            "main", 
            f"Scraping completed: {processed_count} pages successful, {failed_count} pages failed"
        )
        
        # Report validation metrics
        metrics = validation_report["metrics"]
        error_handler.log_info(
            "main",
            f"Link validation: {metrics['valid_links']}/{metrics['total_external_links']} valid, "
            f"{metrics['invalid_links']} invalid, {metrics['api_links']} API links"
        )
        
        # Report any failures
        failures = error_handler.get_failures()
        if failures:
            error_handler.log_warning(
                "main",
                f"There were {len(failures)} failures during processing. "
                "Check the error log for details."
            )

    except Exception as e:
        error_handler.log_error("main", "Fatal error", e)
        sys.exit(1)

    logging.info("DocHarvester completed successfully")


if __name__ == "__main__":
    main()
