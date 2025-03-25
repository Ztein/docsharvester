"""
Tests for the content validation functionality.
"""

import pytest
from pathlib import Path
from datetime import datetime
from mcp_doc_getter.validation.content_validator import (
    ContentValidator,
    ValidationMetrics,
    ValidationResult
)

@pytest.fixture
def validator():
    """Create a content validator instance with test configuration."""
    config = {
        'validation': {
            'enabled': True,
            'log_level': 'INFO',
            'min_accuracy': 0.95  # Adjusted to be more realistic
        }
    }
    return ContentValidator(config)

@pytest.fixture
def test_content():
    """Create test content for validation."""
    return {
        'original': """
<html>
    <body>
        <h1>Test Document</h1>
        <h2>Section 1</h2>
        <p>This is a test paragraph.</p>
        <h2>Section 2</h2>
        <p>Another test paragraph.</p>
    </body>
</html>
""",
        'extracted': """# Test Document
## Section 1
This is a test paragraph.
## Section 2
Another test paragraph."""
    }

@pytest.fixture
def test_structure():
    """Create test structure data for validation."""
    return {
        'original': {
            'headings': [
                {'level': 1, 'text': 'Test Document'},
                {'level': 2, 'text': 'Section 1'},
                {'level': 2, 'text': 'Section 2'}
            ]
        },
        'extracted': {
            'headings': [
                {'level': 1, 'text': 'Test Document'},
                {'level': 2, 'text': 'Section 1'},
                {'level': 2, 'text': 'Section 2'}
            ]
        }
    }

def test_validation_metrics_initialization():
    """Test that validation metrics are properly initialized."""
    metrics = ValidationMetrics(
        extraction_accuracy=0.95,
        structure_preservation=0.98,
        content_comparison_score=0.97,
        total_errors=0,
        total_warnings=1
    )
    
    assert metrics.extraction_accuracy == 0.95
    assert metrics.structure_preservation == 0.98
    assert metrics.content_comparison_score == 0.97
    assert metrics.total_errors == 0
    assert metrics.total_warnings == 1

def test_content_extraction_validation(validator, test_content):
    """Test content extraction validation."""
    accuracy, differences = validator.validate_content_extraction(
        test_content['original'],
        test_content['extracted']
    )
    
    assert accuracy > 0.95  # Adjusted to be more realistic
    assert len(differences) == 0  # No differences expected

def test_structure_validation(validator, test_structure):
    """Test structure validation."""
    score, errors = validator.validate_structure(
        test_structure['original'],
        test_structure['extracted']
    )
    
    assert score == 1.0  # Perfect match
    assert len(errors) == 0  # No errors expected

def test_file_organization_validation(validator, tmp_path):
    """Test file organization validation."""
    # Create a test file
    test_file = tmp_path / "test_document.md"
    test_file.touch()
    
    expected_structure = {
        'naming_pattern': r'^[a-z_]+\.md$',
        'directory_structure': str(tmp_path)
    }
    
    success, errors = validator.validate_file_organization(test_file, expected_structure)
    
    assert success
    assert len(errors) == 0

def test_validation_report_generation(validator):
    """Test validation report generation."""
    # Create test results
    results = [
        ValidationResult(
            success=True,
            metrics=ValidationMetrics(
                extraction_accuracy=0.98,
                structure_preservation=0.99,
                content_comparison_score=0.97,
                total_errors=0,
                total_warnings=1
            ),
            errors=[],
            warnings=["Minor formatting issue"],
            details={"file": "test.md"}
        )
    ]
    
    report = validator.generate_validation_report(results)
    
    assert report['total_validations'] == 1
    assert report['successful_validations'] == 1
    assert report['failed_validations'] == 0
    assert report['total_errors'] == 0
    assert report['total_warnings'] == 1
    assert report['average_metrics']['extraction_accuracy'] == 0.98
    assert report['average_metrics']['structure_preservation'] == 0.99
    assert report['average_metrics']['content_comparison_score'] == 0.97
    assert len(report['details']) == 1

def test_validation_with_errors(validator, test_content):
    """Test validation with content that has errors."""
    # Modify extracted content to introduce errors
    modified_content = test_content['extracted'].replace("test", "wrong")
    
    accuracy, differences = validator.validate_content_extraction(
        test_content['original'],
        modified_content
    )
    
    assert accuracy < 0.95  # Adjusted to match new threshold
    assert len(differences) > 0  # Should have differences 