# MCP Documentation Scraper

A Python-based web scraper that downloads and stores documentation from ModelContextProtocol.io (and other sites) into Markdown files for offline reference.

## Features

- Downloads complete ModelContextProtocol.io documentation
- Converts HTML content to well-formatted Markdown
- Maintains link integrity within saved documents
- Organizes content in a structured file hierarchy
- Easily extensible to other documentation sources

## Installation

### Prerequisites

- Python 3.9 or higher
- UV package manager (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mcp_doc_getter.git
   cd mcp_doc_getter
   ```

2. Set up the environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
mcp-scraper
```

### Custom Configuration

Specify a custom configuration file:

```bash
mcp-scraper --config path/to/config.yaml
```

### Configuration Options

Create a YAML configuration file with the following structure:

```yaml
site:
  name: "ModelContextProtocol"
  base_url: "https://modelcontextprotocol.io"
  
crawling:
  include_patterns:
    - "/docs/*"
  exclude_patterns:
    - "/blog/*"
  rate_limit: 1  # requests per second
  
extraction:
  content_selector: "main.content"
  title_selector: "h1.title"
  
output:
  base_dir: "MCP_DOCS"
  file_prefix: "MCP_"
```

## Extending to Other Sites

To adapt the scraper for other documentation sites:

1. Create a new configuration file for the target site
2. Modify the selectors to match the site's HTML structure
3. Run the scraper with the new configuration

## Development

### Setup Development Environment

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

MIT License 