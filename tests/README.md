# Tests for MCP Documentation Scraper

This directory contains tests for the MCP Documentation Scraper project. The tests are organized by component to match the project structure.

## Test Environment Setup

1. Ensure you're in the virtual environment:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install test dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

Common test commands:
```bash
# Run all tests
python -m pytest

# Run with verbose output (recommended)
python -m pytest -v

# Run specific component tests
python -m pytest tests/component_name/

# Run a specific test file
python -m pytest tests/component_name/test_file.py

# Run a specific test case
python -m pytest tests/component_name/test_file.py::TestClass::test_method

# Generate coverage report
python -m pytest --cov=mcp_doc_getter tests/
```

## Project Test Structure

```
tests/
├── config_manager/      # Configuration management tests
├── content_extractor/   # HTML content extraction tests
├── error_handler/       # Error handling and logging tests
├── file_system_manager/ # File operations tests
├── integration/         # End-to-end integration tests
├── link_handler/        # Link processing tests
├── markdown_converter/  # HTML to Markdown conversion tests
├── validation/          # Content validation tests
├── web_crawler/        # Web crawling tests
├── conftest.py         # Shared pytest fixtures
├── test_utils.py       # Test utilities
└── test_mcp_specific.py # MCP-specific functionality tests
```

## Available Fixtures

Common test fixtures in `conftest.py`:

```python
# Example usage of fixtures
def test_content_extraction(mock_config, sample_html):
    extractor = ContentExtractor(mock_config)
    content = extractor.extract(sample_html)
    assert content is not None
```

Key fixtures:
- `mock_config`: Pre-configured ConfigManager with default settings
- `custom_mock_config`: Configurable mock ConfigManager
- `temp_dir`: Temporary directory that's automatically cleaned up
- `sample_html`: Sample HTML content for testing
- `sample_markdown`: Sample Markdown content for testing
- `sample_content_dict`: Sample content dictionary

## Test Utilities

`test_utils.py` provides:
- `MockConfigManager`: Configurable configuration mock
- `TestFileManager`: File and directory management utilities
- `DEFAULT_CONFIG`: Default test configuration values

## Writing New Tests

1. Place tests in the appropriate component directory
2. Use existing fixtures from `conftest.py` when possible
3. Follow the naming pattern: `test_<functionality>.py`
4. Include docstrings for test classes and methods
5. Use descriptive test names that explain the test case

Example:
```python
def test_extract_content_with_missing_selector(mock_config):
    """Test that content extraction handles missing CSS selectors gracefully."""
    extractor = ContentExtractor(mock_config)
    result = extractor.extract("<html><body>Test</body></html>")
    assert result.get('content') == "Test"
```

## Skipped Tests

Some integration tests are currently skipped as they require implementation:
- `test_full_pipeline_integration`
- `test_scrape_single_page`

These tests will be enabled as the corresponding functionality is implemented. 