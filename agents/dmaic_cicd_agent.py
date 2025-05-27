import os
import json
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum

from dmaic import DMAICHandler, DMAICPhase, DMAICFactorizer
from utils.ci_cd_integration import CICDStage, DMAICCICDIntegration
from utils.output_handler import OutputHandler
from agents.agent_common import BaseAgent, AgentRole, AgentMessage, AgentPriority, StandardAgentResponse, AgentCapability, validate_input

class PipelineMetrics(Enum):
    """Critical metrics for CI/CD pipeline analysis"""
    BUILD_TIME = "build_time"
    TEST_COVERAGE = "test_coverage"
    TEST_SUCCESS_RATE = "test_success_rate"
    DEPLOYMENT_FREQUENCY = "deployment_frequency"
    LEAD_TIME = "lead_time"
    CHANGE_FAILURE_RATE = "change_failure_rate"
    MTTR = "mean_time_to_recovery"

    @property
    def lower_is_better(self) -> bool:
        """Indicates if a lower value is better for this metric."""
        return self.value in [
            PipelineMetrics.BUILD_TIME.value,
            PipelineMetrics.CHANGE_FAILURE_RATE.value,
            PipelineMetrics.MTTR.value,
            PipelineMetrics.LEAD_TIME.value  # Assuming lower lead time is better
        ]

