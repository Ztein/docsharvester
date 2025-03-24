# Tests for MCP Documentation Scraper

This directory contains tests for the MCP Documentation Scraper project. The tests are organized by component to match the project structure.

## Test Structure

- `config_manager/`: Tests for the configuration manager component
- `web_crawler/`: Tests for the web crawler component
- `content_extractor/`: Tests for the content extraction component
- `markdown_converter/`: Tests for the HTML to Markdown conversion component
- `link_handler/`: Tests for the link processing component
- `file_system_manager/`: Tests for the file system operations component
- `error_handler/`: Tests for the error handling component
- `conftest.py`: Shared pytest fixtures for all tests
- `test_utils.py`: Utility functions and classes for testing

## Fixtures

Common test fixtures are defined in `conftest.py` and can be used in any test file:

- `mock_config`: A mock implementation of the ConfigManager with default configuration
- `custom_mock_config`: A configurable mock ConfigManager
- `temp_dir`: A temporary directory that is cleaned up after the test
- `test_file_manager`: A utility for managing test files and directories
- `sample_html`: Sample HTML content for testing
- `sample_markdown`: Sample Markdown content for testing
- `sample_content_dict`: A sample content dictionary for testing

## Running Tests

To run all tests:

```bash
pytest
```

To run tests for a specific component:

```bash
pytest tests/component_name/
```

To run tests with output:

```bash
pytest -v
```

## Test Utilities

The `test_utils.py` file provides useful utilities for tests:

- `MockConfigManager`: A configurable mock for the ConfigManager
- `TestFileManager`: A utility for managing test files and directories
- `DEFAULT_CONFIG`: Default configuration values for testing

## Writing Tests

When writing new tests:

1. Place them in the appropriate component directory
2. Use fixtures from `conftest.py` where possible
3. Follow the existing naming conventions
4. Include docstrings for test classes and methods
5. Use test-driven development where appropriate

For components without implementation yet, tests should be marked with `@unittest.skip("Implementation pending")` and include commented expectations for when the implementation is available. 