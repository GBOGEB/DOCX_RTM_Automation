"""
DMAIC CI/CD Agent for the RTM Automation system.
Handles CI/CD operations in the DMAIC framework.
"""

import os
import sys
import logging
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import base agent components
from agents.agent_common import BaseAgent, AgentRole, AgentCapability, AgentMessage, validate_input
from dmaic import DMAICHandler, DMAICPhase
from utils.output_handler import OutputHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


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
    Agent for handling CI/CD operations within the DMAIC framework.

    This agent monitors and manages CI/CD operations across the DMAIC phases:
    - Define: Set up repository structure and initial CI pipeline
    - Measure: Capture metrics and generate reports
    - Analyze: Analyze metrics and generate insights
    - Improve: Implement improvements and verify results
    - Control: Monitor long-term performance and maintain improvements
    """

    def __init__(self, dmaic_handler: Optional[DMAICHandler] = None, output_handler: Optional[OutputHandler] = None):
        """
        Initialize the DMAICCICDAgent.

        Args:
            dmaic_handler: DMAIC handler for accessing project context
            output_handler: Output handler for logging and reporting
        """
        super().__init__()
        self.agent_id = "dmaic_cicd_agent"
        self.role = AgentRole.ANALYST
        self.capabilities = [
            AgentCapability.GIT_OPERATIONS,
            AgentCapability.VERSION_CONTROL,
            AgentCapability.CICD_PIPELINE_ANALYSIS,
            AgentCapability.CICD_METRICS_COLLECTION,
            AgentCapability.CICD_IMPROVEMENT_PLANNING,
            AgentCapability.CICD_BUILD_FAILURE_ANALYSIS
        ]
        self.dmaic_handler = dmaic_handler
        self.output_handler = output_handler
        self.status = "initialized"
        self.pipeline_metrics: Dict[str, Any] = {}
        self.improvement_iterations = 0
        self.baseline_metrics: Dict[str, Any] = {}

        if output_handler:
            self.output_handler.log_info(f"DMAICCICDAgent {self.agent_id} initialized")
        else:
            logger.info(f"DMAICCICDAgent {self.agent_id} initialized without output_handler")

    def process_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Process incoming messages directed to this agent.

        Args:
            message: The message to process

        Returns:
            Response dictionary with results
        """
        if message.message_type == "dmaic_phase_change":
            return self._handle_phase_change(message.content)
        elif message.message_type == "setup_pipeline_request":
            return self._handle_setup_pipeline(message.content)
        elif message.message_type == "run_pipeline_request":
            return self._handle_run_pipeline(message.content)
        elif message.message_type == "deploy_request":
            return self._handle_deploy(message.content)
        elif message.message_type == "initialize_cicd_project":
            return self.handle_initialize_project(message)
        elif message.message_type == "collect_cicd_baseline":
            return self.handle_collect_baseline_metrics(message)
        elif message.message_type == "analyze_cicd_performance":
            return self.handle_analyze_pipeline_performance(message)
        elif message.message_type == "generate_cicd_improvement_plan":
            return self.handle_generate_improvement_plan(message)
        elif message.message_type == "establish_cicd_control_plan":
            return self.handle_establish_control_plan(message)
        elif message.message_type == "analyze_cicd_build_failure":
            return self.handle_analyze_build_failure(message)
        elif message.message_type == "compare_cicd_metrics":
            return self.handle_compare_metrics(message)
        else:
            return {
                "status": "error",
                "message": f"Unsupported message type: {message.message_type}"
            }

    def _handle_phase_change(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DMAIC phase change notifications."""
        phase = content.get("phase")

        if not phase:
            return {"status": "error", "message": "No phase specified"}

        if self.dmaic_handler:
            self.dmaic_handler.set_phase(phase)

            if self.output_handler:
                self.output_handler.log_info(f"DMAIC phase changed to {phase}")

            return {
                "status": "success",
                "message": f"Phase changed to {phase}",
                "data": {"phase": phase}
            }
        else:
            return {
                "status": "error",
                "message": "DMAIC handler not available"
            }

    def _handle_setup_pipeline(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to set up CI/CD pipeline."""
        repo_path = content.get("repo_path")
        pipeline_type = content.get("pipeline_type", "standard")

        if not repo_path:
            return {"status": "error", "message": "Repository path required"}

        try:
            # In a real implementation, this would set up pipeline config files
            if self.output_handler:
                self.output_handler.log_info(f"Setting up {pipeline_type} pipeline in {repo_path}")

            # Simulate pipeline setup
            pipeline_config = {
                "type": pipeline_type,
                "repo": repo_path,
                "stages": ["build", "test", "deploy"],
                "active": True
            }

            return {
                "status": "success",
                "message": f"Pipeline setup successfully",
                "data": pipeline_config
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to set up pipeline: {e}"}

    def _handle_run_pipeline(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to run CI/CD pipeline."""
        pipeline_id = content.get("pipeline_id")

        if not pipeline_id:
            return {"status": "error", "message": "Pipeline ID required"}

        try:
            # In a real implementation, this would trigger a pipeline run
            if self.output_handler:
                self.output_handler.log_info(f"Running pipeline {pipeline_id}")

            # Simulate pipeline run
            run_result = {
                "pipeline_id": pipeline_id,
                "run_id": f"run_{int(time.time())}",
                "status": "success",
                "stages": [
                    {"name": "build", "status": "success", "duration_sec": 45},
                    {"name": "test", "status": "success", "duration_sec": 120},
                    {"name": "deploy", "status": "success", "duration_sec": 30}
                ]
            }

            return {
                "status": "success",
                "message": f"Pipeline run successfully",
                "data": run_result
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to run pipeline: {e}"}

    def _handle_deploy(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to deploy to an environment."""
        environment = content.get("environment", "development")
        artifact_id = content.get("artifact_id")

        if not artifact_id:
            return {"status": "error", "message": "Artifact ID required"}

        try:
            # In a real implementation, this would perform deployment
            if self.output_handler:
                self.output_handler.log_info(f"Deploying artifact {artifact_id} to {environment}")

            # Simulate deployment
            deployment_result = {
                "environment": environment,
                "artifact_id": artifact_id,
                "deployment_id": f"deploy_{int(time.time())}",
                "status": "success",
                "timestamp": time.time()
            }

            return {
                "status": "success",
                "message": f"Deployment to {environment} successful",
                "data": deployment_result
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to deploy: {e}"}
