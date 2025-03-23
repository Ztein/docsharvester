"""
Configuration Manager for MCP Documentation Scraper

This module handles loading, validating, and providing access to configuration
values from YAML files.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """
    Manages configuration for the documentation scraper.
    
    Provides methods to load, validate, and access configuration
    values from YAML files.
    """
    
    def __init__(self, config_path: str) -> None:
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()
        self._validate_config()
    
    def _load_config(self) -> None:
        """
        Load configuration from the YAML file.
        
        Raises:
            FileNotFoundError: If the configuration file is not found
            yaml.YAMLError: If the configuration file cannot be parsed
        """
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
            logging.info(f"Loaded configuration from {self.config_path}")
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing configuration file: {e}")
            raise
    
    def _validate_config(self) -> None:
        """
        Validate the configuration.
        
        Ensures all required fields are present and have the correct types.
        
        Raises:
            ValueError: If the configuration is invalid
        """
        required_sections = ["site", "crawling", "extraction", "output"]
        for section in required_sections:
            if section not in self.config:
                msg = f"Missing required section in configuration: {section}"
                logging.error(msg)
                raise ValueError(msg)
        
        # Validate site section
        site = self.config["site"]
        if "name" not in site or "base_url" not in site:
            msg = "Site section must contain 'name' and 'base_url'"
            logging.error(msg)
            raise ValueError(msg)
        
        # Additional validation will be added as needed
        
        logging.info("Configuration validated successfully")
    
    def get(self, section: str, key: str, default: Optional[Any] = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            section: The configuration section
            key: The configuration key
            default: Default value if key is not found
            
        Returns:
            The configuration value, or the default if not found
        """
        if section not in self.config:
            return default
        
        section_dict = self.config[section]
        if key not in section_dict:
            return default
        
        return section_dict[key]
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section.
        
        Args:
            section: The configuration section
            
        Returns:
            The configuration section as a dictionary, or empty dict if not found
        """
        return self.config.get(section, {}) 