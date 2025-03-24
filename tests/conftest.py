"""
Pytest fixtures for MCP Documentation Scraper tests.

This module provides fixtures that can be used across all test files.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock

from tests.test_utils import MockConfigManager, TestFileManager, DEFAULT_CONFIG


@pytest.fixture
def mock_config():
    """
    Fixture that provides a mock ConfigManager with default configuration.
    
    Returns:
        A MockConfigManager instance with default configuration.
    """
    return MockConfigManager(DEFAULT_CONFIG.copy()).mock


@pytest.fixture
def custom_mock_config(request):
    """
    Fixture that provides a mock ConfigManager with custom configuration.
    
    Usage:
        @pytest.mark.parametrize('custom_mock_config', [
            {'site': {'name': 'Custom Site'}}
        ], indirect=True)
        def test_something(custom_mock_config):
            ...
    
    Args:
        request: The pytest request object containing the parameter
    
    Returns:
        A MockConfigManager instance with custom configuration.
    """
    config_data = DEFAULT_CONFIG.copy()
    custom_config = getattr(request, 'param', {})
    
    # Update the config with custom values
    for section, section_data in custom_config.items():
        if section not in config_data:
            config_data[section] = {}
        config_data[section].update(section_data)
    
    return MockConfigManager(config_data).mock


@pytest.fixture
def temp_dir():
    """
    Fixture that provides a temporary directory for testing.
    
    Returns:
        Path to a temporary directory that will be cleaned up after the test.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_file_manager():
    """
    Fixture that provides a TestFileManager instance.
    
    Returns:
        A TestFileManager instance that will clean up after the test.
    """
    file_manager = TestFileManager()
    yield file_manager
    file_manager.cleanup()


@pytest.fixture
def sample_html():
    """
    Fixture that provides sample HTML content for testing.
    
    Returns:
        A string containing sample HTML content.
    """
    return """<!DOCTYPE html>
<html>
<head>
    <title>Sample Page</title>
</head>
<body>
    <h1 class="title">Sample Title</h1>
    <main class="content">
        <h2>Section 1</h2>
        <p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
        <pre><code class="language-python">def hello_world():
    print("Hello, World!")
        </code></pre>
        <h2>Section 2</h2>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <table>
            <tr>
                <th>Column 1</th>
                <th>Column 2</th>
            </tr>
            <tr>
                <td>Data 1</td>
                <td>Data 2</td>
            </tr>
        </table>
    </main>
</body>
</html>"""


@pytest.fixture
def sample_markdown():
    """
    Fixture that provides sample Markdown content for testing.
    
    Returns:
        A string containing sample Markdown content.
    """
    return """# Sample Title

## Section 1

This is a paragraph with **bold** and *italic* text.

```python
def hello_world():
    print("Hello, World!")
```

## Section 2

- Item 1
- Item 2

| Column 1 | Column 2 |
| --- | --- |
| Data 1 | Data 2 |
"""


@pytest.fixture
def sample_content_dict():
    """
    Fixture that provides a sample content dictionary for testing.
    
    Returns:
        A dictionary containing sample content.
    """
    return {
        "title": "Sample Title",
        "content": """<main class="content">
        <h2>Section 1</h2>
        <p>This is a paragraph with <strong>bold</strong> and <em>italic</em> text.</p>
        <pre><code class="language-python">def hello_world():
    print("Hello, World!")
        </code></pre>
        </main>""",
        "url": "https://example.com/docs/sample-page",
        "original_url": "https://example.com/docs/sample-page"
    } 