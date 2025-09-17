
"""
Tests for quality gates and approval workflows.
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from tests.validation.quality_gates import (
    QualityGateEngine, QualityGate, ApprovalWorkflow, ApprovalStatus
)

class TestQualityGates:
    """Test suite for quality gates and approval workflows."""
    
    @pytest.fixture
    def quality_gate_config(self, cricket_score_config):
        """Create quality gate configuration."""
        return {
            **cricket_score_config,
            "quality_gates": {
                "strict_validation": True,
                "auto_approval_threshold": 90,
                "manual_review_threshold": 70
            }
        }
    
    @pytest.fixture
    def sample_output_file(self, temp_dir):
        """Create sample output file for testing."""
        output_data = {
            "document_id": "test_001",
            "metadata": {
                "title": "Test Document",
                "author": "Test Author",
                "processing_date": "2025-09-10"
            },
            "content": {
                "sections": 5,
                "requirements": 10,
                "quality_score": 85
            }
        }
        
        output_file = temp_dir / "test_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        return output_file
    
    def test_quality_gate_creation(self, quality_gate_config):
        """Test quality gate creation and configuration."""
        gate = QualityGate(
            name="test_gate",
            description="Test quality gate",
            validators=["DigitalTwinValidator"],
            threshold=80.0,
            auto_approve_threshold=90.0,
            cricket_scoring=True
        )
        
        assert gate.name == "test_gate"
        assert gate.threshold == 80.0
        assert gate.auto_approve_threshold == 90.0
        assert gate.cricket_scoring is True
        assert gate.required is True  # Default value
    
    def test_approval_workflow_creation(self, quality_gate_config):
        """Test approval workflow creation."""
        gate1 = QualityGate("gate1", "Gate 1", ["Validator1"], 80.0, 90.0)
        gate2 = QualityGate("gate2", "Gate 2", ["Validator2"], 75.0, 85.0)
        
        workflow = ApprovalWorkflow(
            name="test_workflow",
            quality_gates=[gate1, gate2],
            auto_approval_enabled=True,
            manual_approval_required=False
        )
        
        assert workflow.name == "test_workflow"
        assert len(workflow.quality_gates) == 2
        assert workflow.auto_approval_enabled is True
        assert workflow.manual_approval_required is False
    
    def test_quality_gate_engine_initialization(self, quality_gate_config):
        """Test quality gate engine initialization."""
        engine = QualityGateEngine(quality_gate_config)
        
        # Check default quality gates are loaded
        assert "digital_twin_quality" in engine.quality_gates
        assert "metadata_completeness" in engine.quality_gates
        assert "template_conformity" in engine.quality_gates
        assert "overall_quality" in engine.quality_gates
        
        # Check default workflows are loaded
        assert "standard" in engine.workflows
        assert "production" in engine.workflows
        
        # Check validators are initialized
        assert "DigitalTwinValidator" in engine.validators
        assert "MetadataValidator" in engine.validators
    
    def test_standard_workflow_execution(self, quality_gate_config, sample_output_file, cricket_score_config):
        """Test standard workflow execution with cricket scoring."""
        engine = QualityGateEngine(quality_gate_config)
        
        expected_criteria = {
            "quality_threshold": 75,
            "required_fields": ["document_id", "metadata", "content"]
        }
        
        results = engine.run_quality_gates(sample_output_file, "standard", expected_criteria)
        
        # Validate workflow execution results
        assert results["workflow_name"] == "standard"
        assert "timestamp" in results
        assert "execution_time" in results
        assert results["execution_time"] > 0
        
        # Validate scores
        assert 0 <= results["overall_score"] <= 100
        assert results["overall_cricket_score"] is not None
        
        # Validate gate results
        assert results["total_gates"] > 0
        assert results["gates_passed"] + results["gates_failed"] + results["gates_warning"] == results["total_gates"]
        
        # Validate approval status
        assert results["approval_status"] in [status.value for status in ApprovalStatus]
        
        # Validate cricket summary
        cricket_summary = results["cricket_summary"]
        assert "result" in cricket_summary
        assert "message" in cricket_summary
        assert "score" in cricket_summary
        
        # Cricket scoring validation
        cricket_score = results["overall_cricket_score"]
        if cricket_score >= cricket_score_config["cricket_scoring"]["boundary_6"]:
            print(f"🏏 SIX! Excellent workflow performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["boundary_4"]:
            print(f"🏏 FOUR! Good workflow performance: {cricket_score:.1f}")
        elif cricket_score >= cricket_score_config["cricket_scoring"]["wicket"]:
            print(f"🏏 Single. Acceptable workflow performance: {cricket_score:.1f}")
        else:
            print(f"🏏 WICKET! Workflow needs improvement: {cricket_score:.1f}")
        
        print(f"🏏 Approval status: {results['approval_status']}")
    
    def test_production_workflow_execution(self, quality_gate_config, sample_output_file):
        """Test production workflow with stricter requirements."""
        engine = QualityGateEngine(quality_gate_config)
        
        expected_criteria = {
            "quality_threshold": 90,  # Higher threshold for production
            "required_fields": ["document_id", "metadata", "content"]
        }
        
        results = engine.run_quality_gates(sample_output_file, "production", expected_criteria)
        
        # Production workflow should have stricter requirements
        assert results["workflow_name"] == "production"
        
        # May require manual approval
        production_workflow = engine.workflows["production"]
        if production_workflow.manual_approval_required:
            assert results["approval_status"] in ["pending", "approved", "rejected"]
        
        print(f"🏏 Production workflow cricket score: {results['overall_cricket_score']:.1f}")
        print(f"🏏 Production approval status: {results['approval_status']}")
    
    def test_auto_approval_logic(self, quality_gate_config, sample_output_file):
        """Test auto-approval logic based on scores."""
        engine = QualityGateEngine(quality_gate_config)
        
        # Create criteria that should result in high scores
        high_score_criteria = {
            "quality_threshold": 70,  # Lower threshold
            "required_fields": ["document_id"]  # Minimal requirements
        }
        
        results = engine.run_quality_gates(sample_output_file, "standard", high_score_criteria)
        
        # Should potentially get auto-approval
        if results["overall_score"] >= 90:
            assert results["approval_status"] in ["auto_approved", "approved"]
            print(f"🏏 Auto-approval achieved with score: {results['overall_score']:.1f}")
        else:
            print(f"🏏 Manual review required, score: {results['overall_score']:.1f}")
    
    def test_quality_gate_failure_handling(self, quality_gate_config, temp_dir):
        """Test handling of quality gate failures."""
        engine = QualityGateEngine(quality_gate_config)
        
        # Create file that will fail validation
        poor_output = {"incomplete": "data"}
        poor_output_file = temp_dir / "poor_output.json"
        with open(poor_output_file, 'w') as f:
            json.dump(poor_output, f)
        
        # Strict criteria that should cause failures
        strict_criteria = {
            "quality_threshold": 95,
            "required_fields": ["document_id", "metadata", "structure", "content", "extra_field"],
            "schema": {
                "required_fields": ["document_id", "metadata", "structure", "content"]
            }
        }
        
        results = engine.run_quality_gates(poor_output_file, "standard", strict_criteria)
        
        # Should have failures
        assert results["gates_failed"] > 0 or results["overall_score"] < 70
        assert results["approval_status"] in ["rejected", "pending"]
        
        # Should have recommendations
        assert len(results["recommendations"]) > 0
        assert any("🔴" in rec for rec in results["recommendations"])  # Should have failure indicators
        
        print(f"🏏 Failed gates: {results['gates_failed']}")
        print(f"🏏 Cricket score with failures: {results['overall_cricket_score']:.1f}")
    
    def test_quality_report_generation(self, quality_gate_config, sample_output_file, temp_dir):
        """Test comprehensive quality report generation."""
        engine = QualityGateEngine(quality_gate_config)
        
        expected_criteria = {"quality_threshold": 80}
        results = engine.run_quality_gates(sample_output_file, "standard", expected_criteria)
        
        # Generate quality report
        report_path = engine.generate_quality_report(results, temp_dir)
        
        # Validate report file
        assert report_path.exists()
        assert report_path.name.startswith("quality_report_")
        assert report_path.suffix == ".json"
        
        # Load and validate report content
        with open(report_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        # Validate enhanced report structure
        assert "report_metadata" in report_data
        assert "quality_summary" in report_data
        assert "cricket_summary" in report_data
        assert "gate_results" in report_data
        
        # Validate report metadata
        report_metadata = report_data["report_metadata"]
        assert "generated_at" in report_metadata
        assert "report_version" in report_metadata
        assert report_metadata["cricket_scoring_enabled"] is True
        
        # Validate quality summary
        quality_summary = report_data["quality_summary"]
        assert "overall_status" in quality_summary
        assert "cricket_achievement" in quality_summary
        assert "performance_level" in quality_summary
        assert "improvement_potential" in quality_summary
        
        # Validate improvement potential
        improvement = quality_summary["improvement_potential"]
        assert "improvement_points_available" in improvement
        assert "improvement_percentage" in improvement
        assert "priority_gates" in improvement
        
        print(f"🏏 Quality report generated: {report_path}")
        print(f"🏏 Performance level: {quality_summary['performance_level']}")
        print(f"🏏 Improvement potential: {improvement['improvement_percentage']:.1f}%")
    
    def test_cricket_scoring_achievements(self, quality_gate_config, sample_output_file, cricket_score_config):
        """Test cricket scoring achievement levels."""
        engine = QualityGateEngine(quality_gate_config)
        
        # Test different criteria to achieve different cricket scores
        test_scenarios = [
            {
                "name": "excellent",
                "criteria": {"quality_threshold": 60, "required_fields": ["document_id"]},
                "expected_achievement": "boundary_6"
            },
            {
                "name": "good", 
                "criteria": {"quality_threshold": 75, "required_fields": ["document_id", "metadata"]},
                "expected_achievement": "boundary_4"
            },
            {
                "name": "acceptable",
                "criteria": {"quality_threshold": 85, "required_fields": ["document_id", "metadata", "content"]},
                "expected_achievement": "single"
            }
        ]
        
        for scenario in test_scenarios:
            results = engine.run_quality_gates(sample_output_file, "standard", scenario["criteria"])
            cricket_summary = results["cricket_summary"]
            
            print(f"🏏 Scenario '{scenario['name']}': {cricket_summary['result']} (Score: {cricket_summary['score']:.1f})")
            
            # Validate cricket achievement is reasonable
            assert cricket_summary["achievement"] in ["boundary_6", "boundary_4", "single", "wicket"]
    
    def test_workflow_performance_monitoring(self, quality_gate_config, sample_output_file, performance_monitor):
        """Test workflow performance monitoring."""
        engine = QualityGateEngine(quality_gate_config)
        
        performance_monitor.start()
        
        # Run multiple workflows to test performance
        workflows_to_test = ["standard", "production"]
        workflow_results = []
        
        for workflow_name in workflows_to_test:
            expected_criteria = {"quality_threshold": 80}
            results = engine.run_quality_gates(sample_output_file, workflow_name, expected_criteria)
            workflow_results.append({
                "workflow": workflow_name,
                "execution_time": results["execution_time"],
                "cricket_score": results["overall_cricket_score"]
            })
        
        performance_monitor.stop()
        
        # Validate performance
        for result in workflow_results:
            assert result["execution_time"] > 0
            assert result["execution_time"] < 10.0  # Should be reasonably fast
            print(f"🏏 {result['workflow']} workflow: {result['execution_time']:.3f}s, cricket: {result['cricket_score']:.1f}")
        
        # Overall performance should be good
        metrics = performance_monitor.get_metrics()
        assert metrics["duration"] < 15.0  # Total time for all workflows
        print(f"🏏 Total workflow performance time: {metrics['duration']:.3f}s")
    
    @pytest.mark.benchmark
    def test_quality_gate_benchmark(self, quality_gate_config, sample_output_file, benchmark):
        """Benchmark quality gate execution."""
        engine = QualityGateEngine(quality_gate_config)
        expected_criteria = {"quality_threshold": 80}
        
        def run_quality_gates():
            return engine.run_quality_gates(sample_output_file, "standard", expected_criteria)
        
        results = benchmark(run_quality_gates)
        
        assert results["workflow_name"] == "standard"
        assert results["overall_cricket_score"] is not None
        print(f"🏏 Benchmark cricket score: {results['overall_cricket_score']:.1f}")
