"""
Error handler module.

This module provides functionality for error handling, logging, and retrying operations.
"""

from mcp_doc_getter.src.error_handler.error_handler import (
    ErrorHandler,
    setup_error_handling,
    retry_on_exception,
    MCP_Exception,
    CrawlingError,
    ExtractionError,
    ConversionError,
    LinkProcessingError,
    FileSystemError,
)

__all__ = [
    "ErrorHandler",
    "setup_error_handling",
    "retry_on_exception",
    "MCP_Exception",
    "CrawlingError",
    "ExtractionError",
    "ConversionError",
    "LinkProcessingError",
    "FileSystemError",
]
