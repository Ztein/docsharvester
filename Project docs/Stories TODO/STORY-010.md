# STORY-010: Universal Scraper Implementation

## Description
As a developer, I need to transform the current MCP-specific implementation into a truly universal documentation scraper that can work with different documentation sites through configuration, aligning with the DocHarvester name and project goals.

## Acceptance Criteria
- Rename all MCP-specific classes, files, and references to generic/universal equivalents
- Implement a plugin architecture for site-specific extractors
- Create a command-line interface that accepts a URL parameter
- Remove hardcoded "/docs" path assumptions
- Update the module structure to reflect the universal design
- Make the configuration system flexible for different site structures
- Enable automatic detection of documentation structure
- Ensure backwards compatibility with existing MCP functionality

## Technical Notes
- Refactor package structure from `mcp_doc_getter` to `docharvester`
- Create a plugin system for site-specific extractors and handlers
- Abstract site-specific logic into plugins
- Implement feature detection for documentation structure
- Design a flexible system for handling different URL patterns
- Ensure configuration supports various documentation site structures

## Tasks
1. Refactor directory structure from `mcp_doc_getter` to `docharvester`
2. Update imports and references in all files
3. Create plugin architecture for site-specific extractors
4. Refactor `main.py` to accept URL parameter and detect site structure
5. Move MCP-specific code to plugins directory
6. Create base classes for site-specific implementations
7. Implement automatic detection of documentation patterns
8. Update command-line interface for universal usage
9. Create generic configuration templates
10. Update tests to reflect new structure
11. Ensure backward compatibility

## Definition of Done
- Directory structure and imports reflect the universal design
- Command-line interface accepts URL parameter and site type
- MCP functionality works as a plugin
- Generic extractors handle common documentation patterns
- Plugin system allows easy addition of new site handlers
- All tests pass with the new architecture
- Documentation reflects the universal approach 