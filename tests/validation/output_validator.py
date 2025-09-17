
"""
Output validation framework for generated artifacts.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import re
from dataclasses import dataclass
from enum import Enum

class ValidationResult(Enum):
    """Validation result types."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"

@dataclass
class ValidationReport:
    """Validation report structure."""
    validator_name: str
    result: ValidationResult
    score: float
    message: str
    details: Dict[str, Any]
    cricket_score: Optional[float] = None

class OutputValidator:
    """Base class for output validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cricket_config = config.get("cricket_scoring", {})
    
    def validate(self, output_path: Path, expected_criteria: Dict[str, Any]) -> ValidationReport:
        """Validate output against criteria."""
        raise NotImplementedError("Subclasses must implement validate method")
    
    def calculate_cricket_score(self, score: float) -> float:
        """Calculate cricket score based on validation score."""
        if score >= 95:
            return self.cricket_config.get("boundary_6", 95)
        elif score >= 85:
            return self.cricket_config.get("boundary_4", 85)
        elif score >= 70:
            return self.cricket_config.get("wicket", 70)
        else:
            return max(0, score)

class DigitalTwinValidator(OutputValidator):
    """Validator for digital twin artifacts."""
    
    def validate(self, output_path: Path, expected_criteria: Dict[str, Any]) -> ValidationReport:
        """Validate digital twin output."""
        try:
            if not output_path.exists():
                return ValidationReport(
                    validator_name="DigitalTwinValidator",
                    result=ValidationResult.FAIL,
                    score=0.0,
                    message="Digital twin file not found",
                    details={"file_path": str(output_path)},
                    cricket_score=0.0
                )
            
            # Load and validate digital twin structure
            if output_path.suffix.lower() == '.json':
                with open(output_path, 'r', encoding='utf-8') as f:
                    digital_twin = json.load(f)
            elif output_path.suffix.lower() in ['.yml', '.yaml']:
                with open(output_path, 'r', encoding='utf-8') as f:
                    digital_twin = yaml.safe_load(f)
            else:
                return ValidationReport(
                    validator_name="DigitalTwinValidator",
                    result=ValidationResult.FAIL,
                    score=0.0,
                    message="Unsupported digital twin format",
                    details={"format": output_path.suffix},
                    cricket_score=0.0
                )
            
            # Validate required fields
            required_fields = expected_criteria.get("required_fields", [
                "document_id", "metadata", "structure", "content"
            ])
            
            missing_fields = []
            for field in required_fields:
                if field not in digital_twin:
                    missing_fields.append(field)
            
            # Calculate validation score
            field_score = (len(required_fields) - len(missing_fields)) / len(required_fields) * 100
            
            # Validate metadata completeness
            metadata_score = self._validate_metadata(
                digital_twin.get("metadata", {}),
                expected_criteria.get("metadata_requirements", {})
            )
            
            # Validate structure integrity
            structure_score = self._validate_structure(
                digital_twin.get("structure", {}),
                expected_criteria.get("structure_requirements", {})
            )
            
            # Calculate overall score
            overall_score = (field_score + metadata_score + structure_score) / 3
            cricket_score = self.calculate_cricket_score(overall_score)
            
            result = ValidationResult.PASS if overall_score >= 70 else ValidationResult.FAIL
            if 70 <= overall_score < 85:
                result = ValidationResult.WARNING
            
            return ValidationReport(
                validator_name="DigitalTwinValidator",
                result=result,
                score=overall_score,
                message=f"Digital twin validation completed with score {overall_score:.1f}",
                details={
                    "missing_fields": missing_fields,
                    "field_score": field_score,
                    "metadata_score": metadata_score,
                    "structure_score": structure_score,
                    "file_size": output_path.stat().st_size
                },
                cricket_score=cricket_score
            )
            
        except Exception as e:
            return ValidationReport(
                validator_name="DigitalTwinValidator",
                result=ValidationResult.FAIL,
                score=0.0,
                message=f"Validation error: {str(e)}",
                details={"error": str(e)},
                cricket_score=0.0
            )
    
    def _validate_metadata(self, metadata: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """Validate metadata completeness."""
        if not requirements:
            return 100.0
        
        required_keys = requirements.get("required_keys", [])
        if not required_keys:
            return 100.0
        
        present_keys = [key for key in required_keys if key in metadata]
        return (len(present_keys) / len(required_keys)) * 100
    
    def _validate_structure(self, structure: Dict[str, Any], requirements: Dict[str, Any]) -> float:
        """Validate structure integrity."""
        if not requirements:
            return 100.0
        
        # Check for required structure elements
        required_elements = requirements.get("required_elements", [])
        if not required_elements:
            return 100.0
        
        present_elements = [elem for elem in required_elements if elem in structure]
        return (len(present_elements) / len(required_elements)) * 100

class MetadataValidator(OutputValidator):
    """Validator for metadata artifacts."""
    
    def validate(self, output_path: Path, expected_criteria: Dict[str, Any]) -> ValidationReport:
        """Validate metadata output."""
        try:
            if not output_path.exists():
                return ValidationReport(
                    validator_name="MetadataValidator",
                    result=ValidationResult.FAIL,
                    score=0.0,
                    message="Metadata file not found",
                    details={"file_path": str(output_path)},
                    cricket_score=0.0
                )
            
            # Load metadata
            with open(output_path, 'r', encoding='utf-8') as f:
                if output_path.suffix.lower() == '.json':
                    metadata = json.load(f)
                elif output_path.suffix.lower() in ['.yml', '.yaml']:
                    metadata = yaml.safe_load(f)
                else:
                    # Assume text-based metadata
                    content = f.read()
                    metadata = {"content": content, "size": len(content)}
            
            # Validate metadata schema
            schema_score = self._validate_schema(metadata, expected_criteria.get("schema", {}))
            
            # Validate data quality
            quality_score = self._validate_data_quality(metadata, expected_criteria.get("quality", {}))
            
            # Validate completeness
            completeness_score = self._validate_completeness(metadata, expected_criteria.get("completeness", {}))
            
            # Calculate overall score
            overall_score = (schema_score + quality_score + completeness_score) / 3
            cricket_score = self.calculate_cricket_score(overall_score)
            
            result = ValidationResult.PASS if overall_score >= 70 else ValidationResult.FAIL
            if 70 <= overall_score < 85:
                result = ValidationResult.WARNING
            
            return ValidationReport(
                validator_name="MetadataValidator",
                result=result,
                score=overall_score,
                message=f"Metadata validation completed with score {overall_score:.1f}",
                details={
                    "schema_score": schema_score,
                    "quality_score": quality_score,
                    "completeness_score": completeness_score,
                    "metadata_keys": list(metadata.keys()) if isinstance(metadata, dict) else []
                },
                cricket_score=cricket_score
            )
            
        except Exception as e:
            return ValidationReport(
                validator_name="MetadataValidator",
                result=ValidationResult.FAIL,
                score=0.0,
                message=f"Metadata validation error: {str(e)}",
                details={"error": str(e)},
                cricket_score=0.0
            )
    
    def _validate_schema(self, metadata: Dict[str, Any], schema_requirements: Dict[str, Any]) -> float:
        """Validate metadata schema."""
        if not schema_requirements:
            return 100.0
        
        required_fields = schema_requirements.get("required_fields", [])
        if not required_fields:
            return 100.0
        
        if not isinstance(metadata, dict):
            return 0.0
        
        present_fields = [field for field in required_fields if field in metadata]
        return (len(present_fields) / len(required_fields)) * 100
    
    def _validate_data_quality(self, metadata: Dict[str, Any], quality_requirements: Dict[str, Any]) -> float:
        """Validate data quality."""
        if not quality_requirements:
            return 100.0
        
        # Check for non-empty values
        non_empty_check = quality_requirements.get("non_empty_values", False)
        if non_empty_check and isinstance(metadata, dict):
            empty_values = [k for k, v in metadata.items() if not v]
            if empty_values:
                return max(0, 100 - len(empty_values) * 10)
        
        return 100.0
    
    def _validate_completeness(self, metadata: Dict[str, Any], completeness_requirements: Dict[str, Any]) -> float:
        """Validate metadata completeness."""
        if not completeness_requirements:
            return 100.0
        
        min_fields = completeness_requirements.get("min_fields", 0)
        if isinstance(metadata, dict) and len(metadata) < min_fields:
            return (len(metadata) / min_fields) * 100
        
        return 100.0

class TemplateConformityValidator(OutputValidator):
    """Validator for template conformity."""
    
    def validate(self, output_path: Path, expected_criteria: Dict[str, Any]) -> ValidationReport:
        """Validate template conformity."""
        try:
            if not output_path.exists():
                return ValidationReport(
                    validator_name="TemplateConformityValidator",
                    result=ValidationResult.FAIL,
                    score=0.0,
                    message="Output file not found",
                    details={"file_path": str(output_path)},
                    cricket_score=0.0
                )
            
            # Read output content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate format conformity
            format_score = self._validate_format(content, expected_criteria.get("format", {}))
            
            # Validate structure conformity
            structure_score = self._validate_template_structure(content, expected_criteria.get("structure", {}))
            
            # Validate content requirements
            content_score = self._validate_content_requirements(content, expected_criteria.get("content", {}))
            
            # Calculate overall score
            overall_score = (format_score + structure_score + content_score) / 3
            cricket_score = self.calculate_cricket_score(overall_score)
            
            result = ValidationResult.PASS if overall_score >= 70 else ValidationResult.FAIL
            if 70 <= overall_score < 85:
                result = ValidationResult.WARNING
            
            return ValidationReport(
                validator_name="TemplateConformityValidator",
                result=result,
                score=overall_score,
                message=f"Template conformity validation completed with score {overall_score:.1f}",
                details={
                    "format_score": format_score,
                    "structure_score": structure_score,
                    "content_score": content_score,
                    "content_length": len(content)
                },
                cricket_score=cricket_score
            )
            
        except Exception as e:
            return ValidationReport(
                validator_name="TemplateConformityValidator",
                result=ValidationResult.FAIL,
                score=0.0,
                message=f"Template validation error: {str(e)}",
                details={"error": str(e)},
                cricket_score=0.0
            )
    
    def _validate_format(self, content: str, format_requirements: Dict[str, Any]) -> float:
        """Validate format requirements."""
        if not format_requirements:
            return 100.0
        
        score = 100.0
        
        # Check required patterns
        required_patterns = format_requirements.get("required_patterns", [])
        for pattern in required_patterns:
            if not re.search(pattern, content):
                score -= 20
        
        # Check forbidden patterns
        forbidden_patterns = format_requirements.get("forbidden_patterns", [])
        for pattern in forbidden_patterns:
            if re.search(pattern, content):
                score -= 15
        
        return max(0, score)
    
    def _validate_template_structure(self, content: str, structure_requirements: Dict[str, Any]) -> float:
        """Validate template structure."""
        if not structure_requirements:
            return 100.0
        
        score = 100.0
        
        # Check required sections
        required_sections = structure_requirements.get("required_sections", [])
        for section in required_sections:
            if section.lower() not in content.lower():
                score -= 25
        
        return max(0, score)
    
    def _validate_content_requirements(self, content: str, content_requirements: Dict[str, Any]) -> float:
        """Validate content requirements."""
        if not content_requirements:
            return 100.0
        
        score = 100.0
        
        # Check minimum length
        min_length = content_requirements.get("min_length", 0)
        if len(content) < min_length:
            score -= 30
        
        # Check required keywords
        required_keywords = content_requirements.get("required_keywords", [])
        for keyword in required_keywords:
            if keyword.lower() not in content.lower():
                score -= 10
        
        return max(0, score)

class QualityGateValidator(OutputValidator):
    """Validator for quality gates."""
    
    def validate(self, output_path: Path, expected_criteria: Dict[str, Any]) -> ValidationReport:
        """Validate quality gates."""
        try:
            # Aggregate validation from multiple validators
            validators = [
                DigitalTwinValidator(self.config),
                MetadataValidator(self.config),
                TemplateConformityValidator(self.config)
            ]
            
            validation_results = []
            total_score = 0.0
            
            for validator in validators:
                try:
                    result = validator.validate(output_path, expected_criteria)
                    validation_results.append(result)
                    total_score += result.score
                except Exception as e:
                    # Skip failed validators but log the error
                    validation_results.append(ValidationReport(
                        validator_name=validator.__class__.__name__,
                        result=ValidationResult.SKIP,
                        score=0.0,
                        message=f"Validator skipped due to error: {str(e)}",
                        details={"error": str(e)},
                        cricket_score=0.0
                    ))
            
            # Calculate overall quality gate score
            valid_results = [r for r in validation_results if r.result != ValidationResult.SKIP]
            if valid_results:
                overall_score = sum(r.score for r in valid_results) / len(valid_results)
            else:
                overall_score = 0.0
            
            cricket_score = self.calculate_cricket_score(overall_score)
            
            # Determine quality gate result
            quality_threshold = expected_criteria.get("quality_threshold", 80)
            result = ValidationResult.PASS if overall_score >= quality_threshold else ValidationResult.FAIL
            
            return ValidationReport(
                validator_name="QualityGateValidator",
                result=result,
                score=overall_score,
                message=f"Quality gate validation completed with score {overall_score:.1f}",
                details={
                    "individual_results": [
                        {
                            "validator": r.validator_name,
                            "result": r.result.value,
                            "score": r.score,
                            "cricket_score": r.cricket_score
                        }
                        for r in validation_results
                    ],
                    "quality_threshold": quality_threshold,
                    "passed_quality_gate": overall_score >= quality_threshold
                },
                cricket_score=cricket_score
            )
            
        except Exception as e:
            return ValidationReport(
                validator_name="QualityGateValidator",
                result=ValidationResult.FAIL,
                score=0.0,
                message=f"Quality gate validation error: {str(e)}",
                details={"error": str(e)},
                cricket_score=0.0
            )
