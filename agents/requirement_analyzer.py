"""
Requirement Analyzer Agents for the RTM Automation system.

Provides agents for analyzing requirements and traceability.
"""

import os
import re
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import base agent components
from agents.agent_common import BaseAgent, AgentRole, AgentCapability, AgentMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RequirementAnalysisAgent(BaseAgent):
    """
    Agent for analyzing requirements.

    This agent provides functionality for:
    - Requirements extraction and validation
    - Requirements quality assessment
    - Impact analysis for requirement changes
    """

    def __init__(self, agent_id: str, output_handler=None):
        """
        Initialize the RequirementAnalysisAgent.

        Args:
            agent_id: Unique identifier for this agent
            output_handler: Output handler for logging and reporting
        """
        super().__init__()
        self.agent_id = agent_id
        self.role = AgentRole.ANALYSER
        self.capabilities = [
            AgentCapability.REQUIREMENT_ANALYSIS,
            AgentCapability.IMPACT_ANALYSIS
        ]
        self.output_handler = output_handler
        self.status = "initialized"

        # Define regex patterns for requirement identification
        self.req_pattern = re.compile(r"REQ-\d+(?:-\d+)*")

        if output_handler:
            self.output_handler.log_info(f"RequirementAnalysisAgent {agent_id} initialized")
        else:
            logger.info(f"RequirementAnalysisAgent {agent_id} initialized without output_handler")

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
                "message": f"Extracted {len(requirements)} requirements",
                "data": {"requirements": requirements}
            }
        except Exception as e:
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
                "message": f"Validated {len(requirements)} requirements",
                "data": {"validation_results": validation_results}
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to validate requirements: {e}"}

    def _handle_impact_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request for impact analysis."""
        changed_requirements = content.get("changed_requirements", [])
        all_requirements = content.get("all_requirements", [])

        if not changed_requirements:
            return {"status": "error", "message": "No changed requirements provided"}

        try:
            impact_analysis = self.analyze_impact(changed_requirements, all_requirements)
            return {
                "status": "success",
                "message": f"Analyzed impact for {len(changed_requirements)} requirements",
                "data": {"impact_analysis": impact_analysis}
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to analyze impact: {e}"}

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
        except Exception as e:
            if self.output_handler:
                self.output_handler.log_error(f"Error reading file {file_path}: {e}")
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
            issues.append("Description too long (consider breaking into multiple requirements)")

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
            recommendations.append("Perform a full review of all affected requirements")
            recommendations.append("Consider breaking the change into smaller increments")
            recommendations.append("Update test cases for all affected requirements")
        elif risk_level == "medium":
            recommendations.append("Review the affected requirements carefully")
            recommendations.append("Update relevant test cases")
        else:
            recommendations.append("Proceed with the changes as planned")
            if impact_count > 0:
                recommendations.append("Notify the owners of affected requirements")

        return recommendations


class TraceabilityAnalysisAgent(BaseAgent):
    """
    Agent for analyzing requirement traceability.

    This agent provides functionality for:
    - Analyzing traceability between requirements and test cases
    - Generating traceability matrices
    - Identifying gaps in coverage
    """

    def __init__(self, agent_id: str, output_handler=None):
        """
        Initialize the TraceabilityAnalysisAgent.

        Args:
            agent_id: Unique identifier for this agent
            output_handler: Output handler for logging and reporting
        """
        super().__init__()
        self.agent_id = agent_id
        self.role = AgentRole.ANALYSER
        self.capabilities = [
            AgentCapability.TRACEABILITY_ANALYSIS
        ]
        self.output_handler = output_handler
        self.status = "initialized"

        # Define regex patterns
        self.req_pattern = re.compile(r"REQ-\d+(?:-\d+)*")
        self.test_pattern = re.compile(r"TC-\d+(?:-\d+)*")

        if output_handler:
            self.output_handler.log_info(f"TraceabilityAnalysisAgent {agent_id} initialized")
        else:
            logger.info(f"TraceabilityAnalysisAgent {agent_id} initialized without output_handler")

    def process_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Process incoming messages directed to this agent.

        Args:
            message: The message to process

        Returns:
            Response dictionary with results
        """
        if message.message_type == "analyze_traceability_request":
            return self._handle_analyze_traceability(message.content)
        elif message.message_type == "generate_matrix_request":
            return self._handle_generate_matrix(message.content)
        elif message.message_type == "analyze_coverage_request":
            return self._handle_analyze_coverage(message.content)
        else:
            return {
                "status": "error",
                "message": f"Unsupported message type: {message.message_type}"
            }

    def _handle_analyze_traceability(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to analyze traceability."""
        files = content.get("files", [])
        directory = content.get("directory")

        if not files and not directory:
            return {"status": "error", "message": "No files or directory provided"}

        try:
            if directory:
                traceability_data = self.analyze_directory_traceability(directory)
            else:
                traceability_data = self.analyze_files_traceability(files)

            return {
                "status": "success",
                "message": "Traceability analysis completed",
                "data": traceability_data
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to analyze traceability: {e}"}

    def _handle_generate_matrix(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to generate a traceability matrix."""
        traceability_data = content.get("traceability_data")
        output_format = content.get("output_format", "html")

        if not traceability_data:
            return {"status": "error", "message": "No traceability data provided"}

        try:
            matrix_data = self.generate_traceability_matrix(traceability_data, output_format)
            return {
                "status": "success",
                "message": f"Generated {output_format} traceability matrix",
                "data": {"matrix": matrix_data}
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to generate traceability matrix: {e}"}

    def _handle_analyze_coverage(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request to analyze requirement coverage."""
        traceability_data = content.get("traceability_data")

        if not traceability_data:
            return {"status": "error", "message": "No traceability data provided"}

        try:
            coverage_data = self.analyze_coverage(traceability_data)
            return {
                "status": "success",
                "message": "Coverage analysis completed",
                "data": {"coverage": coverage_data}
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to analyze coverage: {e}"}

    def analyze_directory_traceability(self, directory: str) -> Dict[str, Any]:
        """
        Analyze traceability in all files within a directory.

        Args:
            directory: Directory path to analyze

        Returns:
            Traceability data
        """
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Not a directory: {directory}")

        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(('.md', '.txt')):
                    files.append(os.path.join(root, filename))

        return self.analyze_files_traceability(files)

    def analyze_files_traceability(self, files: List[str]) -> Dict[str, Any]:
        """
        Analyze traceability in a list of files.

        Args:
            files: List of file paths

        Returns:
            Traceability data
        """
        requirements = {}
        test_cases = {}
        links = []

        for file_path in files:
            if not os.path.exists(file_path):
                if self.output_handler:
                    self.output_handler.log_warning(f"File not found: {file_path}")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract requirements
                req_ids = set(self.req_pattern.findall(content))
                for req_id in req_ids:
                    if req_id not in requirements:
                        requirements[req_id] = {
                            "id": req_id,
                            "files": [file_path],
                            "description": self._extract_description(content, req_id)
                        }
                    else:
                        requirements[req_id]["files"].append(file_path)

                # Extract test cases
                test_ids = set(self.test_pattern.findall(content))
                for test_id in test_ids:
                    if test_id not in test_cases:
                        test_cases[test_id] = {
                            "id": test_id,
                            "files": [file_path],
                            "description": self._extract_description(content, test_id)
                        }
                    else:
                        test_cases[test_id]["files"].append(file_path)

                # Extract links
                # Look for patterns like "REQ-123 -> TC-456" or similar
                lines = content.splitlines()
                for line in lines:
                    req_matches = list(self.req_pattern.finditer(line))
                    test_matches = list(self.test_pattern.finditer(line))

                    if len(req_matches) > 0 and len(test_matches) > 0:
                        # There's both a requirement and test case on this line
                        for req_match in req_matches:
                            req_id = req_match.group()
                            for test_match in test_matches:
                                test_id = test_match.group()

                                # Determine link type based on syntax
                                if "->" in line:
                                    parts = line.split("->")
                                    if req_id in parts[0] and test_id in parts[1]:
                                        link_type = "validates"
                                    elif test_id in parts[0] and req_id in parts[1]:
                                        link_type = "verifies"
                                    else:
                                        link_type = "related"
                                else:
                                    link_type = "related"

                                links.append({
                                    "source": req_id if link_type == "validates" else test_id,
                                    "target": test_id if link_type == "validates" else req_id,
                                    "type": link_type,
                                    "file": file_path
                                })

            except Exception as e:
                if self.output_handler:
                    self.output_handler.log_error(f"Error analyzing file {file_path}: {e}")

        return {
            "requirements": requirements,
            "test_cases": test_cases,
            "links": links,
            "stats": {
                "requirement_count": len(requirements),
                "test_case_count": len(test_cases),
                "link_count": len(links)
            }
        }

    def _extract_description(self, content: str, item_id: str) -> str:
        """Extract description for a requirement or test case."""
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if item_id in line:
                # Extract description from the line
                parts = line.split(item_id, 1)
                if len(parts) > 1:
                    description = parts[1].strip()
                    if description.startswith(":"):
                        description = description[1:].strip()
                    return description
        return ""

    def generate_traceability_matrix(self, traceability_data: Dict[str, Any],
                                     output_format: str = "html") -> Dict[str, Any]:
        """
        Generate a traceability matrix.

        Args:
            traceability_data: Traceability data
            output_format: Output format (html, markdown, etc.)

        Returns:
            Matrix data in the specified format
        """
        requirements = traceability_data.get("requirements", {})
        test_cases = traceability_data.get("test_cases", {})
        links = traceability_data.get("links", [])

        # Create a mapping of which test cases verify which requirements
        req_to_tests = {}
        test_to_reqs = {}

        for link in links:
            source = link.get("source", "")
            target = link.get("target", "")
            link_type = link.get("type", "")

            if link_type == "validates" and source in requirements and target in test_cases:
                if source not in req_to_tests:
                    req_to_tests[source] = []
                req_to_tests[source].append(target)

                if target not in test_to_reqs:
                    test_to_reqs[target] = []
                test_to_reqs[target].append(source)
            elif link_type == "verifies" and source in test_cases and target in requirements:
                if target not in req_to_tests:
                    req_to_tests[target] = []
                req_to_tests[target].append(source)

                if source not in test_to_reqs:
                    test_to_reqs[source] = []
                test_to_reqs[source].append(target)

        # Format the matrix based on the requested output format
        if output_format == "html":
            return self._generate_html_matrix(requirements, test_cases, req_to_tests)
        elif output_format == "markdown":
            return self._generate_markdown_matrix(requirements, test_cases, req_to_tests)
        else:
            return {"error": f"Unsupported output format: {output_format}"}

    def _generate_html_matrix(self, requirements: Dict[str, Any], test_cases: Dict[str, Any],
                              req_to_tests: Dict[str, List[str]]) -> Dict[str, str]:
        """Generate an HTML traceability matrix."""
        req_ids = sorted(requirements.keys())
        test_ids = sorted(test_cases.keys())

        table_html = "<table border='1'>\n<tr><th>Requirement \\ Test</th>"

        # Header row with test case IDs
        for test_id in test_ids:
            table_html += f"<th>{test_id}</th>"
        table_html += "</tr>\n"

        # Rows for each requirement
        for req_id in req_ids:
            table_html += f"<tr><th>{req_id}</th>"

            for test_id in test_ids:
                if req_to_tests.get(req_id) and test_id in req_to_tests[req_id]:
                    table_html += "<td>X</td>"
                else:
                    table_html += "<td></td>"

            table_html += "</tr>\n"

        table_html += "</table>"

        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Traceability Matrix</title>
    <style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background-color: #f2f2f2; }}
        .covered {{ background-color: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Requirements Traceability Matrix</h1>
    <p>Total Requirements: {len(requirements)}</p>
    <p>Total Test Cases: {len(test_cases)}</p>
    {table_html}
</body>
</html>"""

        return {"html": full_html}

    def _generate_markdown_matrix(self, requirements: Dict[str, Any], test_cases: Dict[str, Any],
                                 req_to_tests: Dict[str, List[str]]) -> Dict[str, str]:
        """Generate a Markdown traceability matrix."""
        req_ids = sorted(requirements.keys())
        test_ids = sorted(test_cases.keys())

        table_md = "| Requirement \\ Test |"

        # Header row with test case IDs
        for test_id in test_ids:
            table_md += f" {test_id} |"
        table_md += "\n|---|"

        # Header separator row
        for _ in test_ids:
            table_md += "---|"
        table_md += "\n"

        # Rows for each requirement
        for req_id in req_ids:
            table_md += f"| {req_id} |"

            for test_id in test_ids:
                if req_to_tests.get(req_id) and test_id in req_to_tests[req_id]:
                    table_md += " X |"
                else:
                    table_md += " |"

            table_md += "\n"

        full_md = f"""# Requirements Traceability Matrix

## Summary

- **Total Requirements**: {len(requirements)}
- **Total Test Cases**: {len(test_cases)}

## Matrix

{table_md}
"""

        return {"markdown": full_md}

    def analyze_coverage(self, traceability_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze requirement coverage.

        Args:
            traceability_data: Traceability data

        Returns:
            Coverage analysis results
        """
        requirements = traceability_data.get("requirements", {})
        test_cases = traceability_data.get("test_cases", {})
        links = traceability_data.get("links", [])

        # Create a mapping of which test cases verify which requirements
        req_to_tests = {}

        for link in links:
            source = link.get("source", "")
            target = link.get("target", "")
            link_type = link.get("type", "")

            if link_type == "validates" and source in requirements and target in test_cases:
                if source not in req_to_tests:
                    req_to_tests[source] = []
                req_to_tests[source].append(target)
            elif link_type == "verifies" and source in test_cases and target in requirements:
                if target not in req_to_tests:
                    req_to_tests[target] = []
                req_to_tests[target].append(source)

        # Calculate coverage metrics
        covered_requirements = sum(1 for req_id in requirements if req_id in req_to_tests and req_to_tests[req_id])
        total_requirements = len(requirements)
        coverage_percent = (covered_requirements / total_requirements * 100) if total_requirements > 0 else 0

        # Identify uncovered requirements
        uncovered = [
            {
                "id": req_id,
                "description": requirements[req_id].get("description", "")
            }
            for req_id in requirements if req_id not in req_to_tests or not req_to_tests[req_id]
        ]

        return {
            "total_requirements": total_requirements,
            "covered_requirements": covered_requirements,
            "uncovered_requirements": len(uncovered),
            "coverage_percent": coverage_percent,
            "uncovered_details": uncovered,
            "status": self._get_coverage_status(coverage_percent)
        }

    def _get_coverage_status(self, coverage_percent: float) -> str:
        """Get status based on coverage percentage."""
        if coverage_percent >= 90:
            return "Excellent"
        elif coverage_percent >= 75:
            return "Good"
        elif coverage_percent >= 50:
            return "Fair"
        else:
            return "Poor"
