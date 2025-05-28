"""
Requirement Analyzer Agents for the RTM Automation system.

Provides agents for analyzing requirements and traceability.
"""

import logging
import re
import sys  # Added import
import os  # Added import
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import modules from project
# These imports are placed after sys.path modification
from agents.agent_common import BaseAgent, AgentRole, AgentCapability, AgentMessage  # pylint: disable=wrong-import-position # noqa: E402
from services.openai_service import OpenAIService  # pylint: disable=wrong-import-position # noqa: E402
from utils.output_handler import OutputHandler  # pylint: disable=wrong-import-position # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RequirementAnalysisAgent(BaseAgent):
    """
    Agent for analyzing requirements.

    This agent provides functionality for:
    - Requirements extraction and validation
    - Requirements quality assessment
    - Impact analysis for requirement changes
    """

    def __init__(self,
                 openai_service: OpenAIService = None,
                 output_handler: OutputHandler = None,
                 config: Dict[str, Any] = None):
        """
        Initialize the RequirementAnalysisAgent.

        Args:
            openai_service: OpenAI service for advanced analysis
            output_handler: Output handler for logging and reporting
            config: Configuration dictionary
        """
        super().__init__()
        self.agent_id = config.get("agent_id", "default_id")
        self.role = AgentRole.ANALYSER
        self.capabilities = [
            AgentCapability.REQUIREMENT_ANALYSIS,
            AgentCapability.IMPACT_ANALYSIS
        ]
        self.openai_service = openai_service
        self.output_handler = output_handler
        self.status = "initialized"

        # Define regex patterns for requirement identification
        self.req_pattern = re.compile(r"REQ-\d+(?:-\d+)*")

        if output_handler:
            self.output_handler.log_info(
                "RequirementAnalyzerAgent %s initialized", self.agent_id
            )
        else:
            logger.info(
                "RequirementAnalyzerAgent %s initialized without output_handler",
                self.agent_id
            )

    def process_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Process incoming messages directed to this agent.

        Args:
            message: The message to process

        Returns:
            Response dictionary with results
        """
        if message.message_type == "extract_requirements_request":
            return self._handle_extract_requirements(message.content)
        elif message.message_type == "validate_requirements_request":
            return self._handle_validate_requirements(message.content)
        elif message.message_type == "impact_analysis_request":
            return self._handle_impact_analysis(message.content)
        else:
            return {
                "status": "error",
                "message": f"Unsupported message type: {message.message_type}"
            }

    def _handle_extract_requirements(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to extract requirements from content."""
        file_path = content.get("file_path")
        text_content = content.get("content")

        if not file_path and not text_content:
            return {"status": "error", "message": "No file path or content provided"}

        try:
            if text_content:
                requirements = self.extract_requirements_from_text(text_content)
            else:
                requirements = self.extract_requirements_from_file(file_path)

            return {
                "status": "success",
                "message": "Requirements extracted successfully",
                "data": {"requirements": requirements}
            }
        except Exception as e:  # pylint: disable=broad-except
            return {"status": "error", "message": f"Failed to extract requirements: {e}"}

    def _handle_validate_requirements(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to validate requirements."""
        requirements = content.get("requirements", [])

        if not requirements:
            return {"status": "error", "message": "No requirements provided"}

        try:
            validation_results = self.validate_requirements(requirements)
            return {
                "status": "success",
                "message": "Requirements validated successfully",
                "data": {"validation_report": validation_results}
            }
        except Exception as e:  # pylint: disable=broad-except
            return {"status": "error", "message": f"Failed to validate requirements: {e}"}

    def _handle_impact_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to analyze impact of requirement changes."""
        # Placeholder implementation for impact analysis
        changed_requirements = content.get("changed_requirements", [])
        all_requirements = content.get("all_requirements", [])

        if not changed_requirements:
            return {
                "status": "error",
                "message": "No changed requirements provided for impact analysis"
            }

        try:
            analysis_result = self.analyze_impact(changed_requirements, all_requirements)
            return {
                "status": "success",
                "message": "Impact analysis completed",
                "data": analysis_result
            }
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error during impact analysis: %s", e)
            return {"status": "error", "message": f"Impact analysis failed: {e}"}

    def extract_requirements_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract requirements from a file.

        Args:
            file_path: Path to the file

        Returns:
            List of extracted requirements
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.extract_requirements_from_text(content)
        except Exception as e:  # pylint: disable=broad-except
            if self.output_handler:
                self.output_handler.log_error("Error reading file %s: %s", file_path, e)
            raise

    def extract_requirements_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract requirements from text content.

        Args:
            text: Text content to extract requirements from

        Returns:
            List of extracted requirements
        """
        requirements = []

        # Find all requirement IDs in the text
        req_ids = set(self.req_pattern.findall(text))

        # For each requirement ID, extract the surrounding text
        for req_id in req_ids:
            # Find lines containing the requirement ID
            lines = text.splitlines()
            for i, line in enumerate(lines):
                if req_id in line:
                    # Extract description from the line
                    description = line.replace(req_id, "").strip()
                    if ":" in description:
                        description = description.split(":", 1)[1].strip()

                    # Check if there's additional content in the next line
                    additional_content = ""
                    if i + 1 < len(lines) and not self.req_pattern.search(lines[i + 1]):
                        additional_content = lines[i + 1].strip()

                    requirements.append({
                        "id": req_id,
                        "description": description,
                        "additional_content": additional_content,
                        "line_number": i + 1
                    })
                    break

        return requirements

    def validate_requirements(self, requirements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate a list of requirements.

        Args:
            requirements: List of requirements to validate

        Returns:
            List of validation results for each requirement
        """
        validation_results = []

        for req in requirements:
            # Check for empty description
            has_description = bool(req.get("description", "").strip())

            # Check for SMART criteria
            # (Specific, Measurable, Achievable, Relevant, Time-bound)
            description = req.get("description", "")
            is_specific = len(description.split()) > 3  # Very basic check
            has_measurable = any(word in description.lower() for word in ["measure", "count", "percent", "number"])

            # Overall quality score (very simplified)
            quality_score = sum([
                5 if has_description else 0,
                2 if is_specific else 0,
                3 if has_measurable else 0
            ])

            validation_results.append({
                "id": req.get("id"),
                "has_description": has_description,
                "is_specific": is_specific,
                "has_measurable_criteria": has_measurable,
                "quality_score": quality_score,
                "max_score": 10,
                "issues": self._get_requirement_issues(req)
            })

        return validation_results

    def _get_requirement_issues(self, requirement: Dict[str, Any]) -> List[str]:
        """Identify issues in a requirement."""
        issues = []
        description = requirement.get("description", "")

        if not description:
            issues.append("Missing description")
            return issues

        # Check for ambiguous words
        ambiguous_words = ["may", "might", "could", "should", "would", "can", "optionally"]
        found_ambiguous = [word for word in ambiguous_words if f" {word} " in f" {description} "]
        if found_ambiguous:
            issues.append(f"Contains ambiguous words: {', '.join(found_ambiguous)}")

        # Check for length
        if len(description) < 10:
            issues.append("Description too short")
        elif len(description) > 200:
            issues.append(
                "Description too long (consider breaking into multiple requirements)"
            )

        return issues

    def analyze_impact(self, changed_requirements: List[Dict[str, Any]],
                       all_requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the impact of changing requirements.

        Args:
            changed_requirements: List of requirements that are changing
            all_requirements: List of all requirements in the system

        Returns:
            Impact analysis results
        """
        # For a real implementation, we would need traceability information
        # This is a simplified version based just on text similarity

        changed_ids = [req.get("id") for req in changed_requirements]

        # Find potentially affected requirements (simplified)
        potentially_affected = []
        for req in all_requirements:
            if req.get("id") in changed_ids:
                continue  # Skip the changed requirements themselves

            # Look for references to changed requirements in the description
            description = req.get("description", "")
            for changed_id in changed_ids:
                if changed_id in description:
                    potentially_affected.append(req.get("id"))
                    break

        # Calculate risk metrics
        risk_level = "low"
        if len(potentially_affected) > 10:
            risk_level = "high"
        elif len(potentially_affected) > 3:
            risk_level = "medium"

        return {
            "changed_requirements": changed_ids,
            "potentially_affected_requirements": potentially_affected,
            "impact_count": len(potentially_affected),
            "risk_level": risk_level,
            "recommendations": self._get_impact_recommendations(risk_level, len(potentially_affected))
        }

    def _get_impact_recommendations(self, risk_level: str, impact_count: int) -> List[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []

        if risk_level == "high":
            recommendations.append(
                "Perform a full review of all affected requirements "
                "and consider breaking the change into smaller increments"
            )
            recommendations.append("Update test cases for all affected requirements")
        elif risk_level == "medium":
            recommendations.append("Review the affected requirements carefully")
            recommendations.append("Update relevant test cases")
        else:
            recommendations.append("Proceed with the changes as planned")
            if impact_count > 0:
                recommendations.append("Notify the owners of affected requirements")

        return recommendations
