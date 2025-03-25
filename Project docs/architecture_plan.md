# DocHarvester - Universal Documentation Scraper Architecture Plan

## Overview
This project aims to develop a Python-based web scraper that downloads and stores documentation from various websites into Markdown files for offline reference. The scraper is designed to be adaptable for different documentation sites through configuration.

## Core Principles
1. **Simplicity**: Each component has a single, clear responsibility
2. **Flexibility**: Easy to adapt to different documentation sites
3. **Reliability**: Robust error handling and recovery
4. **Performance**: Efficient processing and caching
5. **Maintainability**: Clear interfaces and documentation

## System Architecture

### Components

1. **Configuration Manager**
   - Handles YAML-based configuration
   - Provides settings for crawling, parsing, and output
   - Enables easy adaptation to different documentation sites
   - Supports environment-specific configurations

2. **Plugin System**
   - Simple plugin interface for site-specific implementations
   - Site-specific configuration and rules
   - Content extraction and processing
   - Link handling and transformation
   - Rate limiting and authentication

3. **Web Crawler**
   - Traverses documentation site systematically
   - Respects robots.txt and implements rate limiting
   - Identifies all documentation pages for processing
   - Handles session management and retries
   - Supports authentication when required

4. **Content Processor**
   - Parses HTML content using site-specific selectors
   - Extracts meaningful documentation text
   - Converts HTML to well-formatted Markdown
   - Handles various content structures
   - Processes images and links

5. **Storage Manager**
   - Manages file system operations
   - Implements caching for efficiency
   - Organizes files in structured hierarchy
   - Handles file operations with error handling
   - Supports different output formats

6. **Monitoring Handler**
   - Tracks performance metrics
   - Logs errors and warnings
   - Provides recovery mechanisms
   - Generates performance reports
   - Handles retry logic

### Data Flow

1. **Load Configuration**
   - Load and validate configuration
   - Initialize plugin system

2. **Initialize Plugin**
   - Load site-specific plugin
   - Configure site-specific rules

3. **Crawl Site**
   - Traverse documentation pages
   - Respect rate limits and robots.txt
   - Handle authentication if needed

4. **Process Content**
   - Extract and parse content
   - Convert to Markdown
   - Process links and images
   - Handle errors and retries

5. **Save Results**
   - Cache processed content
   - Save to file system
   - Generate reports

## Technology Stack

- **Python 3.9+**
- **UV package manager** for dependency management
- **Key Libraries**:
  - BeautifulSoup4 for HTML parsing
  - httpx for HTTP requests
  - Markdown for HTML to Markdown conversion
  - PyYAML for configuration
  - structlog for logging

## Project Structure

```
docharvester/
├── config/
│   ├── mcp_config.yaml     # ModelContextProtocol.io configuration
│   └── pydantic_config.yaml # Example additional site configuration
├── src/
│   ├── __init__.py
│   ├── config_manager.py
│   ├── plugin_system.py
│   ├── web_crawler.py
│   ├── content_processor.py
│   ├── storage_manager.py
│   ├── monitoring_handler.py
│   └── main.py
├── plugins/
│   ├── __init__.py
│   ├── mcp_plugin.py
│   └── pydantic_plugin.py
├── tests/
│   ├── __init__.py
│   ├── test_config_manager.py
│   ├── test_web_crawler.py
│   └── ... (tests for each component)
├── docs/
│   ├── README.md
│   └── plugin_guide.md
├── .gitignore
├── pyproject.toml
└── main.py
```

## Configuration Format
The configuration file (YAML) will include:

```yaml
site:
  name: "ModelContextProtocol"
  base_url: "https://modelcontextprotocol.io"
  plugin: "mcp_plugin"  # Name of the plugin to use
  
crawling:
  include_patterns:
    - "/docs/*"
  exclude_patterns:
    - "/blog/*"
  max_depth: 5
  rate_limit: 1  # requests per second
  
processing:
  content_selector: "main.content"
  title_selector: "h1.title"
  ignore_selectors:
    - "div.sidebar"
    - "footer"
    
output:
  base_dir: "MCP_DOCS"
  file_prefix: "MCP_"
  naming_convention: "UPPERCASE_WITH_UNDERSCORES"
```

## Implementation Approach

The implementation will follow a modular, test-driven approach to ensure high code quality and maintainability. Each component will be developed independently with clear interfaces, allowing for easy testing and future extension.

## Deployment Strategy

The application will be packaged as a command-line tool that can be installed using pip or run directly from source. It will be designed to run both as a one-time process and as a scheduled task for documentation updates. 