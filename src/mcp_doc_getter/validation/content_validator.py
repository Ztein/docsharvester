"""
Content validation module for MCP Documentation Scraper.

This module provides functionality to validate content extraction, structure,
and conversion accuracy.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import difflib
import json
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@dataclass
class ValidationMetrics:
    """Metrics collected during content validation."""
    extraction_accuracy: float
    structure_preservation: float
    content_comparison_score: float
    total_errors: int
    total_warnings: int

@dataclass
class ValidationResult:
    """Results from content validation."""
    success: bool
    metrics: ValidationMetrics
    errors: List[str]
    warnings: List[str]
    details: Dict[str, any]

class ContentValidator:
    """Main class for content validation."""
    
    def __init__(self, config: Dict):
        """Initialize the content validator with configuration."""
        self.config = config
        self.metrics = ValidationMetrics(
            extraction_accuracy=0.0,
            structure_preservation=0.0,
            content_comparison_score=0.0,
            total_errors=0,
            total_warnings=0
        )
    
    def _normalize_content(self, content: str) -> str:
        """
        Normalize content for comparison by removing whitespace, HTML tags,
        and Markdown formatting.
        
        Args:
            content: The content to normalize
            
        Returns:
            Normalized content string
        """
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove Markdown heading markers
        content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def validate_content_extraction(self, original_content: str, extracted_content: str) -> Tuple[float, List[str]]:
        """
        Validate the accuracy of content extraction.
        
        Args:
            original_content: The original HTML content
            extracted_content: The extracted content
            
        Returns:
            Tuple of (accuracy_score, error_messages)
        """
        # Normalize both contents
        orig_normalized = self._normalize_content(original_content)
        ext_normalized = self._normalize_content(extracted_content)
        
        # Calculate similarity using difflib
        matcher = difflib.SequenceMatcher(None, orig_normalized, ext_normalized)
        accuracy = matcher.ratio()
        
        # Generate detailed differences
        differences = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                differences.append(f"{tag}: {orig_normalized[i1:i2]} -> {ext_normalized[j1:j2]}")
        
        return accuracy, differences
    
    def validate_structure(self, original_structure: Dict, extracted_structure: Dict) -> Tuple[float, List[str]]:
        """
        Validate the preservation of content structure.
        
        Args:
            original_structure: Dictionary representing original content structure
            extracted_structure: Dictionary representing extracted content structure
            
        Returns:
            Tuple of (structure_score, error_messages)
        """
        # Compare structure elements
        structure_errors = []
        score = 0.0
        
        # Compare headings hierarchy
        if 'headings' in original_structure and 'headings' in extracted_structure:
            orig_headings = original_structure['headings']
            ext_headings = extracted_structure['headings']
            
            if len(orig_headings) != len(ext_headings):
                structure_errors.append(f"Heading count mismatch: {len(orig_headings)} vs {len(ext_headings)}")
            else:
                for i, (orig, ext) in enumerate(zip(orig_headings, ext_headings)):
                    if orig['level'] != ext['level']:
                        structure_errors.append(f"Heading level mismatch at position {i}")
                    if orig['text'] != ext['text']:
                        structure_errors.append(f"Heading text mismatch at position {i}")
        
        # Calculate structure score
        if not structure_errors:
            score = 1.0
        else:
            score = 1.0 - (len(structure_errors) / max(len(orig_headings), len(ext_headings)))
        
        return score, structure_errors
    
    def validate_file_organization(self, file_path: Path, expected_structure: Dict) -> Tuple[bool, List[str]]:
        """
        Validate file naming and organization.
        
        Args:
            file_path: Path to the file being validated
            expected_structure: Dictionary containing expected file organization rules
            
        Returns:
            Tuple of (success, error_messages)
        """
        errors = []
        
        # Validate file naming convention
        if 'naming_pattern' in expected_structure:
            import re
            pattern = re.compile(expected_structure['naming_pattern'])
            if not pattern.match(file_path.name):
                errors.append(f"File name does not match pattern: {file_path.name}")
        
        # Validate directory structure
        if 'directory_structure' in expected_structure:
            expected_path = Path(expected_structure['directory_structure'])
            if not str(file_path.parent).startswith(str(expected_path)):
                errors.append(f"File location does not match expected structure")
        
        return len(errors) == 0, errors
    
    def generate_validation_report(self, results: List[ValidationResult]) -> Dict:
        """
        Generate a validation report from multiple validation results.
        
        Args:
            results: List of validation results
            
        Returns:
            Dictionary containing the validation report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_validations': len(results),
            'successful_validations': sum(1 for r in results if r.success),
            'failed_validations': sum(1 for r in results if not r.success),
            'total_errors': sum(len(r.errors) for r in results),
            'total_warnings': sum(len(r.warnings) for r in results),
            'average_metrics': {
                'extraction_accuracy': sum(r.metrics.extraction_accuracy for r in results) / len(results),
                'structure_preservation': sum(r.metrics.structure_preservation for r in results) / len(results),
                'content_comparison_score': sum(r.metrics.content_comparison_score for r in results) / len(results)
            },
            'details': [r.details for r in results]
        }
        
        return report 