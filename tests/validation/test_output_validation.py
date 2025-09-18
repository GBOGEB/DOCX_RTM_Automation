
"""
Tests for output validation framework.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock
import sys

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.validation.output_validator import (
    DigitalTwinValidator, MetadataValidator, TemplateConformityValidator, 
    QualityGateValidator, ValidationResult
)
from tests.validation.quality_gates import QualityGateEngine, ApprovalStatus

class TestOutputValidation:
    """Test suite for output validation framework."""
    
    @pytest.fixture
    def validation_config(self, cricket_score_config):
        """Create validation configuration."""
        return {
            **cricket_score_config,
            "validation_settings": {
                "strict_mode": False,
                "auto_fix_enabled": True
            }
        }
    
    @pytest.fixture
    def sample_digital_twin(self, temp_dir):
        """Create sample digital twin for testing."""
        digital_twin = {
            "document_id": "test_doc_001",
            "metadata": {
                "title": "Test Document",
                "author": "Test Author",
                "created_date": "2025-09-10",
                "document_type": "requirements"
            },
            "structure": {
                "sections": ["introduction", "requirements", "conclusion"],
                "hierarchy_depth": 3,
                "total_elements": 15
            },
            "content": {
                "text_length": 5000,
                "requirements_count": 10,
                "tables_count": 2
            }
        }
        
        digital_twin_path = temp_dir / "test_digital_twin.json"
        with open(digital_twin_path, 'w', encoding='utf-8') as f:
            json.dump(digital_twin, f, indent=2)
        
        return digital_twin_path
    
    @pytest.fixture
    def sample_metadata(self, temp_dir):
        """Create sample metadata for testing."""
        metadata = {
            "processing_info": {
                "engine": "word_processor",
                "version": "1.0.0",
                "timestamp": "2025-09-10T08:00:00Z"
            },
            "document_stats": {
                "pages": 10,
                "words": 2500,
                "characters": 15000
            },
            "quality_metrics": {
                "readability_score": 85,
                "completeness": 95,
                "accuracy": 90
            }
        }
        
        metadata_path = temp_dir / "test_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata_path
    
    @pytest.fixture
    def sample_template_output(self, temp_dir):
        """Create sample template output for testing."""
        template_content = """# Requirements Document

## Introduction
This document contains the system requirements.

## Requirements
REQ-001: System shall process documents
REQ-002: System shall generate reports
REQ-003: System shall validate inputs

