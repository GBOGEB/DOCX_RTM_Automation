
#!/usr/bin/env python3
"""
DMAIC Pipeline Main Controller
Full lifecycle automation with compliance tracking and DMAIC iteration
"""

import json
import yaml
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DMAICPhase(Enum):
    """DMAIC phases enumeration"""
    DEFINE = "Define"
    MEASURE = "Measure"
    ANALYZE = "Analyze"
    IMPROVE = "Improve"
    CONTROL = "Control"

class ComplianceStatus(Enum):
    """Compliance status enumeration"""
    COMPLIANT = "Compliant"
    NON_COMPLIANT = "Non-Compliant"
    PARTIALLY_COMPLIANT = "Partially Compliant"
    UNDER_REVIEW = "Under Review"

@dataclass
class DMAICIteration:
    """DMAIC iteration tracking"""
    iteration_id: str
    phase: DMAICPhase
    start_date: datetime
    end_date: Optional[datetime]
    objectives: List[str]
    deliverables: List[str]
    success_criteria: List[str]
    actual_results: List[str]
    compliance_score: float
    status: ComplianceStatus
    lessons_learned: List[str]
    next_actions: List[str]

@dataclass
class ComplianceMetric:
    """Compliance tracking metric"""
    metric_id: str
    name: str
    description: str
    target_value: float
    actual_value: float
    unit: str
    measurement_date: datetime
    compliance_threshold: float
    status: ComplianceStatus
    trend: str  # "improving", "stable", "declining"

