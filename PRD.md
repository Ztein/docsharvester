I'll update the PRD to make it more general, focusing on a flexible approach that works with various documentation sites, starting with a single URL.

# Product Requirements Document (PRD)

## Project: DocHarvester - Universal Documentation Scraper

### 1. Project Overview

#### 1.1 Purpose
Develop a flexible Python-based documentation scraper that can download technical documentation from any website starting from a single URL, convert it to Markdown format, and store it locally for offline use with AI coding assistants like Cursor or Claude Code.

#### 1.2 Goals
- Create a universal documentation scraper that works with minimal configuration
- Enable users to start with just a single URL and extract all related documentation
- Convert HTML documentation to well-formatted Markdown
- Maintain navigation structure and link integrity
- Require minimal site-specific configuration
- Support immediate use cases (ModelContextProtocol.io and Pydantic AI)
- Facilitate "vibe coding" by making documentation available offline

### 2. Functional Requirements

#### 2.1 Core Functionality
- **URL-based Initialization**: Start crawling from a single user-provided URL
- **Intelligent Crawling**: Automatically detect and follow documentation links within the same domain
- **Boundary Detection**: Intelligently determine the boundaries of documentation content
- **Content Extraction**: Identify and extract meaningful documentation text
- **Markdown Conversion**: Convert HTML content to clean Markdown while preserving:
  - Headers and section structure
  - Code blocks and syntax highlighting
  - Tables
  - Lists (ordered and unordered)
  - Images (with appropriate references)
  - Links (both internal and external)
- **File Storage**: Save content to disk using a sensible naming convention derived from page titles or URLs
- **Minimal Configuration**: Work out-of-the-box with reasonable defaults

#### 2.2 File Organization
- Create a target directory named after the documentation source (configurable)
- Generate filenames based on page titles or URL paths
- Convert filenames to a consistent format (e.g., uppercase with underscores)
- Create subdirectories that reflect the website's structure when appropriate
- Include a metadata file that maps original URLs to local files

#### 2.3 Link Handling
- Preserve all external links as-is
- Convert internal links to relative paths that work locally
- Handle anchor links appropriately
- Create a link map for troubleshooting

#### 2.4 Error Handling
- Implement robust error handling for network issues
- Log all errors and warnings
- Skip problematic pages with appropriate notifications
- Resume capability if the process is interrupted

### 3. Technical Specifications

#### 3.1 Technology Stack
- Python 3.9+
- UV package manager for dependency management
- Libraries:
  - BeautifulSoup4 or similar for HTML parsing
  - Requests or httpx for HTTP requests
  - Markdown or html2text for HTML to Markdown conversion
  - PyYAML for optional configuration

#### 3.2 Architecture
- Modular design with separate components for:
  - Web crawling and discovery
  - Content extraction
  - Markdown conversion
  - File I/O operations
- Plugin system for site-specific customizations
- Command-line interface with appropriate options

#### 3.3 Performance Requirements
- Respect website's robots.txt
- Implement rate limiting to avoid overloading servers
- Parallel processing with configurable concurrency limits
- Caching mechanism to avoid redundant downloads
- Support for resuming interrupted operations

### 4. User Interface

#### 4.1 Command Line Interface
```
docsharvester crawl https://modelcontextprotocol.io/ --output-dir MCP_DOCS
docsharvester crawl https://docs.pydantic.ai/ --output-dir PYDANTIC_DOCS
```

#### 4.2 Configuration Options
- URL to start crawling from
- Output directory name
- Depth limit (how many links to follow)
- Domain restrictions (stay within specific subdomains)
- Concurrency settings
- File naming patterns (optional)
- Custom content selectors (optional)

### 5. Implementation Plan

#### 5.1 Project Setup
1. Initialize Git repository
2. Set up virtual environment using UV
3. Create project structure
4. Add initial documentation

#### 5.2 Development Phases
1. **Phase 1: Core Engine**
   - Implement base crawler with URL-based initialization
   - Create content detection and extraction logic
   - Build Markdown converter
   - Develop file system handler

2. **Phase 2: Intelligent Features**
   - Implement boundary detection
   - Add link conversion logic
   - Create metadata tracking
   - Build resumption capability

3. **Phase 3: Testing with Target Sites**
   - Test with ModelContextProtocol.io
   - Test with Pydantic AI documentation
   - Fine-tune general algorithms based on findings
   - Implement minimal site-specific adjustments if needed

4. **Phase 4: Refinement**
   - Improve error handling
   - Optimize performance
   - Add command-line interface polish
   - Create comprehensive documentation

### 6. Customization Capabilities

#### 6.1 Optional Configuration
Allow for site-specific configuration through YAML files that can specify:
- CSS selectors for main content
- Patterns to include/exclude URLs
- Special handling for particular content types
- Custom filename patterns

#### 6.2 Plugin System
Design a simple plugin architecture that allows for:
- Site-specific content extraction rules
- Custom post-processing of Markdown
- Special handling for specific documentation systems

### 7. Deliverables

- Fully functional Python package
- GitHub repository with complete documentation
- Command-line interface for easy usage
- Sample configurations for ModelContextProtocol.io and Pydantic AI
- Comprehensive README with usage instructions
- Contribution guidelines for extending functionality

### 8. Success Criteria

- Successfully crawl and extract documentation from ModelContextProtocol.io and Pydantic AI
- Generate well-formatted Markdown files that preserve the original content's meaning and structure
- Create a sensible file hierarchy that reflects the documentation's organization
- Require minimal configuration for new documentation sites
- Maintain working links between downloaded files

### 9. Future Enhancements

- Web interface for monitoring and configuration
- Auto-update feature to refresh documentation
- Diff-based updates to only download changed content
- Integration with search tools for local documentation
- Direct integration with AI coding assistants
- Support for authentication-protected documentation sites
- Extraction of interactive elements as static examples

This PRD outlines a flexible, user-friendly tool that starts with a simple URL and intelligently extracts documentation into a format ideal for offline use and AI-assisted development.