class DMAICCICDAgent(BaseAgent):
    """
    AI Agent that applies DMAIC methodology to CI/CD processes.
    This agent monitors, analyzes, and improves CI/CD pipelines using
    the structured DMAIC (Define-Measure-Analyze-Improve-Control) approach.
    """

    def __init__(self, dmaic_handler: DMAICHandler, output_handler: OutputHandler):
        """Initialize the DMAIC CI/CD agent"""
        super().__init__("cicd_agent", AgentRole.ANALYST, output_handler)  # Pass output_handler
        self.dmaic_handler = dmaic_handler
        self.integration = DMAICCICDIntegration(dmaic_handler, output_handler)
        self.pipeline_metrics: Dict[str, Any] = {}
        self.improvement_iterations = 0
        self.baseline_metrics: Dict[str, Any] = {}

        self.register_capability(AgentCapability.CICD_PIPELINE_ANALYSIS)
        self.register_capability(AgentCapability.CICD_METRICS_COLLECTION)
        self.register_capability(AgentCapability.CICD_IMPROVEMENT_PLANNING)
        self.register_capability(AgentCapability.CICD_BUILD_FAILURE_ANALYSIS)

        # Register message handlers if this agent is to be called by others
        self.register_message_handler("initialize_cicd_project", self.handle_initialize_project)
        self.register_message_handler("collect_cicd_baseline", self.handle_collect_baseline_metrics)
        self.register_message_handler("analyze_cicd_performance", self.handle_analyze_pipeline_performance)
        self.register_message_handler("generate_cicd_improvement_plan", self.handle_generate_improvement_plan)
        self.register_message_handler("establish_cicd_control_plan", self.handle_establish_control_plan)
        self.register_message_handler("analyze_cicd_build_failure", self.handle_analyze_build_failure)
        self.register_message_handler("compare_cicd_metrics", self.handle_compare_metrics)

    def handle_initialize_project(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["pipeline_name", "config"]):
            return {"status": "error", "message": "Missing pipeline_name or config.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        pipeline_name = content["pipeline_name"]
        config = content["config"]
        try:
            define_outputs = self.initialize_project(pipeline_name, config)
            return {"status": "success", "message": "Project initialized.", "data": define_outputs, "error_details": None, "markdown_content": None}
        except Exception as e:
            return {"status": "error", "message": "Failed to initialize project.", "data": None, "error_details": str(e), "markdown_content": None}

    def initialize_project(self, pipeline_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a CI/CD improvement project using DMAIC"""
        # Start with Define phase
        self.dmaic_handler.start_phase(DMAICPhase.DEFINE)

        # Automatically generate problem statement based on pipeline name
        problem_definition = self.dmaic_handler.interact(
            f"Define specific CI/CD problems that might exist in a pipeline named '{pipeline_name}'. "
            f"Focus on potential inefficiencies and quality issues."
        )

        # Define the scope and goals
        scope_goals = self.dmaic_handler.interact(
            f"Based on the pipeline name '{pipeline_name}' and potential problems identified, "
            f"what should be the scope and specific goals for improving this CI/CD pipeline?"
        )

        # Complete Define phase
        define_outputs = {
            "pipeline_name": pipeline_name,
            "problem_statement": problem_definition,
            "scope_and_goals": scope_goals,
            "config": config
        }

        self.dmaic_handler.complete_phase(define_outputs)
        self.output_handler.log_info(f"DMAIC CI/CD project initialized for pipeline: {pipeline_name}")

        return define_outputs

    def handle_collect_baseline_metrics(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["pipeline_data"]):
            return {"status": "error", "message": "Missing pipeline_data.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        pipeline_data = content["pipeline_data"]
        try:
            measure_outputs = self.collect_baseline_metrics(pipeline_data)
            return {"status": "success", "message": "Baseline metrics collected.", "data": measure_outputs, "error_details": None, "markdown_content": None}
        except Exception as e:
            return {"status": "error", "message": "Failed to collect baseline metrics.", "data": None, "error_details": str(e), "markdown_content": None}

    def collect_baseline_metrics(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect baseline metrics for the CI/CD pipeline (Measure phase)"""
        self.dmaic_handler.start_phase(DMAICPhase.MEASURE)

        # Extract metrics from pipeline data
        extracted_metrics = self._extract_metrics_from_pipeline(pipeline_data)
        self.baseline_metrics = extracted_metrics

        # Have DMAIC analyze the baseline metrics
        metrics_analysis = self.dmaic_handler.interact(
            f"Analyze these baseline CI/CD metrics and identify what they tell us about the current state of the pipeline:\n"
            f"{json.dumps(extracted_metrics, indent=2)}"
        )

        measure_outputs = {
            "baseline_metrics": extracted_metrics,
            "metrics_analysis": metrics_analysis
        }

        self.dmaic_handler.complete_phase(measure_outputs)
        return measure_outputs

    def handle_analyze_pipeline_performance(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["pipeline_runs"]):
            return {"status": "error", "message": "Missing pipeline_runs.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        pipeline_runs = content["pipeline_runs"]
        if not isinstance(pipeline_runs, list):
            return {"status": "error", "message": "pipeline_runs must be a list.", "data": None, "error_details": "Invalid input type", "markdown_content": None}

        try:
            analyze_outputs = self.analyze_pipeline_performance(pipeline_runs)
            return {"status": "success", "message": "Pipeline performance analyzed.", "data": analyze_outputs, "error_details": None, "markdown_content": None}
        except Exception as e:
            return {"status": "error", "message": "Failed to analyze pipeline performance.", "data": None, "error_details": str(e), "markdown_content": None}

    def analyze_pipeline_performance(self, pipeline_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze CI/CD pipeline performance data (Analyze phase)"""
        self.dmaic_handler.start_phase(DMAICPhase.ANALYZE)

        # Prepare data for analysis
        pipeline_summary = self._summarize_pipeline_runs(pipeline_runs)

        # Perform root cause analysis
        root_cause_prompt = (
            f"Analyze the following CI/CD pipeline performance data and identify potential root causes of issues:\n"
            f"{json.dumps(pipeline_summary, indent=2)}\n\n"
            f"Consider build failures, test failures, slow deployments, and any other performance issues."
        )

        root_cause_analysis = self.dmaic_handler.interact(root_cause_prompt)

        # Identify improvement opportunities
        opportunity_prompt = (
            f"Based on the root cause analysis, identify specific improvement opportunities for this CI/CD pipeline."
        )

        improvement_opportunities = self.dmaic_handler.interact(opportunity_prompt)

        analyze_outputs = {
            "pipeline_summary": pipeline_summary,
            "root_cause_analysis": root_cause_analysis,
            "improvement_opportunities": improvement_opportunities
        }

        self.dmaic_handler.complete_phase(analyze_outputs)
        return analyze_outputs

    def generate_improvement_plan(self, analyze_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate improvement plan for CI/CD pipeline (Improve phase)"""
        self.dmaic_handler.start_phase(DMAICPhase.IMPROVE)

        # Generate improvement solutions
        solutions_prompt = (
            f"Based on the following analysis:\n"
            f"{analyze_results['root_cause_analysis']}\n\n"
            f"And these opportunities:\n"
            f"{analyze_results['improvement_opportunities']}\n\n"
            f"Generate specific, actionable solutions to improve the CI/CD pipeline. Include code examples where appropriate."
        )

        solutions = self.dmaic_handler.interact(solutions_prompt)

        # Prioritize improvements
        prioritization_prompt = (
            f"Prioritize the proposed solutions based on expected impact and implementation effort. "
            f"Create a prioritized implementation roadmap."
        )

        prioritized_roadmap = self.dmaic_handler.interact(prioritization_prompt)

        # Implementation plan
        implementation_prompt = (
            f"Create a detailed implementation plan for the top 3 prioritized improvements. "
            f"Include specific steps, resources needed, and expected outcomes."
        )

        implementation_plan = self.dmaic_handler.interact(implementation_prompt)

        improve_outputs = {
            "proposed_solutions": solutions,
            "prioritized_roadmap": prioritized_roadmap,
            "implementation_plan": implementation_plan,
            "improvement_iteration": self.improvement_iterations + 1
        }

        self.improvement_iterations += 1
        self.dmaic_handler.complete_phase(improve_outputs)
        return improve_outputs

    def establish_control_plan(self, improve_results: Dict[str, Any]) -> Dict[str, Any]:
        """Establish control plan to sustain improvements (Control phase)"""
        self.dmaic_handler.start_phase(DMAICPhase.CONTROL)

        # Create control metrics
        control_metrics_prompt = (
            f"Based on the improvement plan:\n"
            f"{improve_results['implementation_plan']}\n\n"
            f"Define specific metrics that should be monitored to ensure the improvements are sustained over time."
        )

        control_metrics = self.dmaic_handler.interact(control_metrics_prompt)

        # Monitoring plan
        monitoring_prompt = (
            f"Create a monitoring plan that defines how frequently metrics should be checked, "
            f"who should review them, and what actions should be taken if metrics drift outside acceptable ranges."
        )

        monitoring_plan = self.dmaic_handler.interact(monitoring_prompt)

        # Standardization plan
        standardization_prompt = (
            f"How should these CI/CD improvements be standardized across other pipelines in the organization? "
            f"Provide a standardization approach and documentation requirements."
        )

        standardization_plan = self.dmaic_handler.interact(standardization_prompt)

        control_outputs = {
            "control_metrics": control_metrics,
            "monitoring_plan": monitoring_plan,
            "standardization_plan": standardization_plan
        }

        self.dmaic_handler.complete_phase(control_outputs)
        return control_outputs

    def analyze_build_failure(self, build_logs: str) -> Dict[str, Any]:
        """Analyze a CI/CD build failure and provide recommendations"""
        prompt = (
            f"Analyze this CI/CD build failure log and identify:\n"
            f"1. The root cause of the failure\n"
            f"2. Potential solutions\n"
            f"3. How to prevent similar issues in the future\n\n"
            f"Build Logs:\n{build_logs[:3000]}..."  # Truncate if too long
        )

        analysis = self.dmaic_handler.interact(prompt)

        # Extract structured data from the analysis
        return {
            "build_logs_summary": build_logs[:500] + "..." if len(build_logs) > 500 else build_logs,
            "analysis": analysis,
            "recommendations": self._extract_recommendations(analysis)
        }

    def compare_with_baseline(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current metrics with baseline to measure improvement"""
        if not self.baseline_metrics:
            return {"status": "error", "message": "No baseline metrics established", "comparison": {}, "improvements": {}, "overall_improvement_score": 0, "summary": "No baseline metrics available for comparison."}

        comparison = {}
        improvements = {}

        for metric_name, current_value in current_metrics.items():
            if metric_name in self.baseline_metrics:
                baseline_value = self.baseline_metrics[metric_name]

                try:
                    metric_enum = PipelineMetrics(metric_name)
                except ValueError:
                    metric_enum = None  # Metric not in our defined enum

                diff = 0
                pct_change = 0
                is_improvement = None

                if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                    diff = current_value - baseline_value
                    if baseline_value != 0:
                        pct_change = (diff / baseline_value) * 100
                    else:
                        pct_change = float('inf') if diff > 0 else (float('-inf') if diff < 0 else 0)

                    if metric_enum:
                        if metric_enum.lower_is_better:
                            is_improvement = diff < 0
                        else:
                            is_improvement = diff > 0
                    elif metric_enum is None and diff != 0:
                        is_improvement = diff > 0

                comparison[metric_name] = {
                    "baseline": baseline_value,
                    "current": current_value,
                    "difference": diff if isinstance(current_value, (int, float)) else "N/A",
                    "percent_change": f"{pct_change:.2f}%" if isinstance(current_value, (int, float)) else "N/A"
                }

                if is_improvement is not None:
                    improvements[metric_name] = is_improvement

        overall_score = 0
        if improvements:
            num_comparable_metrics = len([imp for imp in improvements.values() if imp is not None])
            if num_comparable_metrics > 0:
                overall_score = sum(1 if improved else (-1 if improved is False else 0) for improved in improvements.values()) / num_comparable_metrics

        return {
            "status": "success",
            "message": "Metrics comparison complete.",
            "comparison": comparison,
            "improvements": improvements,
            "overall_improvement_score": overall_score,
            "summary": self._generate_improvement_summary(comparison, improvements)
        }

    def generate_report(self, project_data: Dict[str, Any], report_type: str = "full") -> str:
        """Generate a comprehensive DMAIC CI/CD improvement report"""
        report_prompt = (
            f"Generate a {report_type} DMAIC report for a CI/CD pipeline improvement project.\n"
            f"Project data:\n{json.dumps(project_data, indent=2)}\n\n"
            f"The report should follow the DMAIC structure and include key findings, metrics, and recommendations."
        )

        report = self.dmaic_handler.interact(report_prompt)

        # Save report to output
        report_filename = f"dmaic_cicd_report_{time.strftime('%Y%m%d_%H%M%S')}.md"
        report_path = self.output_handler.save_results(
            {"report_content": report, "project_data": project_data},
            report_filename
        )

        return report_path

    def _extract_metrics_from_pipeline(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant metrics from pipeline data"""
        metrics = {}

        # Extract build time if available
        if "build_duration" in pipeline_data:
            metrics[PipelineMetrics.BUILD_TIME.value] = pipeline_data["build_duration"]
        elif "start_time" in pipeline_data and "end_time" in pipeline_data:
            try:
                start = pipeline_data["start_time"]
                end = pipeline_data["end_time"]
                if isinstance(start, (int, float)) and isinstance(end, (int, float)):
                    metrics[PipelineMetrics.BUILD_TIME.value] = end - start
            except (TypeError, ValueError):
                pass

        # Extract test metrics if available
        if "test_results" in pipeline_data:
            test_data = pipeline_data["test_results"]

            if isinstance(test_data, dict):
                if "coverage" in test_data:
                    metrics[PipelineMetrics.TEST_COVERAGE.value] = test_data["coverage"]

                if "total" in test_data and "passed" in test_data:
                    total = test_data["total"]
                    passed = test_data["passed"]
                    if total > 0:
                        metrics[PipelineMetrics.TEST_SUCCESS_RATE.value] = (passed / total) * 100

        # Extract deployment metrics if available
        if "deployments" in pipeline_data:
            deployments = pipeline_data["deployments"]
            metrics[PipelineMetrics.DEPLOYMENT_FREQUENCY.value] = len(deployments)

            if "lead_time" in pipeline_data:
                metrics[PipelineMetrics.LEAD_TIME.value] = pipeline_data["lead_time"]

            if "failures" in pipeline_data and "total" in pipeline_data:
                total = pipeline_data["total"]
                failures = pipeline_data["failures"]
                if total > 0:
                    metrics[PipelineMetrics.CHANGE_FAILURE_RATE.value] = (failures / total) * 100

        return metrics

    def _summarize_pipeline_runs(self, pipeline_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from multiple pipeline runs"""
        if not pipeline_runs:
            return {}

        summary = {
            "total_runs": len(pipeline_runs),
            "successful_runs": 0,
            "failed_runs": 0,
            "avg_build_time": 0,
            "avg_test_success_rate": 0,
            "trends": {},
            "common_failures": {}
        }

        build_times = []
        test_success_rates = []
        failure_reasons = {}

        # Process each run
        for run in pipeline_runs:
            # Count successes/failures
            if run.get("status") == "success":
                summary["successful_runs"] += 1
            else:
                summary["failed_runs"] += 1
                # Track failure reasons
                reason = run.get("failure_reason", "unknown")
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

            # Track build times
            if "build_duration" in run:
                build_times.append(run["build_duration"])

            # Track test success rates
            if "test_results" in run and "success_rate" in run["test_results"]:
                test_success_rates.append(run["test_results"]["success_rate"])

        # Calculate averages
        if build_times:
            summary["avg_build_time"] = sum(build_times) / len(build_times)

        if test_success_rates:
            summary["avg_test_success_rate"] = sum(test_success_rates) / len(test_success_rates)

        # Find common failures
        summary["common_failures"] = sorted(
            [{reason: count} for reason, count in failure_reasons.items()],
            key=lambda x: list(x.values())[0],
            reverse=True
        )[:5]  # Top 5 failure reasons

        # Identify trends if enough data
        if len(pipeline_runs) >= 5:
            # Simple trend analysis for build time
            if len(build_times) >= 5:
                first_half = build_times[:len(build_times)//2]
                second_half = build_times[len(build_times)//2:]
                avg_first = sum(first_half) / len(first_half)
                avg_second = sum(second_half) / len(second_half)
                summary["trends"]["build_time"] = "increasing" if avg_second > avg_first else "decreasing"

            # Success rate trend
            success_rate = summary["successful_runs"] / summary["total_runs"] * 100
            summary["success_rate"] = success_rate

        return summary

    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract actionable recommendations from analysis text"""
        recommendations = []

        # Look for recommendation patterns in text
        lines = analysis.split('\n')
        in_recommendations_section = False

        for line in lines:
            line = line.strip()

            # Check if we're entering a recommendations section
            if any(header in line.lower() for header in ["recommendation", "suggest", "solution"]):
                if any(header_marker in line for header_marker in [":", "#", "-"]):
                    in_recommendations_section = True
                    continue

            # Extract numbered or bulleted recommendations
            if in_recommendations_section or any(marker in line[:2] for marker in ["- ", "• ", "* ", "1.", "2.", "3."]):
                if line and not line.startswith("#") and len(line) > 5:
                    # Clean up the recommendation
                    recommendation = line
                    for prefix in ["- ", "• ", "* ", "1. ", "2. ", "3. ", "4. ", "5. "]:
                        if recommendation.startswith(prefix):
                            recommendation = recommendation[len(prefix):]
                            break

                    if recommendation and recommendation not in recommendations:
                        recommendations.append(recommendation)

        # If no structured recommendations found, try to extract sentences with recommendation keywords
        if not recommendations:
            for line in lines:
                if any(keyword in line.lower() for keyword in ["recommend", "should", "could", "improve", "fix", "solve"]):
                    recommendations.append(line.strip())

        # Limit to top 5 recommendations
        return recommendations[:5]

    def _generate_improvement_summary(self, comparison: Dict[str, Any], improvements: Dict[str, bool]) -> str:
        """Generate a human-readable summary of improvements"""
        improved_metrics = [k for k, v in improvements.items() if v]
        degraded_metrics = [k for k, v in improvements.items() if not v]

        if not comparison:
            return "No comparison data available."

        summary = []

        # Add overall statement
        if len(improved_metrics) > len(degraded_metrics):
            summary.append("Overall, the CI/CD pipeline has improved since the baseline measurement.")
        elif len(improved_metrics) < len(degraded_metrics):
            summary.append("Overall, the CI/CD pipeline has degraded since the baseline measurement.")
        else:
            summary.append("The CI/CD pipeline shows mixed results compared to the baseline.")

        # Add details for improved metrics
        if improved_metrics:
            summary.append("\nImprovements:")
            for metric in improved_metrics:
                data = comparison[metric]
                summary.append(f"- {metric}: {data['baseline']} → {data['current']} ({data['percent_change']} change)")

        # Add details for degraded metrics
        if degraded_metrics:
            summary.append("\nAreas for further improvement:")
            for metric in degraded_metrics:
                data = comparison[metric]
                summary.append(f"- {metric}: {data['baseline']} → {data['current']} ({data['percent_change']} change)")

        return "\n".join(summary)

    # New Message Handlers
    def handle_generate_improvement_plan(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["analysis_results"]):
            return {"status": "error", "message": "Missing analysis_results.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        analysis_results = content["analysis_results"]
        try:
            improve_outputs = self.generate_improvement_plan(analysis_results)
            md_content = f"### CI/CD Improvement Plan Generated\n\n**Proposed Solutions:**\n{improve_outputs.get('proposed_solutions', 'N/A')}\n\n**Roadmap:**\n{improve_outputs.get('prioritized_roadmap', 'N/A')}"
            return {"status": "success", "message": "Improvement plan generated.", "data": improve_outputs, "error_details": None, "markdown_content": md_content}
        except Exception as e:
            return {"status": "error", "message": "Failed to generate improvement plan.", "data": None, "error_details": str(e), "markdown_content": None}

    def handle_establish_control_plan(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["improvement_results"]):
            return {"status": "error", "message": "Missing improvement_results.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        improvement_results = content["improvement_results"]
        try:
            control_outputs = self.establish_control_plan(improvement_results)
            md_content = f"### CI/CD Control Plan Established\n\n**Control Metrics:**\n{control_outputs.get('control_metrics', 'N/A')}\n\n**Monitoring Plan:**\n{control_outputs.get('monitoring_plan', 'N/A')}"
            return {"status": "success", "message": "Control plan established.", "data": control_outputs, "error_details": None, "markdown_content": md_content}
        except Exception as e:
            return {"status": "error", "message": "Failed to establish control plan.", "data": None, "error_details": str(e), "markdown_content": None}

    def handle_analyze_build_failure(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["build_logs"]):
            return {"status": "error", "message": "Missing build_logs.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        build_logs = content["build_logs"]
        try:
            analysis_outputs = self.analyze_build_failure(build_logs)
            md_content = f"### Build Failure Analysis\n\n**Analysis:**\n{analysis_outputs.get('analysis', 'N/A')}\n\n**Recommendations:**\n"
            md_content += "\n".join([f"- {rec}" for rec in analysis_outputs.get('recommendations', [])])
            return {"status": "success", "message": "Build failure analyzed.", "data": analysis_outputs, "error_details": None, "markdown_content": md_content}
        except Exception as e:
            return {"status": "error", "message": "Failed to analyze build failure.", "data": None, "error_details": str(e), "markdown_content": None}

    def handle_compare_metrics(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["current_metrics"]):
            return {"status": "error", "message": "Missing current_metrics.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        current_metrics = content["current_metrics"]
        try:
            comparison_outputs = self.compare_with_baseline(current_metrics)
            if comparison_outputs.get("status") == "error":  # Pass through error from compare_with_baseline
                return {"status": "error", "message": comparison_outputs["message"], "data": None, "error_details": comparison_outputs.get("message"), "markdown_content": None}

            md_content = f"### CI/CD Metrics Comparison\n\n{comparison_outputs.get('summary', 'No summary available.')}"
            return {"status": "success", "message": "Metrics comparison complete.", "data": comparison_outputs, "error_details": None, "markdown_content": md_content}
        except Exception as e:
            return {"status": "error", "message": "Failed to compare metrics.", "data": None, "error_details": str(e), "markdown_content": None}