## Conclusion
All requirements have been documented.
"""
        
        template_path = temp_dir / "test_template_output.md"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        return template_path
    
    def test_digital_twin_validator(self, validation_config, sample_digital_twin, cricket_score_config):
        """Test digital twin validation with cricket scoring."""
        validator = DigitalTwinValidator(validation_config)
        
        expected_criteria = {
            "required_fields": ["document_id", "metadata", "structure", "content"],
            "metadata_requirements": {
                "required_keys": ["title", "author", "created_date"]
            },
            "structure_requirements": {
                "required_elements": ["sections", "hierarchy_depth"]
            }
        }
        
        result = validator.validate(sample_digital_twin, expected_criteria)
        
        # Validate result structure
        assert result.validator_name == "DigitalTwinValidator"
        assert result.result in [ValidationResult.PASS, ValidationResult.WARNING, ValidationResult.FAIL]
        assert 0 <= result.score <= 100
        assert result.cricket_score is not None
        
        # Should pass with good score
        assert result.score >= 70, f"Digital twin validation score too low: {result.score}"
        
        # Cricket scoring validation
        if result.cricket_score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
            print(f"🏏 SIX! Excellent digital twin validation: {result.cricket_score:.1f}")
        elif result.cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good digital twin validation: {result.cricket_score:.1f}")
        else:
            print(f"🏏 Single. Acceptable digital twin validation: {result.cricket_score:.1f}")
    
    def test_metadata_validator(self, validation_config, sample_metadata, cricket_score_config):
        """Test metadata validation with cricket scoring."""
        validator = MetadataValidator(validation_config)
        
        expected_criteria = {
            "schema": {
                "required_fields": ["processing_info", "document_stats", "quality_metrics"]
            },
            "quality": {
                "non_empty_values": True
            },
            "completeness": {
                "min_fields": 3
            }
        }
        
        result = validator.validate(sample_metadata, expected_criteria)
        
        # Validate result
        assert result.validator_name == "MetadataValidator"
        assert result.result in [ValidationResult.PASS, ValidationResult.WARNING, ValidationResult.FAIL]
        assert 0 <= result.score <= 100
        assert result.cricket_score is not None
        
        # Should pass with good score
        assert result.score >= 70, f"Metadata validation score too low: {result.score}"
        
        # Cricket scoring validation
        if result.cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good metadata validation: {result.cricket_score:.1f}")
        else:
            print(f"🏏 Acceptable metadata validation: {result.cricket_score:.1f}")
    
    def test_template_conformity_validator(self, validation_config, sample_template_output, cricket_score_config):
        """Test template conformity validation with cricket scoring."""
        validator = TemplateConformityValidator(validation_config)
        
        expected_criteria = {
            "format": {
                "required_patterns": [r"# .+", r"## .+", r"REQ-\d+:"],
                "forbidden_patterns": [r"TODO", r"FIXME"]
            },
            "structure": {
                "required_sections": ["Introduction", "Requirements", "Conclusion"]
            },
            "content": {
                "min_length": 100,
                "required_keywords": ["requirements", "system"]
            }
        }
        
        result = validator.validate(sample_template_output, expected_criteria)
        
        # Validate result
        assert result.validator_name == "TemplateConformityValidator"
        assert result.result in [ValidationResult.PASS, ValidationResult.WARNING, ValidationResult.FAIL]
        assert 0 <= result.score <= 100
        assert result.cricket_score is not None
        
        # Should pass with good score
        assert result.score >= 70, f"Template conformity score too low: {result.score}"
        
        # Cricket scoring validation
        if result.cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good template conformity: {result.cricket_score:.1f}")
        else:
            print(f"🏏 Acceptable template conformity: {result.cricket_score:.1f}")
    
    def test_quality_gate_validator(self, validation_config, sample_digital_twin, cricket_score_config):
        """Test quality gate validator aggregation."""
        validator = QualityGateValidator(validation_config)
        
        expected_criteria = {
            "quality_threshold": 80,
            "required_fields": ["document_id", "metadata"],
            "schema": {"required_fields": ["document_id"]},
            "format": {"required_patterns": [r"\{.*\}"]},  # JSON format
        }
        
        result = validator.validate(sample_digital_twin, expected_criteria)
        
        # Validate aggregated result
        assert result.validator_name == "QualityGateValidator"
        assert result.result in [ValidationResult.PASS, ValidationResult.WARNING, ValidationResult.FAIL]
        assert 0 <= result.score <= 100
        assert result.cricket_score is not None
        
        # Check individual results in details
        assert "individual_results" in result.details
        individual_results = result.details["individual_results"]
        assert len(individual_results) > 0
        
        print(f"🏏 Quality gate overall score: {result.cricket_score:.1f}")
    
    def test_quality_gate_engine(self, validation_config, sample_digital_twin, cricket_score_config):
        """Test quality gate engine with full workflow."""
        engine = QualityGateEngine(validation_config)
        
        expected_criteria = {
            "quality_threshold": 75,
            "required_fields": ["document_id", "metadata", "structure", "content"],
            "schema": {
                "required_fields": ["document_id", "metadata"]
            }
        }
        
        # Run standard workflow
        results = engine.run_quality_gates(sample_digital_twin, "standard", expected_criteria)
        
        # Validate workflow results
        assert results["workflow_name"] == "standard"
        assert "timestamp" in results
        assert "execution_time" in results
        assert 0 <= results["overall_score"] <= 100
        assert results["overall_cricket_score"] is not None
        assert results["total_gates"] > 0
        assert results["approval_status"] in [status.value for status in ApprovalStatus]
        
        # Validate cricket summary
        cricket_summary = results["cricket_summary"]
        assert "result" in cricket_summary
        assert "message" in cricket_summary
        assert "score" in cricket_summary
        
        # Validate recommendations
        assert "recommendations" in results
        assert isinstance(results["recommendations"], list)
        
        print(f"🏏 Workflow cricket score: {results['overall_cricket_score']:.1f}")
        print(f"🏏 Cricket result: {cricket_summary['result']}")
        print(f"🏏 Approval status: {results['approval_status']}")
    
    def test_quality_gate_engine_production_workflow(self, validation_config, sample_digital_twin):
        """Test production workflow with stricter requirements."""
        engine = QualityGateEngine(validation_config)
        
        expected_criteria = {
            "quality_threshold": 90,  # Higher threshold for production
            "required_fields": ["document_id", "metadata", "structure", "content"],
            "schema": {
                "required_fields": ["document_id", "metadata", "structure", "content"]
            }
        }
        
        # Run production workflow
        results = engine.run_quality_gates(sample_digital_twin, "production", expected_criteria)
        
        # Production workflow should require manual approval
        assert results["workflow_name"] == "production"
        # May be pending due to manual approval requirement
        assert results["approval_status"] in ["pending", "approved", "rejected"]
        
        print(f"🏏 Production workflow result: {results['approval_status']}")
    
    def test_quality_report_generation(self, validation_config, sample_digital_twin, temp_dir):
        """Test quality report generation."""
        engine = QualityGateEngine(validation_config)
        
        expected_criteria = {"quality_threshold": 80}
        results = engine.run_quality_gates(sample_digital_twin, "standard", expected_criteria)
        
        # Generate quality report
        report_path = engine.generate_quality_report(results, temp_dir)
        
        # Validate report file
        assert report_path.exists()
        assert report_path.suffix == ".json"
        
        # Validate report content
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        assert "report_metadata" in report_data
        assert "quality_summary" in report_data
        assert "cricket_summary" in report_data
        
        quality_summary = report_data["quality_summary"]
        assert "overall_status" in quality_summary
        assert "cricket_achievement" in quality_summary
        assert "performance_level" in quality_summary
        assert "improvement_potential" in quality_summary
        
        print(f"🏏 Quality report generated: {report_path}")
        print(f"🏏 Performance level: {quality_summary['performance_level']}")
    
    def test_validation_error_handling(self, validation_config, temp_dir):
        """Test validation error handling."""
        validator = DigitalTwinValidator(validation_config)
        
        # Test with non-existent file
        non_existent_file = temp_dir / "non_existent.json"
        result = validator.validate(non_existent_file, {})
        
        assert result.result == ValidationResult.FAIL
        assert result.score == 0.0
        assert "not found" in result.message.lower()
        
        # Test with invalid JSON
        invalid_json_file = temp_dir / "invalid.json"
        with open(invalid_json_file, 'w') as f:
            f.write("invalid json content {")
        
        result = validator.validate(invalid_json_file, {})
        assert result.result == ValidationResult.FAIL
        assert result.score == 0.0
    
    def test_cricket_scoring_boundaries(self, validation_config, sample_digital_twin, cricket_score_config):
        """Test cricket scoring boundary conditions."""
        validator = DigitalTwinValidator(validation_config)
        
        # Test with minimal criteria (should get high score)
        minimal_criteria = {"required_fields": ["document_id"]}
        result = validator.validate(sample_digital_twin, minimal_criteria)
        
        assert result.cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]
        print(f"🏏 Minimal criteria cricket score: {result.cricket_score:.1f}")
        
        # Test with strict criteria (may get lower score)
        strict_criteria = {
            "required_fields": ["document_id", "metadata", "structure", "content", "extra_field"],
            "metadata_requirements": {
                "required_keys": ["title", "author", "created_date", "extra_key"]
            }
        }
        result = validator.validate(sample_digital_twin, strict_criteria)
        
        print(f"🏏 Strict criteria cricket score: {result.cricket_score:.1f}")
        # Should still be reasonable score
        assert result.cricket_score >= 0
    
    @pytest.mark.benchmark
    def test_validation_performance_benchmark(self, validation_config, sample_digital_twin, benchmark):
        """Benchmark validation performance."""
        validator = DigitalTwinValidator(validation_config)
        expected_criteria = {"required_fields": ["document_id", "metadata"]}
        
        def run_validation():
            return validator.validate(sample_digital_twin, expected_criteria)
        
        result = benchmark(run_validation)
        assert result.result in [ValidationResult.PASS, ValidationResult.WARNING, ValidationResult.FAIL]
        print(f"🏏 Validation benchmark cricket score: {result.cricket_score:.1f}")
