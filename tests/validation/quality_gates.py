
"""
Quality gates and approval workflows for CI/CD pipeline.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import time
from datetime import datetime

from .output_validator import (
    OutputValidator, ValidationReport, ValidationResult,
    DigitalTwinValidator, MetadataValidator, TemplateConformityValidator, QualityGateValidator
)

class ApprovalStatus(Enum):
    """Approval status types."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"

@dataclass
class QualityGate:
    """Quality gate definition."""
    name: str
    description: str
    validators: List[str]
    threshold: float
    auto_approve_threshold: float
    required: bool = True
    cricket_scoring: bool = True

@dataclass
class ApprovalWorkflow:
    """Approval workflow definition."""
    name: str
    quality_gates: List[QualityGate]
    auto_approval_enabled: bool = True
    manual_approval_required: bool = False
    notification_enabled: bool = True

class QualityGateEngine:
    """Engine for managing quality gates and approval workflows."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cricket_config = config.get("cricket_scoring", {})
        self.quality_gates = self._load_quality_gates()
        self.workflows = self._load_workflows()
        self.validators = self._initialize_validators()
    
    def _load_quality_gates(self) -> Dict[str, QualityGate]:
        """Load quality gate definitions."""
        gates = {}
        
        # Default quality gates
        gates["digital_twin_quality"] = QualityGate(
            name="digital_twin_quality",
            description="Validate digital twin artifact quality",
            validators=["DigitalTwinValidator"],
            threshold=80.0,
            auto_approve_threshold=90.0,
            cricket_scoring=True
        )
        
        gates["metadata_completeness"] = QualityGate(
            name="metadata_completeness",
            description="Validate metadata completeness and quality",
            validators=["MetadataValidator"],
            threshold=85.0,
            auto_approve_threshold=95.0,
            cricket_scoring=True
        )
        
        gates["template_conformity"] = QualityGate(
            name="template_conformity",
            description="Validate template conformity and structure",
            validators=["TemplateConformityValidator"],
            threshold=75.0,
            auto_approve_threshold=90.0,
            cricket_scoring=True
        )
        
        gates["overall_quality"] = QualityGate(
            name="overall_quality",
            description="Overall quality assessment",
            validators=["QualityGateValidator"],
            threshold=80.0,
            auto_approve_threshold=95.0,
            required=True,
            cricket_scoring=True
        )
        
        return gates
    
    def _load_workflows(self) -> Dict[str, ApprovalWorkflow]:
        """Load approval workflow definitions."""
        workflows = {}
        
        # Default workflow
        workflows["standard"] = ApprovalWorkflow(
            name="standard",
            quality_gates=[
                self.quality_gates["digital_twin_quality"],
                self.quality_gates["metadata_completeness"],
                self.quality_gates["template_conformity"],
                self.quality_gates["overall_quality"]
            ],
            auto_approval_enabled=True,
            manual_approval_required=False,
            notification_enabled=True
        )
        
        # Strict workflow for production
        workflows["production"] = ApprovalWorkflow(
            name="production",
            quality_gates=[
                self.quality_gates["digital_twin_quality"],
                self.quality_gates["metadata_completeness"],
                self.quality_gates["template_conformity"],
                self.quality_gates["overall_quality"]
            ],
            auto_approval_enabled=False,
            manual_approval_required=True,
            notification_enabled=True
        )
        
        return workflows
    
    def _initialize_validators(self) -> Dict[str, OutputValidator]:
        """Initialize validators."""
        return {
            "DigitalTwinValidator": DigitalTwinValidator(self.config),
            "MetadataValidator": MetadataValidator(self.config),
            "TemplateConformityValidator": TemplateConformityValidator(self.config),
            "QualityGateValidator": QualityGateValidator(self.config)
        }
    
    def run_quality_gates(self, output_path: Path, workflow_name: str = "standard", 
                         expected_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run quality gates for given output."""
        if workflow_name not in self.workflows:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflows[workflow_name]
        if expected_criteria is None:
            expected_criteria = {}
        
        start_time = time.time()
        gate_results = []
        overall_cricket_scores = []
        
        # Run each quality gate
        for gate in workflow.quality_gates:
            gate_result = self._run_quality_gate(gate, output_path, expected_criteria)
            gate_results.append(gate_result)
            
            if gate_result.get("cricket_score") is not None:
                overall_cricket_scores.append(gate_result["cricket_score"])
        
        # Calculate overall results
        passed_gates = [r for r in gate_results if r["status"] == "passed"]
        failed_gates = [r for r in gate_results if r["status"] == "failed"]
        warning_gates = [r for r in gate_results if r["status"] == "warning"]
        
        overall_score = sum(r["score"] for r in gate_results) / len(gate_results) if gate_results else 0
        overall_cricket_score = sum(overall_cricket_scores) / len(overall_cricket_scores) if overall_cricket_scores else 0
        
        # Determine approval status
        approval_status = self._determine_approval_status(
            workflow, gate_results, overall_score, overall_cricket_score
        )
        
        end_time = time.time()
        
        return {
            "workflow_name": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "execution_time": end_time - start_time,
            "overall_score": overall_score,
            "overall_cricket_score": overall_cricket_score,
            "gates_passed": len(passed_gates),
            "gates_failed": len(failed_gates),
            "gates_warning": len(warning_gates),
            "total_gates": len(gate_results),
            "approval_status": approval_status.value,
            "gate_results": gate_results,
            "cricket_summary": self._generate_cricket_summary(overall_cricket_score),
            "recommendations": self._generate_recommendations(gate_results)
        }
    
    def _run_quality_gate(self, gate: QualityGate, output_path: Path, 
                         expected_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single quality gate."""
        gate_start_time = time.time()
        validation_results = []
        
        # Run validators for this gate
        for validator_name in gate.validators:
            if validator_name in self.validators:
                validator = self.validators[validator_name]
                try:
                    result = validator.validate(output_path, expected_criteria)
                    validation_results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = ValidationReport(
                        validator_name=validator_name,
                        result=ValidationResult.FAIL,
                        score=0.0,
                        message=f"Validator error: {str(e)}",
                        details={"error": str(e)},
                        cricket_score=0.0
                    )
                    validation_results.append(error_result)
        
        # Calculate gate score
        if validation_results:
            gate_score = sum(r.score for r in validation_results) / len(validation_results)
            gate_cricket_scores = [r.cricket_score for r in validation_results if r.cricket_score is not None]
            gate_cricket_score = sum(gate_cricket_scores) / len(gate_cricket_scores) if gate_cricket_scores else None
        else:
            gate_score = 0.0
            gate_cricket_score = None
        
        # Determine gate status
        if gate_score >= gate.threshold:
            if gate_score >= gate.auto_approve_threshold:
                status = "passed"
            else:
                status = "warning"  # Passed but below auto-approve threshold
        else:
            status = "failed"
        
        gate_end_time = time.time()
        
        return {
            "gate_name": gate.name,
            "description": gate.description,
            "status": status,
            "score": gate_score,
            "cricket_score": gate_cricket_score,
            "threshold": gate.threshold,
            "auto_approve_threshold": gate.auto_approve_threshold,
            "required": gate.required,
            "execution_time": gate_end_time - gate_start_time,
            "validation_results": [
                {
                    "validator": r.validator_name,
                    "result": r.result.value,
                    "score": r.score,
                    "message": r.message,
                    "cricket_score": r.cricket_score
                }
                for r in validation_results
            ]
        }
    
    def _determine_approval_status(self, workflow: ApprovalWorkflow, gate_results: List[Dict[str, Any]], 
                                 overall_score: float, overall_cricket_score: float) -> ApprovalStatus:
        """Determine approval status based on gate results."""
        # Check if any required gates failed
        required_failures = [
            r for r in gate_results 
            if r.get("required", True) and r["status"] == "failed"
        ]
        
        if required_failures:
            return ApprovalStatus.REJECTED
        
        # Check for auto-approval conditions
        if workflow.auto_approval_enabled and not workflow.manual_approval_required:
            # All gates passed with high scores
            high_score_gates = [
                r for r in gate_results 
                if r["score"] >= r["auto_approve_threshold"]
            ]
            
            if len(high_score_gates) == len(gate_results):
                return ApprovalStatus.AUTO_APPROVED
        
        # Check if manual approval is required
        if workflow.manual_approval_required:
            return ApprovalStatus.PENDING
        
        # Default approval for passed gates
        failed_gates = [r for r in gate_results if r["status"] == "failed"]
        if not failed_gates:
            return ApprovalStatus.APPROVED
        
        return ApprovalStatus.PENDING
    
    def _generate_cricket_summary(self, overall_cricket_score: float) -> Dict[str, Any]:
        """Generate cricket scoring summary."""
        if overall_cricket_score is None:
            return {"message": "Cricket scoring not available"}
        
        if overall_cricket_score >= self.cricket_config.get("boundary_6", 95):
            return {
                "result": "SIX! 🏏",
                "message": "Excellent performance - all quality gates exceeded expectations",
                "score": overall_cricket_score,
                "achievement": "boundary_6"
            }
        elif overall_cricket_score >= self.cricket_config.get("boundary_4", 85):
            return {
                "result": "FOUR! 🏏",
                "message": "Good performance - quality gates passed with good scores",
                "score": overall_cricket_score,
                "achievement": "boundary_4"
            }
        elif overall_cricket_score >= self.cricket_config.get("wicket", 70):
            return {
                "result": "Single 🏏",
                "message": "Acceptable performance - quality gates passed",
                "score": overall_cricket_score,
                "achievement": "single"
            }
        else:
            return {
                "result": "WICKET! 🏏",
                "message": "Poor performance - quality gates need attention",
                "score": overall_cricket_score,
                "achievement": "wicket"
            }
    
    def _generate_recommendations(self, gate_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on gate results."""
        recommendations = []
        
        failed_gates = [r for r in gate_results if r["status"] == "failed"]
        warning_gates = [r for r in gate_results if r["status"] == "warning"]
        
        if failed_gates:
            recommendations.append(f"🔴 {len(failed_gates)} quality gate(s) failed - immediate attention required")
            for gate in failed_gates:
                recommendations.append(f"  - Fix {gate['gate_name']}: {gate['description']}")
        
        if warning_gates:
            recommendations.append(f"🟡 {len(warning_gates)} quality gate(s) have warnings - consider improvements")
            for gate in warning_gates:
                recommendations.append(f"  - Improve {gate['gate_name']}: score {gate['score']:.1f} (target: {gate['auto_approve_threshold']})")
        
        if not failed_gates and not warning_gates:
            recommendations.append("✅ All quality gates passed - excellent work!")
        
        return recommendations
    
    def generate_quality_report(self, results: Dict[str, Any], output_path: Path) -> Path:
        """Generate comprehensive quality report."""
        report_path = output_path.parent / f"quality_report_{int(time.time())}.json"
        
        # Enhanced report with cricket scoring
        enhanced_results = {
            **results,
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0",
                "cricket_scoring_enabled": True
            },
            "quality_summary": {
                "overall_status": results["approval_status"],
                "cricket_achievement": results["cricket_summary"]["achievement"],
                "performance_level": self._get_performance_level(results["overall_cricket_score"]),
                "improvement_potential": self._calculate_improvement_potential(results["gate_results"])
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_results, f, indent=2, ensure_ascii=False)
        
        return report_path
    
    def _get_performance_level(self, cricket_score: float) -> str:
        """Get performance level description."""
        if cricket_score is None:
            return "unknown"
        elif cricket_score >= 95:
            return "excellent"
        elif cricket_score >= 85:
            return "good"
        elif cricket_score >= 70:
            return "acceptable"
        else:
            return "needs_improvement"
    
    def _calculate_improvement_potential(self, gate_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate improvement potential."""
        total_possible = sum(r["auto_approve_threshold"] for r in gate_results)
        current_total = sum(r["score"] for r in gate_results)
        
        improvement_points = total_possible - current_total
        improvement_percentage = (improvement_points / total_possible) * 100 if total_possible > 0 else 0
        
        return {
            "improvement_points_available": improvement_points,
            "improvement_percentage": improvement_percentage,
            "priority_gates": [
                r["gate_name"] for r in gate_results 
                if r["score"] < r["auto_approve_threshold"]
            ]
        }
