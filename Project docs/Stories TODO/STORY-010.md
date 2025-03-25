# STORY-010: Universal Scraper Implementation

## Description
As a developer, I need to transform the current MCP-specific implementation into a truly universal documentation scraper that can work with different documentation sites through configuration, aligning with the DocHarvester name and project goals.

## Acceptance Criteria
- Rename all MCP-specific classes, files, and references to generic/universal equivalents
- Implement a simple plugin architecture for site-specific extractors
- Create a command-line interface that accepts a URL parameter
- Remove hardcoded "/docs" path assumptions
- Update the module structure to reflect the universal design
- Make the configuration system flexible for different site structures
- Enable automatic detection of documentation structure
- Ensure backwards compatibility with existing MCP functionality

## Technical Notes
- Refactor package structure from `mcp_doc_getter` to `docharvester`
- Create a simple plugin interface:
  ```python
  class DocSitePlugin:
      def __init__(self, config: Dict[str, Any]):
          self.config = config
      
      def can_handle(self, url: str) -> bool:
          """Determine if this plugin can handle the given URL"""
          pass
      
      def get_site_config(self) -> Dict[str, Any]:
          """Return all site-specific configuration in one place"""
          return {
              "selectors": self.get_content_selectors(),
              "rate_limits": self.get_rate_limits(),
              "auth": self.get_auth_requirements(),
              "structure": self.get_site_structure()
          }
      
      def process_page(self, html: str, url: str) -> Dict[str, Any]:
          """Process a single page and return structured content"""
          pass
  ```
- Use the simplified architecture components:
  - Configuration Manager for site settings
  - Plugin System for site-specific rules
  - Web Crawler for page discovery
  - Content Processor for extraction and conversion
  - Storage Manager for file operations
  - Monitoring Handler for metrics and logging

## Tasks
1. Refactor directory structure from `mcp_doc_getter` to `docharvester`
2. Update imports and references in all files
3. Create plugin architecture with base `DocSitePlugin` class
4. Implement plugin registration and discovery system
5. Refactor `main.py` to accept URL parameter and detect site structure
6. Move MCP-specific code to plugins directory
7. Create base classes for site-specific implementations
8. Implement automatic detection of documentation patterns
9. Update command-line interface for universal usage
10. Create generic configuration templates
11. Update tests to reflect new structure
12. Ensure backward compatibility

## Definition of Done
- Directory structure and imports reflect the universal design
- Command-line interface accepts URL parameter and site type
- MCP functionality works as a plugin
- Generic extractors handle common documentation patterns
- Plugin system allows easy addition of new site handlers
- All tests pass with the new architecture
- Documentation reflects the universal approach
- All components of the simplified architecture are properly integrated
- Configuration system supports multiple site types
- Error handling is consistent across all components 