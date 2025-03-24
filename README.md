# DocHarvester

A Python-based web scraper that downloads and stores documentation from different sites like https://modelcontextprotocol.io or https://docs.pydantic.dev/latest/ into Markdown files for offline reference.

A versatile Python tool for scraping technical documentation websites and converting them to local Markdown files. DocHarvester makes offline documentation access seamless for developers who want to enhance their coding workflow with AI assistants like Cursor or Claude Code.

## 🌟 Features

- Download complete documentation from technical frameworks and libraries
- Convert HTML documentation to clean, well-formatted Markdown
- Preserve link structure, code blocks, tables, and other formatting
- Configurable for any documentation site with YAML-based configuration
- Built-in support for ModelContextProtocol.io and other AI frameworks
- Respects rate limits and robots.txt for ethical scraping
- Easily extensible to support new documentation sources

## 🚀 Use cases

- Create local documentation caches for offline development
- Build custom knowledge bases for AI coding assistants
- Generate reference material for team onboarding
- Archive documentation versions for backwards compatibility

## 🛠️ Built with

- Python 3.9+
- UV package manager
- BeautifulSoup4
- Rich for beautiful CLI output
- Configurable architecture using YAML

## Features

- Downloads complete documentation from various technical websites
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
   git clone https://github.com/yourusername/DocHarvester.git
   cd DocHarvester
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
docharvester
```

### Custom Configuration

Specify a custom configuration file:

```bash
docharvester --config path/to/config.yaml
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

## Testing

The project uses pytest for testing. To run the tests:

```bash
python -m pytest
```

For verbose output:

```bash
python -m pytest -v
```

To run tests for a specific component:

```bash
python -m pytest tests/component_name/
```

The test infrastructure is set up for test-driven development. Many tests are skipped because their components are not yet implemented. As you implement each component, update the tests to remove the `@unittest.skip` decorators and verify that the functionality works as expected.

Refer to the `tests/README.md` file for more information about the test structure and available fixtures.

## License

MIT License 