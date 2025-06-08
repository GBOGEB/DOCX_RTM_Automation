"""
Copilot Agent for the RTM Automation system.
Provides integration with GitHub Copilot or similar AI assistants.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import base agent components
from agents.agent_common import BaseAgent, AgentRole, AgentCapability, AgentMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CopilotAgent(BaseAgent):
    """
    Agent that integrates with GitHub Copilot or similar AI assistants.

    This agent provides capabilities like:
    - Code generation
    - Code analysis
    - Repository analysis
    - Report generation
    """

    def __init__(self, dmaic_handler=None, output_handler=None):
        """
        Initialize the CopilotAgent.

        Args:
            dmaic_handler: DMAIC handler for accessing project context
            output_handler: Output handler for logging and reporting
        """
        super().__init__()
        self.agent_id = "copilot_agent"
        self.role = AgentRole.ASSISTANT
        self.capabilities = [
            AgentCapability.CODE_GENERATION,
            AgentCapability.CODE_ANALYSIS,
            AgentCapability.DOCUMENT_PARSING,
            AgentCapability.DOCUMENT_GENERATION,
            AgentCapability.IMPACT_ANALYSIS,
        ]
        self.dmaic_handler = dmaic_handler
        self.output_handler = output_handler
        self.status = "initialized"

        if output_handler:
            self.output_handler.log_info(f"CopilotAgent {self.agent_id} initialized")
        else:
            logger.info(
                f"CopilotAgent {self.agent_id} initialized without output_handler"
            )

    def process_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Process incoming messages directed to this agent.

        Args:
            message: The message to process

        Returns:
            Response dictionary with results
        """
        if message.message_type == "code_generation_request":
            return self._handle_code_generation(message.content)
        elif message.message_type == "code_analysis_request":
            return self._handle_code_analysis(message.content)
        elif message.message_type == "repository_analysis_request":
            return self._handle_repository_analysis(message.content)
        elif message.message_type == "report_generation_request":
            return self._handle_report_generation(message.content)
        else:
            return {
                "status": "error",
                "message": f"Unsupported message type: {message.message_type}",
            }

    def _handle_code_generation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code generation requests."""
        language = content.get("language", "python")
        requirement = content.get("requirement", "")
        output_path = content.get("output_path", None)

        if not requirement:
            return {
                "status": "error",
                "message": "No requirement provided for code generation",
            }

        try:
            generated_code = self.generate_code(language, requirement, output_path)
            return {
                "status": "success",
                "message": "Code generated successfully",
                "data": {"code": generated_code},
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to generate code: {e}"}

    def _handle_code_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code analysis requests."""
        file_path = content.get("file_path", "")

        if not file_path or not os.path.exists(file_path):
            return {"status": "error", "message": f"Invalid file path: {file_path}"}

        try:
            analysis_result = self.analyze_code(file_path)
            return {
                "status": "success",
                "message": "Code analyzed successfully",
                "data": analysis_result,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to analyze code: {e}"}

    def _handle_repository_analysis(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle repository analysis requests."""
        repo_path = content.get("repo_path", "")

        if not repo_path or not os.path.exists(repo_path):
            return {
                "status": "error",
                "message": f"Invalid repository path: {repo_path}",
            }

        try:
            analysis_result = self.analyze_repository(repo_path)
            return {
                "status": "success",
                "message": "Repository analyzed successfully",
                "data": analysis_result,
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to analyze repository: {e}"}

    def _handle_report_generation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle report generation requests."""
        report_type = content.get("report_type", "")
        data = content.get("data", {})
        output_path = content.get("output_path", None)

        if not report_type:
            return {"status": "error", "message": "No report type specified"}

        try:
            report_content = self.generate_report(report_type, data, output_path)
            return {
                "status": "success",
                "message": "Report generated successfully",
                "data": {"report": report_content},
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to generate report: {e}"}

    def generate_code(
        self, language: str, requirement: str, output_path: Optional[str] = None
    ) -> str:
        """
        Generate code based on a requirement.

        Args:
            language: The programming language to generate code in
            requirement: The requirement to implement
            output_path: Path to save the generated code (optional)

        Returns:
            The generated code as a string
        """
        # In a real implementation, this would call the Copilot API or use another AI service
        # For now, we'll generate a simple stub based on the requirement
        if self.output_handler:
            self.output_handler.log_info(
                f"Generating {language} code for: {requirement}"
            )

        {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "csharp": "cs",
            "cpp": "cpp",
            "shell": "sh",
        }.get(language.lower(), "txt")

        # Generate a simple stub
        if language.lower() == "python":
            generated_code = f'''
#!/usr/bin/env python3
"""
{requirement}
"""

def main():
    """Main function implementing the requirement."""
    print("Implementing: {requirement}")
    # TODO: Implement the actual logic here

    return True

if __name__ == "__main__":
    main()
'''
        elif language.lower() == "javascript":
            generated_code = f"""
/**
 * {requirement}
 */

function main() {{
    console.log("Implementing: {requirement}");
    // TODO: Implement the actual logic here

    return true;
}}

main();
"""
        else:
            generated_code = f"""
// {language} implementation for: {requirement}
// TODO: Implement the actual logic here
"""

        # Save to file if output path is provided
        if output_path:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(generated_code)

                if self.output_handler:
                    self.output_handler.log_info(f"Code saved to {output_path}")
            except Exception as e:
                if self.output_handler:
                    self.output_handler.log_error(
                        f"Failed to save code to {output_path}: {e}"
                    )
                else:
                    logger.error(f"Failed to save code to {output_path}: {e}")

        return generated_code

    def analyze_code(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze code in a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if self.output_handler:
            self.output_handler.log_info(f"Analyzing code in {file_path}")

        # Read the file
        try:
            with open(file_path, "r") as f:
                code = f.read()
        except Exception as e:
            if self.output_handler:
                self.output_handler.log_error(f"Failed to read file {file_path}: {e}")
            raise

        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lstrip(".")

        # Simple analysis
        line_count = len(code.splitlines())
        char_count = len(code)
        blank_lines = sum(1 for line in code.splitlines() if not line.strip())
        comment_lines = 0

        # Calculate comment lines based on file extension
        if ext in ["py"]:
            comment_lines = sum(
                1 for line in code.splitlines() if line.strip().startswith("#")
            )
        elif ext in ["js", "ts", "java", "cs", "cpp"]:
            comment_lines = sum(
                1 for line in code.splitlines() if line.strip().startswith("//")
            )

        return {
            "file_path": file_path,
            "language": ext,
            "line_count": line_count,
            "char_count": char_count,
            "blank_lines": blank_lines,
            "comment_lines": comment_lines,
            "code_lines": line_count - blank_lines - comment_lines,
            "comments_ratio": comment_lines / line_count if line_count > 0 else 0,
            "estimated_complexity": (
                "low"
                if line_count < 100
                else ("medium" if line_count < 500 else "high")
            ),
        }

    def analyze_repository(self, repo_path: str) -> Dict[str, Any]:
        """
        Analyze a Git repository.

        Args:
            repo_path: Path to the repository

        Returns:
            Dictionary with analysis results
        """
        if not os.path.exists(repo_path):
            raise FileNotFoundError(f"Repository not found: {repo_path}")

        if self.output_handler:
            self.output_handler.log_info(f"Analyzing repository at {repo_path}")

        # Get all files (excluding .git directory)
        all_files = []
        for root, dirs, files in os.walk(repo_path):
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                all_files.append(os.path.join(root, file))

        # Group files by extension
        files_by_ext = {}
        for file_path in all_files:
            _, ext = os.path.splitext(file_path)
            ext = ext.lstrip(".").lower()
            if not ext:
                ext = "no_extension"

            if ext not in files_by_ext:
                files_by_ext[ext] = []
            files_by_ext[ext].append(file_path)

        # Basic repository statistics
        return {
            "repo_path": repo_path,
            "total_files": len(all_files),
            "file_types": {ext: len(files) for ext, files in files_by_ext.items()},
            "largest_files": self._get_largest_files(all_files, 5),
            "estimated_size_kb": sum(os.path.getsize(f) for f in all_files) / 1024,
            "directory_structure": self._analyze_directory_structure(repo_path),
        }

    def _get_largest_files(
        self, files: List[str], count: int = 5
    ) -> List[Dict[str, Any]]:
        """Get the largest files in a list."""
        file_sizes = [(f, os.path.getsize(f)) for f in files]
        file_sizes.sort(key=lambda x: x[1], reverse=True)

        return [
            {
                "path": os.path.relpath(f, start=os.path.dirname(os.path.dirname(f))),
                "size_kb": size / 1024,
            }
            for f, size in file_sizes[:count]
        ]

    def _analyze_directory_structure(self, repo_path: str) -> Dict[str, int]:
        """Analyze the directory structure of a repository."""
        directories = {}

        for root, dirs, files in os.walk(repo_path):
            if ".git" in dirs:
                dirs.remove(".git")

            rel_path = os.path.relpath(root, start=repo_path)
            if rel_path == ".":
                rel_path = "root"

            directories[rel_path] = len(files)

        return directories

    def generate_report(
        self, report_type: str, data: Dict[str, Any], output_path: Optional[str] = None
    ) -> str:
        """
        Generate a report based on data.

        Args:
            report_type: Type of report to generate
            data: Data to include in the report
            output_path: Path to save the report (optional)

        Returns:
            The generated report as a string
        """
        if self.output_handler:
            self.output_handler.log_info(f"Generating {report_type} report")

        if report_type == "repository_analysis_summary":
            report_content = self._generate_repository_analysis_report(data)
        elif report_type == "code_analysis_summary":
            report_content = self._generate_code_analysis_report(data)
        else:
            report_content = f"# {report_type.replace('_', ' ').title()}\n\nGenerated report with {len(data)} data points.\n"

        # Save to file if output path is provided
        if output_path:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(report_content)

                if self.output_handler:
                    self.output_handler.log_info(f"Report saved to {output_path}")
            except Exception as e:
                if self.output_handler:
                    self.output_handler.log_error(
                        f"Failed to save report to {output_path}: {e}"
                    )
                else:
                    logger.error(f"Failed to save report to {output_path}: {e}")

        return report_content

    def _generate_repository_analysis_report(self, data: Dict[str, Any]) -> str:
        """Generate a repository analysis report."""
        repo_path = data.get("repo_path", "Unknown")
        total_files = data.get("total_files", 0)
        file_types = data.get("file_types", {})
        largest_files = data.get("largest_files", [])
        estimated_size_kb = data.get("estimated_size_kb", 0)

        # Sort file types by count
        sorted_file_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)

        report = f"""# Repository Analysis Report

## Summary

- **Repository Path**: `{repo_path}`
- **Total Files**: {total_files}
- **Total Size**: {estimated_size_kb:.2f} KB

## File Types

| Extension | Count |
|-----------|-------|
"""

        for ext, count in sorted_file_types[:10]:  # Top 10 file types
            report += f"| {ext} | {count} |\n"

        if len(sorted_file_types) > 10:
            report += "| ... | ... |\n"

        report += """
## Largest Files

| Path | Size (KB) |
|------|-----------|
"""

        for file_info in largest_files:
            report += f"| `{file_info['path']}` | {file_info['size_kb']:.2f} |\n"

        report += """
## Recommendations

Based on the repository analysis:

1. Consider organizing files better if there are too many in the root directory
2. Large files might need to be reviewed for optimization
3. Check file type distribution to ensure it aligns with project expectations

## Next Steps

- Review code quality metrics
- Analyze dependencies
- Check for security vulnerabilities
"""

        return report

    def _generate_code_analysis_report(self, data: Dict[str, Any]) -> str:
        """Generate a code analysis report."""
        file_path = data.get("file_path", "Unknown")
        language = data.get("language", "Unknown")
        line_count = data.get("line_count", 0)
        code_lines = data.get("code_lines", 0)
        comment_lines = data.get("comment_lines", 0)
        blank_lines = data.get("blank_lines", 0)
        comments_ratio = data.get("comments_ratio", 0)
        estimated_complexity = data.get("estimated_complexity", "unknown")

        report = f"""# Code Analysis Report

## Summary

- **File**: `{file_path}`
- **Language**: {language}
- **Total Lines**: {line_count}
- **Estimated Complexity**: {estimated_complexity}

## Metrics

| Metric | Value |
|--------|-------|
| Code Lines | {code_lines} |
| Comment Lines | {comment_lines} |
| Blank Lines | {blank_lines} |
| Comments Ratio | {comments_ratio:.2%} |

## Recommendations

Based on the code analysis:

1. {self._get_comment_recommendation(comments_ratio)}
2. {self._get_complexity_recommendation(estimated_complexity)}
3. Consider adding unit tests if not already present

## Next Steps

- Review code quality in detail
- Check for potential bugs
- Optimize performance if needed
"""

        return report

    def _get_comment_recommendation(self, ratio: float) -> str:
        """Get recommendation based on comment ratio."""
        if ratio < 0.1:
            return "Add more comments to improve code readability"
        elif ratio > 0.4:
            return "Consider reducing excessive comments and focus on self-documenting code"
        else:
            return "Good balance of comments to code"

    def _get_complexity_recommendation(self, complexity: str) -> str:
        """Get recommendation based on code complexity."""
        if complexity == "high":
            return "Consider refactoring to reduce complexity"
        elif complexity == "medium":
            return "Monitor code complexity as the project evolves"
        else:
            return "Maintain current code simplicity"