class DMAICPipelineController:
    """Main controller for DMAIC pipeline automation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.current_iteration = None
        self.iterations_history = []
        self.compliance_metrics = []
        self.automation_state = {}
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load pipeline configuration"""
        default_config = {
            "dmaic_phases": {
                "define": {
                    "duration_days": 14,
                    "required_deliverables": ["Problem Statement", "Project Charter", "SIPOC Diagram"],
                    "success_criteria": ["Clear problem definition", "Stakeholder alignment", "Scope definition"]
                },
                "measure": {
                    "duration_days": 21,
                    "required_deliverables": ["Data Collection Plan", "Baseline Measurements", "Measurement System Analysis"],
                    "success_criteria": ["Reliable data collection", "Baseline established", "Measurement system validated"]
                },
                "analyze": {
                    "duration_days": 28,
                    "required_deliverables": ["Root Cause Analysis", "Statistical Analysis", "Process Map"],
                    "success_criteria": ["Root causes identified", "Data-driven insights", "Process understanding"]
                },
                "improve": {
                    "duration_days": 35,
                    "required_deliverables": ["Solution Design", "Pilot Implementation", "Results Analysis"],
                    "success_criteria": ["Solutions implemented", "Improvements validated", "Benefits realized"]
                },
                "control": {
                    "duration_days": 21,
                    "required_deliverables": ["Control Plan", "Standard Operating Procedures", "Monitoring System"],
                    "success_criteria": ["Sustained improvements", "Process control", "Knowledge transfer"]
                }
            },
            "compliance_thresholds": {
                "high": 0.9,
                "medium": 0.7,
                "low": 0.5
            },
            "automation_settings": {
                "auto_phase_transition": True,
                "compliance_monitoring": True,
                "alert_thresholds": {
                    "schedule_variance": 0.2,
                    "compliance_drop": 0.1
                }
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config
    
    def initialize_dmaic_cycle(self, project_name: str, objectives: List[str]) -> str:
        """Initialize a new DMAIC cycle"""
        iteration_id = f"DMAIC_{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_iteration = DMAICIteration(
            iteration_id=iteration_id,
            phase=DMAICPhase.DEFINE,
            start_date=datetime.now(),
            end_date=None,
            objectives=objectives,
            deliverables=[],
            success_criteria=self.config["dmaic_phases"]["define"]["success_criteria"],
            actual_results=[],
            compliance_score=0.0,
            status=ComplianceStatus.UNDER_REVIEW,
            lessons_learned=[],
            next_actions=self.config["dmaic_phases"]["define"]["required_deliverables"]
        )
        
        logger.info(f"Initialized DMAIC cycle: {iteration_id}")
        return iteration_id
    
    def execute_phase(self, phase: DMAICPhase, deliverables: List[str], 
                     results: List[str]) -> Dict[str, Any]:
        """Execute a specific DMAIC phase"""
        logger.info(f"Executing DMAIC phase: {phase.value}")
        
        if not self.current_iteration:
            raise ValueError("No active DMAIC iteration. Please initialize first.")
        
        # Update current iteration
        self.current_iteration.phase = phase
        self.current_iteration.deliverables.extend(deliverables)
        self.current_iteration.actual_results.extend(results)
        
        # Calculate compliance score for this phase
        compliance_score = self._calculate_phase_compliance(phase, deliverables, results)
        self.current_iteration.compliance_score = compliance_score
        
        # Determine compliance status
        if compliance_score >= self.config["compliance_thresholds"]["high"]:
            self.current_iteration.status = ComplianceStatus.COMPLIANT
        elif compliance_score >= self.config["compliance_thresholds"]["medium"]:
            self.current_iteration.status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            self.current_iteration.status = ComplianceStatus.NON_COMPLIANT
        
        # Generate phase report
        phase_report = self._generate_phase_report(phase, compliance_score)
        
        # Check for automatic phase transition
        if (self.config["automation_settings"]["auto_phase_transition"] and 
            compliance_score >= self.config["compliance_thresholds"]["medium"]):
            next_phase = self._get_next_phase(phase)
            if next_phase:
                logger.info(f"Auto-transitioning to next phase: {next_phase.value}")
                phase_report["auto_transition"] = next_phase.value
        
        return phase_report
    
    def _calculate_phase_compliance(self, phase: DMAICPhase, deliverables: List[str], 
                                  results: List[str]) -> float:
        """Calculate compliance score for a phase"""
        phase_config = self.config["dmaic_phases"][phase.value.lower()]
        required_deliverables = phase_config["required_deliverables"]
        success_criteria = phase_config["success_criteria"]
        
        # Deliverables compliance (50% weight)
        deliverable_score = len(deliverables) / len(required_deliverables) if required_deliverables else 1.0
        deliverable_score = min(deliverable_score, 1.0)
        
        # Results compliance (50% weight)
        results_score = len(results) / len(success_criteria) if success_criteria else 1.0
        results_score = min(results_score, 1.0)
        
        # Combined score
        compliance_score = (deliverable_score * 0.5) + (results_score * 0.5)
        
        return compliance_score
    
    def _get_next_phase(self, current_phase: DMAICPhase) -> Optional[DMAICPhase]:
        """Get the next DMAIC phase"""
        phase_order = [DMAICPhase.DEFINE, DMAICPhase.MEASURE, DMAICPhase.ANALYZE, 
                      DMAICPhase.IMPROVE, DMAICPhase.CONTROL]
        
        try:
            current_index = phase_order.index(current_phase)
            if current_index < len(phase_order) - 1:
                return phase_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _generate_phase_report(self, phase: DMAICPhase, compliance_score: float) -> Dict[str, Any]:
        """Generate comprehensive phase report"""
        return {
            "phase": phase.value,
            "iteration_id": self.current_iteration.iteration_id,
            "compliance_score": compliance_score,
            "status": self.current_iteration.status.value,
            "deliverables_completed": len(self.current_iteration.deliverables),
            "results_achieved": len(self.current_iteration.actual_results),
            "timestamp": datetime.now().isoformat(),
            "recommendations": self._generate_recommendations(phase, compliance_score),
            "risk_assessment": self._assess_phase_risks(phase, compliance_score)
        }
    
    def _generate_recommendations(self, phase: DMAICPhase, compliance_score: float) -> List[str]:
        """Generate recommendations based on phase performance"""
        recommendations = []
        
        if compliance_score < self.config["compliance_thresholds"]["medium"]:
            recommendations.append(f"Phase {phase.value} requires additional attention")
            recommendations.append("Consider extending timeline or adding resources")
            recommendations.append("Review deliverables and success criteria")
        
        if compliance_score >= self.config["compliance_thresholds"]["high"]:
            recommendations.append(f"Phase {phase.value} completed successfully")
            recommendations.append("Ready for transition to next phase")
            recommendations.append("Document lessons learned for future iterations")
        
        return recommendations
    
    def _assess_phase_risks(self, phase: DMAICPhase, compliance_score: float) -> Dict[str, Any]:
        """Assess risks for the current phase"""
        risk_level = "Low"
        risk_factors = []
        
        if compliance_score < self.config["compliance_thresholds"]["low"]:
            risk_level = "High"
            risk_factors.extend([
                "Low compliance score indicates significant issues",
                "Project timeline may be at risk",
                "Quality of deliverables may be compromised"
            ])
        elif compliance_score < self.config["compliance_thresholds"]["medium"]:
            risk_level = "Medium"
            risk_factors.extend([
                "Moderate compliance issues identified",
                "Some deliverables may need rework",
                "Timeline pressure possible"
            ])
        
        return {
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "mitigation_actions": self._suggest_mitigation_actions(risk_level)
        }
    
    def _suggest_mitigation_actions(self, risk_level: str) -> List[str]:
        """Suggest mitigation actions based on risk level"""
        if risk_level == "High":
            return [
                "Immediate stakeholder review required",
                "Consider project scope adjustment",
                "Allocate additional resources",
                "Implement daily progress monitoring"
            ]
        elif risk_level == "Medium":
            return [
                "Increase monitoring frequency",
                "Review resource allocation",
                "Clarify deliverable requirements",
                "Schedule stakeholder check-in"
            ]
        else:
            return [
                "Continue current approach",
                "Maintain regular monitoring",
                "Document best practices"
            ]
    
    def track_compliance_metrics(self, metrics: List[ComplianceMetric]) -> Dict[str, Any]:
        """Track and analyze compliance metrics"""
        self.compliance_metrics.extend(metrics)
        
        # Analyze trends
        compliance_analysis = {
            "total_metrics": len(self.compliance_metrics),
            "compliant_metrics": len([m for m in self.compliance_metrics if m.status == ComplianceStatus.COMPLIANT]),
            "non_compliant_metrics": len([m for m in self.compliance_metrics if m.status == ComplianceStatus.NON_COMPLIANT]),
            "average_compliance": sum(m.actual_value / m.target_value for m in self.compliance_metrics) / len(self.compliance_metrics) if self.compliance_metrics else 0,
            "trending_metrics": self._analyze_metric_trends(),
            "alerts": self._generate_compliance_alerts()
        }
        
        return compliance_analysis
    
    def _analyze_metric_trends(self) -> Dict[str, List[str]]:
        """Analyze trends in compliance metrics"""
        trends = {"improving": [], "stable": [], "declining": []}
        
        for metric in self.compliance_metrics:
            trends[metric.trend].append(metric.name)
        
        return trends
    
    def _generate_compliance_alerts(self) -> List[Dict[str, Any]]:
        """Generate compliance alerts"""
        alerts = []
        
        for metric in self.compliance_metrics:
            if metric.status == ComplianceStatus.NON_COMPLIANT:
                alerts.append({
                    "type": "compliance_violation",
                    "metric": metric.name,
                    "severity": "high",
                    "message": f"Metric {metric.name} is non-compliant: {metric.actual_value} vs target {metric.target_value}"
                })
            elif metric.trend == "declining":
                alerts.append({
                    "type": "declining_trend",
                    "metric": metric.name,
                    "severity": "medium",
                    "message": f"Metric {metric.name} shows declining trend"
                })
        
        return alerts
    
    def generate_dmaic_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive DMAIC dashboard data"""
        dashboard_data = {
            "current_iteration": asdict(self.current_iteration) if self.current_iteration else None,
            "iterations_history": [asdict(iteration) for iteration in self.iterations_history],
            "compliance_summary": self._generate_compliance_summary(),
            "performance_metrics": self._calculate_performance_metrics(),
            "recommendations": self._generate_overall_recommendations(),
            "generated_at": datetime.now().isoformat()
        }
        
        return dashboard_data
    
    def _generate_compliance_summary(self) -> Dict[str, Any]:
        """Generate compliance summary"""
        if not self.compliance_metrics:
            return {"status": "No metrics available"}
        
        total_metrics = len(self.compliance_metrics)
        compliant_count = len([m for m in self.compliance_metrics if m.status == ComplianceStatus.COMPLIANT])
        
        return {
            "overall_compliance_rate": compliant_count / total_metrics if total_metrics > 0 else 0,
            "total_metrics": total_metrics,
            "compliant_metrics": compliant_count,
            "compliance_distribution": {
                status.value: len([m for m in self.compliance_metrics if m.status == status])
                for status in ComplianceStatus
            }
        }
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        if not self.iterations_history:
            return {"status": "No historical data available"}
        
        avg_compliance = sum(iteration.compliance_score for iteration in self.iterations_history) / len(self.iterations_history)
        
        return {
            "average_compliance_score": avg_compliance,
            "total_iterations": len(self.iterations_history),
            "successful_iterations": len([i for i in self.iterations_history if i.status == ComplianceStatus.COMPLIANT]),
            "average_cycle_time": self._calculate_average_cycle_time()
        }
    
    def _calculate_average_cycle_time(self) -> float:
        """Calculate average DMAIC cycle time"""
        completed_iterations = [i for i in self.iterations_history if i.end_date]
        if not completed_iterations:
            return 0.0
        
        cycle_times = [(i.end_date - i.start_date).days for i in completed_iterations]
        return sum(cycle_times) / len(cycle_times)
    
    def _generate_overall_recommendations(self) -> List[str]:
        """Generate overall recommendations"""
        recommendations = []
        
        if self.current_iteration:
            if self.current_iteration.compliance_score < self.config["compliance_thresholds"]["medium"]:
                recommendations.append("Current iteration requires immediate attention")
                recommendations.append("Consider stakeholder intervention")
        
        compliance_summary = self._generate_compliance_summary()
        if compliance_summary.get("overall_compliance_rate", 0) < 0.7:
            recommendations.append("Overall compliance rate is below acceptable threshold")
            recommendations.append("Review and strengthen compliance processes")
        
        return recommendations
    
    def export_results(self, output_path: str) -> None:
        """Export pipeline results"""
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Export dashboard data
        dashboard_data = self.generate_dmaic_dashboard()
        with open(output_dir / "dmaic_dashboard.json", 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        
        # Export compliance metrics
        if self.compliance_metrics:
            metrics_df = pd.DataFrame([asdict(metric) for metric in self.compliance_metrics])
            metrics_df.to_csv(output_dir / "compliance_metrics.csv", index=False)
        
        logger.info(f"Pipeline results exported to {output_path}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="DMAIC Pipeline Controller")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--project", help="Project name")
    parser.add_argument("--phase", choices=["define", "measure", "analyze", "improve", "control"], help="DMAIC phase to execute")
    parser.add_argument("--output", default="pipeline_output", help="Output directory")
    
    args = parser.parse_args()
    
    # Initialize controller
    controller = DMAICPipelineController(args.config)
    
    if args.project and args.phase:
        # Initialize and execute phase
        iteration_id = controller.initialize_dmaic_cycle(args.project, ["Improve document processing efficiency"])
        
        phase_enum = DMAICPhase(args.phase.title())
        deliverables = ["Sample deliverable"]
        results = ["Sample result"]
        
        phase_report = controller.execute_phase(phase_enum, deliverables, results)
        print(f"Phase {args.phase} completed with compliance score: {phase_report['compliance_score']}")
    
    # Export results
    controller.export_results(args.output)
    print(f"Results exported to {args.output}")

if __name__ == "__main__":
    main()
