
"""
Comprehensive output reporting and metrics generation.
"""

import json
import yaml
import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Template

@dataclass
class ReportMetrics:
    """Report metrics structure."""
    total_files_processed: int
    successful_validations: int
    failed_validations: int
    warning_validations: int
    average_cricket_score: float
    processing_time: float
    quality_gate_pass_rate: float

class OutputReportGenerator:
    """Generator for comprehensive output reports and metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cricket_config = config.get("cricket_scoring", {})
    
    def generate_comprehensive_report(self, validation_results: List[Dict[str, Any]], 
                                    output_dir: Path) -> Dict[str, Path]:
        """Generate comprehensive output report in multiple formats."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Calculate metrics
        metrics = self._calculate_metrics(validation_results)
        
        # Generate different report formats
        report_files = {}
        
        # JSON report
        report_files["json"] = self._generate_json_report(validation_results, metrics, output_dir)
        
        # HTML report
        report_files["html"] = self._generate_html_report(validation_results, metrics, output_dir)
        
        # CSV report
        report_files["csv"] = self._generate_csv_report(validation_results, metrics, output_dir)
        
        # Cricket scorecard
        report_files["cricket_scorecard"] = self._generate_cricket_scorecard(validation_results, metrics, output_dir)
        
        # Performance charts
        report_files["charts"] = self._generate_performance_charts(validation_results, metrics, output_dir)
        
        return report_files
    
    def _calculate_metrics(self, validation_results: List[Dict[str, Any]]) -> ReportMetrics:
        """Calculate comprehensive metrics from validation results."""
        if not validation_results:
            return ReportMetrics(0, 0, 0, 0, 0.0, 0.0, 0.0)
        
        total_files = len(validation_results)
        successful = len([r for r in validation_results if r.get("approval_status") == "approved" or r.get("approval_status") == "auto_approved"])
        failed = len([r for r in validation_results if r.get("approval_status") == "rejected"])
        warning = total_files - successful - failed
        
        # Calculate average cricket score
        cricket_scores = [r.get("overall_cricket_score", 0) for r in validation_results if r.get("overall_cricket_score") is not None]
        avg_cricket_score = sum(cricket_scores) / len(cricket_scores) if cricket_scores else 0.0
        
        # Calculate total processing time
        processing_times = [r.get("execution_time", 0) for r in validation_results]
        total_processing_time = sum(processing_times)
        
        # Calculate quality gate pass rate
        total_gates = sum(r.get("total_gates", 0) for r in validation_results)
        passed_gates = sum(r.get("gates_passed", 0) for r in validation_results)
        quality_gate_pass_rate = (passed_gates / total_gates * 100) if total_gates > 0 else 0.0
        
        return ReportMetrics(
            total_files_processed=total_files,
            successful_validations=successful,
            failed_validations=failed,
            warning_validations=warning,
            average_cricket_score=avg_cricket_score,
            processing_time=total_processing_time,
            quality_gate_pass_rate=quality_gate_pass_rate
        )
    
    def _generate_json_report(self, validation_results: List[Dict[str, Any]], 
                            metrics: ReportMetrics, output_dir: Path) -> Path:
        """Generate JSON format report."""
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "comprehensive_validation_report",
                "version": "1.0.0",
                "cricket_scoring_enabled": True
            },
            "summary_metrics": asdict(metrics),
            "cricket_summary": self._generate_cricket_summary(metrics.average_cricket_score),
            "validation_results": validation_results,
            "performance_analysis": self._analyze_performance(validation_results),
            "recommendations": self._generate_recommendations(validation_results, metrics)
        }
        
        report_path = output_dir / f"validation_report_{int(datetime.now().timestamp())}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return report_path
    
    def _generate_html_report(self, validation_results: List[Dict[str, Any]], 
                            metrics: ReportMetrics, output_dir: Path) -> Path:
        """Generate HTML format report."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Processing Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }
        .cricket-score { font-size: 2em; color: #FF6B35; font-weight: bold; margin: 10px 0; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #4CAF50; }
        .metric-value { font-size: 2em; font-weight: bold; color: #333; }
        .metric-label { color: #666; font-size: 0.9em; }
        .cricket-achievement { padding: 15px; margin: 20px 0; border-radius: 8px; text-align: center; font-weight: bold; }
        .six { background-color: #4CAF50; color: white; }
        .four { background-color: #FF9800; color: white; }
        .single { background-color: #2196F3; color: white; }
        .wicket { background-color: #f44336; color: white; }
        .results-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .results-table th, .results-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .results-table th { background-color: #f2f2f2; font-weight: bold; }
        .status-approved { color: #4CAF50; font-weight: bold; }
        .status-rejected { color: #f44336; font-weight: bold; }
        .status-pending { color: #FF9800; font-weight: bold; }
        .recommendations { background: #e3f2fd; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .recommendation-item { margin: 10px 0; padding: 10px; background: white; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏏 Document Processing Validation Report</h1>
            <div class="cricket-score">Cricket Score: {{ cricket_summary.score | round(1) }}</div>
            <div class="cricket-achievement {{ cricket_summary.achievement }}">
                {{ cricket_summary.result }} - {{ cricket_summary.message }}
            </div>
            <p>Generated on {{ report_metadata.generated_at }}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{{ metrics.total_files_processed }}</div>
                <div class="metric-label">Total Files Processed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ metrics.successful_validations }}</div>
                <div class="metric-label">Successful Validations</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ metrics.quality_gate_pass_rate | round(1) }}%</div>
                <div class="metric-label">Quality Gate Pass Rate</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ metrics.processing_time | round(2) }}s</div>
                <div class="metric-label">Total Processing Time</div>
            </div>
        </div>
        
        <h2>Validation Results</h2>
        <table class="results-table">
            <thead>
                <tr>
                    <th>Workflow</th>
                    <th>Overall Score</th>
                    <th>Cricket Score</th>
                    <th>Approval Status</th>
                    <th>Gates Passed</th>
                    <th>Execution Time</th>
                </tr>
            </thead>
            <tbody>
                {% for result in validation_results %}
                <tr>
                    <td>{{ result.workflow_name }}</td>
                    <td>{{ result.overall_score | round(1) }}</td>
                    <td>{{ result.overall_cricket_score | round(1) }}</td>
                    <td class="status-{{ result.approval_status.replace('_', '-') }}">{{ result.approval_status }}</td>
                    <td>{{ result.gates_passed }}/{{ result.total_gates }}</td>
                    <td>{{ result.execution_time | round(3) }}s</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="recommendations">
            <h2>🎯 Recommendations</h2>
            {% for recommendation in recommendations %}
            <div class="recommendation-item">{{ recommendation }}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        cricket_summary = self._generate_cricket_summary(metrics.average_cricket_score)
        recommendations = self._generate_recommendations(validation_results, metrics)
        
        html_content = template.render(
            report_metadata={"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            metrics=metrics,
            cricket_summary=cricket_summary,
            validation_results=validation_results,
            recommendations=recommendations
        )
        
        report_path = output_dir / f"validation_report_{int(datetime.now().timestamp())}.html"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def _generate_csv_report(self, validation_results: List[Dict[str, Any]], 
                           metrics: ReportMetrics, output_dir: Path) -> Path:
        """Generate CSV format report."""
        report_path = output_dir / f"validation_report_{int(datetime.now().timestamp())}.csv"
        
        # Flatten validation results for CSV
        csv_data = []
        for result in validation_results:
            csv_row = {
                "workflow_name": result.get("workflow_name", ""),
                "timestamp": result.get("timestamp", ""),
                "overall_score": result.get("overall_score", 0),
                "overall_cricket_score": result.get("overall_cricket_score", 0),
                "approval_status": result.get("approval_status", ""),
                "gates_passed": result.get("gates_passed", 0),
                "gates_failed": result.get("gates_failed", 0),
                "gates_warning": result.get("gates_warning", 0),
                "total_gates": result.get("total_gates", 0),
                "execution_time": result.get("execution_time", 0),
                "cricket_achievement": result.get("cricket_summary", {}).get("achievement", "")
            }
            csv_data.append(csv_row)
        
        # Write CSV
        if csv_data:
            df = pd.DataFrame(csv_data)
            df.to_csv(report_path, index=False)
        
        return report_path
    
    def _generate_cricket_scorecard(self, validation_results: List[Dict[str, Any]], 
                                  metrics: ReportMetrics, output_dir: Path) -> Path:
        """Generate cricket-style scorecard."""
        scorecard_data = {
            "match_summary": {
                "total_overs": len(validation_results),
                "runs_scored": int(metrics.average_cricket_score * len(validation_results)),
                "wickets_lost": metrics.failed_validations,
                "run_rate": metrics.average_cricket_score,
                "strike_rate": (metrics.successful_validations / metrics.total_files_processed * 100) if metrics.total_files_processed > 0 else 0
            },
            "batting_performance": {
                "sixes": len([r for r in validation_results if r.get("overall_cricket_score", 0) >= self.cricket_config.get("boundary_6", 95)]),
                "fours": len([r for r in validation_results if self.cricket_config.get("boundary_4", 85) <= r.get("overall_cricket_score", 0) < self.cricket_config.get("boundary_6", 95)]),
                "singles": len([r for r in validation_results if self.cricket_config.get("wicket", 70) <= r.get("overall_cricket_score", 0) < self.cricket_config.get("boundary_4", 85)]),
                "wickets": len([r for r in validation_results if r.get("overall_cricket_score", 0) < self.cricket_config.get("wicket", 70)])
            },
            "individual_scores": [
                {
                    "workflow": r.get("workflow_name", ""),
                    "score": r.get("overall_cricket_score", 0),
                    "balls_faced": r.get("total_gates", 0),
                    "achievement": r.get("cricket_summary", {}).get("achievement", "")
                }
                for r in validation_results
            ]
        }
        
        scorecard_path = output_dir / f"cricket_scorecard_{int(datetime.now().timestamp())}.json"
        with open(scorecard_path, 'w', encoding='utf-8') as f:
            json.dump(scorecard_data, f, indent=2)
        
        return scorecard_path
    
    def _generate_performance_charts(self, validation_results: List[Dict[str, Any]], 
                                   metrics: ReportMetrics, output_dir: Path) -> Path:
        """Generate performance visualization charts."""
        charts_dir = output_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        try:
            # Cricket score distribution
            cricket_scores = [r.get("overall_cricket_score", 0) for r in validation_results if r.get("overall_cricket_score") is not None]
            
            if cricket_scores:
                plt.figure(figsize=(10, 6))
                plt.hist(cricket_scores, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
                plt.axvline(self.cricket_config.get("boundary_6", 95), color='green', linestyle='--', label='SIX (95+)')
                plt.axvline(self.cricket_config.get("boundary_4", 85), color='orange', linestyle='--', label='FOUR (85+)')
                plt.axvline(self.cricket_config.get("wicket", 70), color='red', linestyle='--', label='WICKET (70-)')
                plt.xlabel('Cricket Score')
                plt.ylabel('Frequency')
                plt.title('🏏 Cricket Score Distribution')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.savefig(charts_dir / "cricket_score_distribution.png", dpi=300, bbox_inches='tight')
                plt.close()
            
            # Quality gate pass rates
            gate_names = []
            pass_rates = []
            
            for result in validation_results:
                for gate_result in result.get("gate_results", []):
                    gate_name = gate_result.get("gate_name", "")
                    if gate_name not in gate_names:
                        gate_names.append(gate_name)
                        # Calculate pass rate for this gate across all results
                        gate_passes = sum(1 for r in validation_results 
                                        for g in r.get("gate_results", []) 
                                        if g.get("gate_name") == gate_name and g.get("status") == "passed")
                        gate_total = sum(1 for r in validation_results 
                                       for g in r.get("gate_results", []) 
                                       if g.get("gate_name") == gate_name)
                        pass_rate = (gate_passes / gate_total * 100) if gate_total > 0 else 0
                        pass_rates.append(pass_rate)
            
            if gate_names and pass_rates:
                plt.figure(figsize=(12, 6))
                bars = plt.bar(gate_names, pass_rates, color=['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in pass_rates])
                plt.xlabel('Quality Gates')
                plt.ylabel('Pass Rate (%)')
                plt.title('🎯 Quality Gate Pass Rates')
                plt.xticks(rotation=45, ha='right')
                plt.ylim(0, 100)
                
                # Add value labels on bars
                for bar, rate in zip(bars, pass_rates):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                           f'{rate:.1f}%', ha='center', va='bottom')
                
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(charts_dir / "quality_gate_pass_rates.png", dpi=300, bbox_inches='tight')
                plt.close()
            
        except Exception as e:
            # If matplotlib is not available or other issues, create a simple text report
            with open(charts_dir / "chart_generation_error.txt", 'w') as f:
                f.write(f"Chart generation failed: {str(e)}\n")
                f.write("Install matplotlib for chart generation: pip install matplotlib\n")
        
        return charts_dir
    
    def _generate_cricket_summary(self, average_cricket_score: float) -> Dict[str, Any]:
        """Generate cricket scoring summary."""
        if average_cricket_score >= self.cricket_config.get("boundary_6", 95):
            return {
                "result": "SIX! 🏏",
                "message": "Outstanding performance across all validations",
                "score": average_cricket_score,
                "achievement": "six"
            }
        elif average_cricket_score >= self.cricket_config.get("boundary_4", 85):
            return {
                "result": "FOUR! 🏏",
                "message": "Excellent performance with room for improvement",
                "score": average_cricket_score,
                "achievement": "four"
            }
        elif average_cricket_score >= self.cricket_config.get("wicket", 70):
            return {
                "result": "Single 🏏",
                "message": "Good performance meeting basic requirements",
                "score": average_cricket_score,
                "achievement": "single"
            }
        else:
            return {
                "result": "WICKET! 🏏",
                "message": "Performance needs significant improvement",
                "score": average_cricket_score,
                "achievement": "wicket"
            }
    
    def _analyze_performance(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends and patterns."""
        if not validation_results:
            return {}
        
        # Execution time analysis
        execution_times = [r.get("execution_time", 0) for r in validation_results]
        avg_execution_time = sum(execution_times) / len(execution_times)
        max_execution_time = max(execution_times) if execution_times else 0
        min_execution_time = min(execution_times) if execution_times else 0
        
        # Score analysis
        scores = [r.get("overall_score", 0) for r in validation_results]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "execution_time_analysis": {
                "average": avg_execution_time,
                "maximum": max_execution_time,
                "minimum": min_execution_time,
                "total": sum(execution_times)
            },
            "score_analysis": {
                "average_score": avg_score,
                "score_distribution": {
                    "excellent": len([s for s in scores if s >= 90]),
                    "good": len([s for s in scores if 80 <= s < 90]),
                    "acceptable": len([s for s in scores if 70 <= s < 80]),
                    "needs_improvement": len([s for s in scores if s < 70])
                }
            }
        }
    
    def _generate_recommendations(self, validation_results: List[Dict[str, Any]], 
                                metrics: ReportMetrics) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Performance recommendations
        if metrics.average_cricket_score < self.cricket_config.get("boundary_4", 85):
            recommendations.append("🎯 Focus on improving overall quality scores to achieve FOUR (85+) cricket performance")
        
        if metrics.quality_gate_pass_rate < 90:
            recommendations.append(f"🔧 Quality gate pass rate is {metrics.quality_gate_pass_rate:.1f}% - target 90%+ for optimal performance")
        
        if metrics.failed_validations > 0:
            recommendations.append(f"🔴 {metrics.failed_validations} validation(s) failed - review and address quality issues")
        
        # Processing time recommendations
        if metrics.processing_time > 60:  # More than 1 minute total
            recommendations.append("⚡ Consider optimizing processing pipeline for better performance")
        
        # Success rate recommendations
        success_rate = (metrics.successful_validations / metrics.total_files_processed * 100) if metrics.total_files_processed > 0 else 0
        if success_rate < 95:
            recommendations.append(f"📈 Success rate is {success_rate:.1f}% - aim for 95%+ success rate")
        
        # Cricket-specific recommendations
        if metrics.average_cricket_score >= self.cricket_config.get("boundary_6", 95):
            recommendations.append("🏆 Excellent cricket performance! Maintain this level of quality")
        elif metrics.average_cricket_score >= self.cricket_config.get("boundary_4", 85):
            recommendations.append("🎯 Good cricket performance - push for SIX (95+) achievement")
        
        if not recommendations:
            recommendations.append("✅ All metrics look excellent - keep up the great work!")
        
        return recommendations
