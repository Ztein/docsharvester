# DocHarvester - Universal Documentation Scraper Architecture Plan

## Overview
This project aims to develop a Python-based web scraper that downloads and stores documentation from various websites (including ModelContextProtocol.io and Pydantic AI) into Markdown files for offline reference. The scraper is designed to be adaptable for different documentation sites through configuration.

## System Architecture

### Components

1. **Configuration Manager**
   - Handles YAML-based configuration
   - Provides settings for crawling, parsing, and output
   - Enables easy adaptation to different documentation sites

2. **Web Crawler**
   - Traverses documentation site systematically
   - Respects robots.txt and implements rate limiting
   - Identifies all documentation pages for processing
   - Handles session management and retries

3. **Content Extractor**
   - Parses HTML content using site-specific selectors
   - Extracts meaningful documentation text
   - Handles various content structures (headers, code blocks, tables, etc.)

4. **Markdown Converter**
   - Converts HTML to well-formatted Markdown
   - Preserves formatting elements (headers, code blocks, tables, lists, etc.)
   - Processes images with appropriate references

5. **Link Handler**
   - Preserves external links
   - Converts internal links to relative paths for local access
   - Handles anchor links appropriately

6. **File System Manager**
   - Saves content following the specified naming convention
   - Organizes files in a structured hierarchy
   - Handles file operations with appropriate error handling

7. **Error Handler**
   - Implements robust error handling for network and parsing issues
   - Logs errors and warnings
   - Provides mechanisms to skip problematic pages and resume operations

### Data Flow

1. Configuration is loaded from YAML file
2. Crawler traverses the documentation site
3. Content extractor parses each page
4. Markdown converter transforms content
5. Link handler processes all links
6. File system manager saves the content to disk

## Technology Stack

- **Python 3.9+**
- **UV package manager** for dependency management
- **Key Libraries**:
  - BeautifulSoup4 for HTML parsing
  - Requests or httpx for HTTP requests
  - Markdown or html2text for HTML to Markdown conversion
  - PyYAML for configuration

## Project Structure

```
docharvester/
├── config/
│   ├── mcp_config.yaml     # ModelContextProtocol.io configuration
│   └── pydantic_config.yaml # Example additional site configuration
├── src/
│   ├── __init__.py
│   ├── config_manager.py
│   ├── web_crawler.py
│   ├── content_extractor.py
│   ├── markdown_converter.py
│   ├── link_handler.py
│   ├── file_system_manager.py
│   └── error_handler.py
├── tests/
│   ├── __init__.py
│   ├── test_config_manager.py
│   ├── test_web_crawler.py
│   └── ... (tests for each component)
├── MCP_DOCS/               # Output directory example for MCP documentation
├── .gitignore
├── README.md
├── pyproject.toml          # Project metadata and dependencies
└── main.py                 # Entry point
```

## Configuration Format
The configuration file (YAML) will include:

```yaml
site:
  name: "ModelContextProtocol"
  base_url: "https://modelcontextprotocol.io"
  
crawling:
  include_patterns:
    - "/docs/*"
  exclude_patterns:
    - "/blog/*"
  max_depth: 5
  rate_limit: 1  # requests per second
  
extraction:
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