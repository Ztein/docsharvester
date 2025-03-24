"""
Error handler implementation.

This module provides classes and functions for centralized error handling, logging,
and retry functionality for the MCP Documentation Scraper.
"""

import functools
import logging
import sys
import time
import traceback
from pathlib import Path
from typing import Type, Callable, Dict, Any, List, Tuple, Optional, Union, Iterable


# Custom exceptions for specific error types
class MCP_Exception(Exception):
    """Base exception for all MCP Documentation Scraper exceptions."""
    pass


class CrawlingError(MCP_Exception):
    """Exception raised for errors during web crawling."""
    pass


class ExtractionError(MCP_Exception):
    """Exception raised for errors during content extraction."""
    pass


class ConversionError(MCP_Exception):
    """Exception raised for errors during content conversion."""
    pass


class LinkProcessingError(MCP_Exception):
    """Exception raised for errors during link processing."""
    pass


class FileSystemError(MCP_Exception):
    """Exception raised for errors during file system operations."""
    pass


def setup_error_handling(config_manager) -> None:
    """
    Set up logging configuration based on the provided configuration.

    Args:
        config_manager: The configuration manager instance
    """
    # Get logging configuration
    error_config = config_manager.get_section("error_handling")
    log_level_str = error_config.get("log_level", "INFO")
    log_file = error_config.get("log_file", None)
    
    # Convert string log level to logging constant
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    # Set up handlers list
    handlers = [logging.StreamHandler()]
    
    # Add file handler if configured
    if log_file:
        # Ensure directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        handlers.append(logging.FileHandler(log_file))
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers
    )
    
    logging.debug(f"Error handling configured with log level: {log_level_str}")


def retry_on_exception(max_retries: int = 3, 
                        retry_delay: int = 1, 
                        exceptions: Tuple[Type[Exception], ...] = (Exception,),
                        logger: Optional[logging.Logger] = None) -> Callable:
    """
    Decorator to retry a function on specified exceptions.

    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
        exceptions: Tuple of exception types to catch and retry on
        logger: Logger to use for logging retry attempts

    Returns:
        Decorated function that implements retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _logger = logger or logging.getLogger(func.__module__)
            
            # Get function name safely (handles MagicMock objects in tests)
            func_name = getattr(func, "__name__", str(func))
            
            attempts = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts > max_retries:
                        _logger.error(
                            f"Max retries ({max_retries}) exceeded for {func_name}: {e}"
                        )
                        raise
                    
                    _logger.warning(
                        f"Retry {attempts}/{max_retries} for {func_name} after error: {e}"
                    )
                    time.sleep(retry_delay)
        return wrapper
    return decorator


class ErrorHandler:
    """
    Centralized error handling and logging class.
    
    This class provides methods for handling errors and logging at different 
    severity levels throughout the application.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the ErrorHandler.
        
        Args:
            config_manager: The configuration manager instance
        """
        self.config_manager = config_manager
        self.error_config = config_manager.get_section("error_handling")
        
        # Get retry configuration
        self.max_retries = self.error_config.get("max_retries", 3)
        self.retry_delay = self.error_config.get("retry_delay", 1)
        
        # Create a dictionary to track failures
        self.failures: Dict[str, List[Dict[str, Any]]] = {
            "crawling": [],
            "extraction": [],
            "conversion": [],
            "link_processing": [],
            "file_system": []
        }
        
        self.logger = logging.getLogger(__name__)
    
    def log_error(self, module: str, message: str, exception: Optional[Exception] = None, 
                  context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error with detailed information.
        
        Args:
            module: The module where the error occurred
            message: The error message
            exception: The exception that was raised, if any
            context: Additional context data for the error
        """
        context_str = f" Context: {context}" if context else ""
        if exception:
            exc_info = sys.exc_info()
            self.logger.error(
                f"{module} - {message}: {exception}{context_str}", 
                exc_info=exc_info if exc_info[0] is not None else None
            )
        else:
            self.logger.error(f"{module} - {message}{context_str}")
    
    def log_warning(self, module: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a warning.
        
        Args:
            module: The module where the warning occurred
            message: The warning message
            context: Additional context data for the warning
        """
        context_str = f" Context: {context}" if context else ""
        self.logger.warning(f"{module} - {message}{context_str}")
    
    def log_info(self, module: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an informational message.
        
        Args:
            module: The module where the info is from
            message: The informational message
            context: Additional context data
        """
        context_str = f" Context: {context}" if context else ""
        self.logger.info(f"{module} - {message}{context_str}")
    
    def log_debug(self, module: str, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a debug message.
        
        Args:
            module: The module where the debug info is from
            message: The debug message
            context: Additional context data
        """
        context_str = f" Context: {context}" if context else ""
        self.logger.debug(f"{module} - {message}{context_str}")
    
    def track_failure(self, failure_type: str, url: str, error: str, 
                      context: Optional[Dict[str, Any]] = None) -> None:
        """
        Track a failure for possible retry later.
        
        Args:
            failure_type: The type of failure (crawling, extraction, etc.)
            url: The URL that failed
            error: The error message
            context: Additional context data
        """
        if failure_type not in self.failures:
            self.failures[failure_type] = []
        
        self.failures[failure_type].append({
            "url": url,
            "error": error,
            "context": context or {},
            "timestamp": time.time()
        })
        
        self.logger.debug(f"Tracked failure: {failure_type} - {url} - {error}")
    
    def get_failures(self, failure_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get tracked failures, optionally filtered by type.
        
        Args:
            failure_type: The type of failures to get, or None for all

        Returns:
            Dictionary of failures by type
        """
        if failure_type:
            return {failure_type: self.failures.get(failure_type, [])}
        return self.failures
    
    def clear_failures(self, failure_type: Optional[str] = None) -> None:
        """
        Clear tracked failures, optionally filtered by type.
        
        Args:
            failure_type: The type of failures to clear, or None for all
        """
        if failure_type:
            self.failures[failure_type] = []
        else:
            for key in self.failures:
                self.failures[key] = []
    
    def get_retry_decorator(self, exceptions: Tuple[Type[Exception], ...] = (Exception,)) -> Callable:
        """
        Get a retry decorator configured with the parameters from config.
        
        Args:
            exceptions: Tuple of exception types to catch and retry on

        Returns:
            Configured retry decorator
        """
        return retry_on_exception(
            max_retries=self.max_retries,
            retry_delay=self.retry_delay,
            exceptions=exceptions,
            logger=self.logger
        ) 