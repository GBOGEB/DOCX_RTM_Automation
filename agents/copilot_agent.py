import os
import sys
import json
import yaml
import subprocess
import re
import shutil
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from enum import Enum, auto

from dmaic import DMAICHandler
from utils.paths_manager import PathsManager
from utils.output_handler import OutputHandler
from agents.agent_common import BaseAgent, AgentRole, AgentMessage, AgentPriority, StandardAgentResponse, AgentCapability, validate_input

class FileType(Enum):
    """Enumeration of file types the agent can process"""
    MARKDOWN = auto()
    DOCX = auto()
    JSON = auto()
    YAML = auto()
    PYTHON = auto()
    SHELL = auto()
    HTML = auto()
    XML = auto()
    CSV = auto()
    UNKNOWN = auto()

class ConversionType(Enum):
    """Supported conversion types"""
    DOCX_TO_MD = auto()
    MD_TO_DOCX = auto()
    JSON_TO_YAML = auto()
    YAML_TO_JSON = auto()
    HTML_TO_MD = auto()
    XML_TO_JSON = auto()
    CSV_TO_JSON = auto()
    PARSE_REQUIREMENTS = auto()

class CopilotAgent(BaseAgent):
    """
    Comprehensive agent that assists with repository analysis, file conversions,
    and automation tasks similar to GitHub Copilot.
    """

    def __init__(self, dmaic_handler: DMAICHandler, output_handler: OutputHandler):
        """Initialize the Copilot agent"""
        super().__init__("copilot_agent", AgentRole.CONTENT, output_handler)
        self.dmaic_handler = dmaic_handler
        self.paths = PathsManager()
        self.workspace_path: Optional[str] = None
        self.project_structure = {}
        self.file_stats = {}
        self.github_info = {}
        self.conversion_tools = {}
        self._initialize_tools()

        # Register capabilities
        self.register_capability(AgentCapability.CODE_GENERATION)
        self.register_capability(AgentCapability.REPO_ANALYSIS)
        self.register_capability(AgentCapability.FILE_CONVERSION)
        self.register_capability(AgentCapability.REQUIREMENT_EXTRACTION)
        self.register_capability(AgentCapability.REPORT_GENERATION)
        self.register_capability(AgentCapability.BASH_SCRIPT_GENERATION)
        self.register_capability(AgentCapability.BASH_SCRIPT_EXECUTION)
        self.register_capability(AgentCapability.DEPLOYMENT_CONFIG_GENERATION)
        self.register_capability(AgentCapability.GITHUB_ACTIONS_WORKFLOW_GENERATION)
        self.register_capability(AgentCapability.CODE_ANALYSIS)

        # Register message handlers
        self.register_message_handler("code_analysis_request", self.handle_code_analysis)
        self.register_message_handler("generate_code", self.handle_generate_code)
        self.register_message_handler("convert_file", self.handle_convert_file)
        self.register_message_handler("extract_requirements", self.handle_extract_requirements)
        self.register_message_handler("analyze_repository", self.handle_analyze_repository)
        self.register_message_handler("generate_report", self.handle_generate_report)
        self.register_message_handler("generate_bash_script", self.handle_generate_bash_script)
        self.register_message_handler("execute_bash_script", self.handle_execute_bash_script)
        self.register_message_handler("generate_deployment_config", self.handle_generate_deployment_config)
        self.register_message_handler("generate_github_actions_workflow", self.handle_generate_github_actions_workflow)

    def _initialize_tools(self):
        """Initialize external conversion tools and dependencies"""
        # Check for pandoc (for docx/md conversion)
        try:
            subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
            self.conversion_tools['pandoc'] = True
        except (subprocess.SubprocessError, FileNotFoundError):
            self.conversion_tools['pandoc'] = False
            self.output_handler.log_info("Pandoc not found. DOCX conversions will be limited.")

        # Check for other tools
        # Add checks for other external dependencies as needed

    def set_workspace(self, workspace_path: str) -> bool:
        """Set and validate the workspace directory"""
        if not os.path.isdir(workspace_path):
            self.output_handler.log_error(f"Invalid workspace path: {workspace_path}")
            return False

        self.workspace_path = workspace_path
        self.output_handler.log_info(f"Workspace set to: {workspace_path}")
        return True

    def analyze_repository(self, repo_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze a repository for structure, file types, and other metrics"""
        target_path = repo_path or self.workspace_path

        if not target_path:
            raise ValueError("Repository path not provided and workspace not set")

        if not os.path.isdir(target_path):
            raise ValueError(f"Invalid repository path: {target_path}")

        self.output_handler.log_info(f"Analyzing repository: {target_path}")

        # Collect repository structure
        structure = self._scan_directory(target_path)

        # Analyze file types and statistics
        stats = self._analyze_file_stats(structure)

        # Check for git repository
        git_info = self._get_git_info(target_path)

        # Store results
        self.project_structure = structure
        self.file_stats = stats
        self.github_info = git_info

        summary = {
            "repository_path": target_path,
            "file_count": stats["total_files"],
            "directory_count": stats["total_directories"],
            "file_types": stats["file_types"],
            "language_breakdown": stats["language_breakdown"],
            "git_info": git_info,
        }

        return summary

    def convert_file(self,
                   input_path: str,
                   output_path: str,
                   conversion_type: ConversionType) -> bool:
        """Convert a file from one format to another"""
        if not os.path.isfile(input_path):
            self.output_handler.log_error(f"Input file not found: {input_path}")
            return False

        self.output_handler.log_info(f"Converting {input_path} → {output_path} ({conversion_type.name})")

        # Handle different conversion types
        if conversion_type == ConversionType.DOCX_TO_MD:
            return self._convert_docx_to_markdown(input_path, output_path)
        elif conversion_type == ConversionType.MD_TO_DOCX:
            return self._convert_markdown_to_docx(input_path, output_path)
        elif conversion_type == ConversionType.JSON_TO_YAML:
            return self._convert_json_to_yaml(input_path, output_path)
        elif conversion_type == ConversionType.YAML_TO_JSON:
            return self._convert_yaml_to_json(input_path, output_path)
        elif conversion_type == ConversionType.PARSE_REQUIREMENTS:
            return self._parse_requirements_doc(input_path, output_path)
        else:
            self.output_handler.log_error(f"Conversion type not implemented: {conversion_type.name}")
            return False

    def generate_bash_script(self, task_description: str, output_path: str) -> str:
        """Generate a bash script for an automation task"""
        prompt = f"""
        Generate a bash script for the following automation task:
        {task_description}

        The script should be well-commented, handle errors appropriately, and follow best practices.
        """

        script_content = self.dmaic_handler.interact(prompt)

        # Extract just the script part (between ``` marks if present)
        script_match = re.search(r'```(?:bash|sh)?\n(.*?)```', script_content, re.DOTALL)
        if script_match:
            script_content = script_match.group(1)

        # Save the script
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script_content)

            # Make the script executable
            os.chmod(output_path, 0o755)  # rwxr-xr-x
            self.output_handler.log_info(f"Bash script generated and saved to {output_path}")
            return output_path
        except Exception as e:
            self.output_handler.log_error(f"Failed to save bash script: {e}")
            return ""

    def execute_bash_script(self, script_path: str, args: List[str] = None) -> Dict[str, Any]:
        """Execute a bash script and return the results"""
        if not os.path.isfile(script_path):
            return {"success": False, "error": f"Script not found: {script_path}"}

        cmd = [script_path]
        if args:
            cmd.extend(args)

        try:
            self.output_handler.log_info(f"Executing script: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            self.output_handler.log_error(f"Script execution error: {e}")
            return {"success": False, "error": str(e)}

    def generate_code(self,
                     language: str,
                     requirement: str,
                     output_path: Optional[str] = None) -> str:
        """Generate code based on requirements"""
        prompt = f"""
        Generate {language} code for the following requirement:
        {requirement}

        The code should be well-documented, handle edge cases, and follow best practices.
        Include example usage if applicable.
        """

        code_content = self.dmaic_handler.interact(prompt)

        # Extract just the code part (between ``` marks if present)
        code_match = re.search(r'```(?:\w+)?\n(.*?)```', code_content, re.DOTALL)
        if code_match:
            code_content = code_match.group(1)

        # Save the code if output path is provided
        if output_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(code_content)
                self.output_handler.log_info(f"Generated code saved to {output_path}")
            except Exception as e:
                self.output_handler.log_error(f"Failed to save generated code: {e}")

        return code_content

    def extract_requirements_from_docs(self, doc_path: str, output_format: str = "json") -> str:
        """Extract requirements from documentation files"""
        if not os.path.isfile(doc_path):
            self.output_handler.log_error(f"Document not found: {doc_path}")
            return ""

        # Determine file type
        file_extension = os.path.splitext(doc_path)[1].lower()

        # Extract text content based on file type
        text_content = ""
        if file_extension == ".docx":
            # Convert to markdown first to get text
            temp_md_path = os.path.join(self.paths.get_output_dir(), "temp_extract.md")
            if self._convert_docx_to_markdown(doc_path, temp_md_path):
                with open(temp_md_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                os.remove(temp_md_path)
        elif file_extension in [".md", ".txt"]:
            with open(doc_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        else:
            self.output_handler.log_error(f"Unsupported file type for requirements extraction: {file_extension}")
            return ""

        # Use AI to extract requirements
        prompt = f"""
        Extract all requirements from this document text.
        Format each requirement with an ID, category, description, and priority.

        Document text:
        {text_content[:4000]}... (truncated for brevity)
        """

        requirements_text = self.dmaic_handler.interact(prompt)

        # Convert to requested output format
        output_path = os.path.join(
            self.paths.get_output_dir(),
            f"requirements_{os.path.basename(doc_path).split('.')[0]}.{output_format}"
        )

        try:
            # Parse the AI's response to extract requirements
            requirements_list = self._parse_requirements_from_text(requirements_text)

            # Save in requested format
            if output_format.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({"requirements": requirements_list}, f, indent=2)
            elif output_format.lower() == "yaml":
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump({"requirements": requirements_list}, f)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(requirements_text)

            self.output_handler.log_info(f"Extracted requirements saved to {output_path}")
            return output_path
        except Exception as e:
            self.output_handler.log_error(f"Failed to save extracted requirements: {e}")
            return ""

    def generate_deployment_config(self,
                                 project_type: str,
                                 output_path: Optional[str] = None) -> str:
        """Generate deployment configuration for different environments"""
        project_structure = self.project_structure if self.project_structure else "Unknown project structure"

        prompt = f"""
        Generate deployment configuration files for a {project_type} project.
        Include configurations for development, testing, and production environments.

        Project structure:
        {json.dumps(project_structure, indent=2)[:2000] if isinstance(project_structure, dict) else project_structure}
        """

        config_content = self.dmaic_handler.interact(prompt)

        # If output path is provided, save the configuration
        if output_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(config_content)
                self.output_handler.log_info(f"Deployment configuration saved to {output_path}")
            except Exception as e:
                self.output_handler.log_error(f"Failed to save deployment configuration: {e}")

        return config_content

    def github_actions_workflow(self,
                              project_type: str,
                              workflow_name: str,
                              output_path: Optional[str] = None) -> str:
        """Generate GitHub Actions workflow configuration"""
        prompt = f"""
        Generate a GitHub Actions workflow file for a {project_type} project.
        The workflow should handle CI/CD for the '{workflow_name}' process.
        Include steps for testing, building, and deployment with proper error handling.
        """

        workflow_content = self.dmaic_handler.interact(prompt)

        # Extract YAML content
        yaml_match = re.search(r'```(?:yaml|yml)?\n(.*?)```', workflow_content, re.DOTALL)
        if yaml_match:
            workflow_content = yaml_match.group(1)

        # If output path is provided, save the workflow
        if output_path:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(workflow_content)
                self.output_handler.log_info(f"GitHub Actions workflow saved to {output_path}")
            except Exception as e:
                self.output_handler.log_error(f"Failed to save GitHub Actions workflow: {e}")

        return workflow_content

    def generate_report(self,
                      report_type: str,
                      data: Dict[str, Any],
                      output_path: Optional[str] = None) -> str:
        """Generate report based on analysis data"""
        prompt = f"""
        Generate a {report_type} report based on the following data:
        {json.dumps(data, indent=2)[:3000]}

        The report should include:
        1. Executive summary
        2. Key findings
        3. Detailed analysis
        4. Recommendations
        5. Next steps

        Format the report in Markdown with proper sections, tables, and bullet points.
        """

        report_content = self.dmaic_handler.interact(prompt)

        # If output path is provided, save the report
        if output_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                self.output_handler.log_info(f"Report saved to {output_path}")
            except Exception as e:
                self.output_handler.log_error(f"Failed to save report: {e}")

        return report_content

    # Private helper methods
    def _scan_directory(self, directory_path: str, max_depth: int = 5, current_depth: int = 0) -> Dict[str, Any]:
        """Recursively scan a directory and build its structure"""
        if current_depth > max_depth:
            return {"type": "directory", "name": os.path.basename(directory_path), "note": "max depth reached"}

        structure = {
            "type": "directory",
            "name": os.path.basename(directory_path),
            "path": directory_path,
            "contents": []
        }

        try:
            items = os.listdir(directory_path)
            for item in items:
                item_path = os.path.join(directory_path, item)

                # Skip hidden files and directories
                if item.startswith('.'):
                    continue

                if os.path.isdir(item_path):
                    # Recursively scan subdirectory
                    subdir_structure = self._scan_directory(item_path, max_depth, current_depth + 1)
                    structure["contents"].append(subdir_structure)
                else:
                    # Add file to structure
                    file_type = self._determine_file_type(item_path)
                    file_info = {
                        "type": "file",
                        "name": item,
                        "path": item_path,
                        "size": os.path.getsize(item_path),
                        "file_type": file_type.name
                    }
                    structure["contents"].append(file_info)

            return structure
        except Exception as e:
            self.output_handler.log_error(f"Error scanning directory {directory_path}: {e}")
            return {
                "type": "directory",
                "name": os.path.basename(directory_path),
                "path": directory_path,
                "error": str(e)
            }

    def _determine_file_type(self, file_path: str) -> FileType:
        """Determine the file type based on extension and content"""
        _, ext = os.path.splitext(file_path.lower())

        if ext in ['.md', '.markdown']:
            return FileType.MARKDOWN
        elif ext == '.docx':
            return FileType.DOCX
        elif ext == '.json':
            return FileType.JSON
        elif ext in ['.yml', '.yaml']:
            return FileType.YAML
        elif ext == '.py':
            return FileType.PYTHON
        elif ext in ['.sh', '.bash']:
            return FileType.SHELL
        elif ext == '.html':
            return FileType.HTML
        elif ext == '.xml':
            return FileType.XML
        elif ext == '.csv':
            return FileType.CSV

        return FileType.UNKNOWN

    def _analyze_file_stats(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze file statistics from the directory structure"""
        stats = {
            "total_files": 0,
            "total_directories": 1,  # Start with 1 for the current directory
            "file_types": {},
            "language_breakdown": {},
            "largest_files": []
        }

        def process_item(item):
            if item["type"] == "directory":
                stats["total_directories"] += 1
                for subitem in item.get("contents", []):
                    process_item(subitem)
            else:  # file
                stats["total_files"] += 1
                file_type = item.get("file_type", "UNKNOWN")

                # Count file types
                if file_type not in stats["file_types"]:
                    stats["file_types"][file_type] = 0
                stats["file_types"][file_type] += 1

                # Track language breakdown for code files
                if file_type in ["PYTHON", "SHELL", "HTML", "XML"]:
                    if file_type not in stats["language_breakdown"]:
                        stats["language_breakdown"][file_type] = 0
                    stats["language_breakdown"][file_type] += 1

                # Track largest files
                stats["largest_files"].append({
                    "name": item["name"],
                    "path": item["path"],
                    "size": item["size"]
                })
                stats["largest_files"].sort(key=lambda x: x["size"], reverse=True)
                stats["largest_files"] = stats["largest_files"][:10]  # Keep top 10

        for item in structure.get("contents", []):
            process_item(item)

        return stats

    def _get_git_info(self, repo_path: str) -> Dict[str, Any]:
        """Get Git repository information"""
        git_info = {
            "is_git_repo": False,
            "current_branch": "",
            "remotes": [],
            "last_commits": []
        }

        # Check if it's a git repository
        git_dir = os.path.join(repo_path, ".git")
        if not os.path.isdir(git_dir):
            return git_info

        git_info["is_git_repo"] = True

        try:
            # Get current branch
            result = subprocess.run(
                ["git", "-C", repo_path, "branch", "--show-current"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                git_info["current_branch"] = result.stdout.strip()

            # Get remotes
            result = subprocess.run(
                ["git", "-C", repo_path, "remote", "-v"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                remotes = result.stdout.strip().split("\n")
                for remote in remotes:
                    if remote:
                        parts = remote.split()
                        if len(parts) >= 2 and parts[0] not in [r["name"] for r in git_info["remotes"]]:
                            git_info["remotes"].append({
                                "name": parts[0],
                                "url": parts[1]
                            })

            # Get last 5 commits
            result = subprocess.run(
                ["git", "-C", repo_path, "log", "-5", "--pretty=format:%H|%an|%ad|%s"],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                for commit in commits:
                    if not commit:
                        continue
                    parts = commit.split("|")
                    if len(parts) >= 4:
                        git_info["last_commits"].append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
        except Exception as e:
            self.output_handler.log_error(f"Error getting git information: {e}")

        return git_info

    def _convert_docx_to_markdown(self, input_path: str, output_path: str) -> bool:
        """Convert a DOCX file to Markdown"""
        if not self.conversion_tools.get('pandoc', False):
            # Fallback if pandoc isn't available
            self.output_handler.log_error(
                "Pandoc not available. Install pandoc for DOCX to Markdown conversion."
            )
            return False

        try:
            subprocess.run([
                'pandoc',
                input_path,
                '-f', 'docx',
                '-t', 'markdown',
                '-o', output_path
            ], check=True, capture_output=True)

            self.output_handler.log_info(f"Converted {input_path} to Markdown")
            return True
        except subprocess.SubprocessError as e:
            self.output_handler.log_error(f"Pandoc conversion error: {e}")
            return False

    def _convert_markdown_to_docx(self, input_path: str, output_path: str) -> bool:
        """Convert a Markdown file to DOCX"""
        if not self.conversion_tools.get('pandoc', False):
            self.output_handler.log_error(
                "Pandoc not available. Install pandoc for Markdown to DOCX conversion."
            )
            return False

        try:
            subprocess.run([
                'pandoc',
                input_path,
                '-f', 'markdown',
                '-t', 'docx',
                '-o', output_path
            ], check=True, capture_output=True)

            self.output_handler.log_info(f"Converted {input_path} to DOCX")
            return True
        except subprocess.SubprocessError as e:
            self.output_handler.log_error(f"Pandoc conversion error: {e}")
            return False

    def _convert_json_to_yaml(self, input_path: str, output_path: str) -> bool:
        """Convert a JSON file to YAML"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            self.output_handler.log_info(f"Converted {input_path} to YAML")
            return True
        except Exception as e:
            self.output_handler.log_error(f"JSON to YAML conversion error: {e}")
            return False

    def _convert_yaml_to_json(self, input_path: str, output_path: str) -> bool:
        """Convert a YAML file to JSON"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            self.output_handler.log_info(f"Converted {input_path} to JSON")
            return True
        except Exception as e:
            self.output_handler.log_error(f"YAML to JSON conversion error: {e}")
            return False

    def _parse_requirements_doc(self, input_path: str, output_path: str) -> bool:
        """Parse a requirements document into structured format"""
        try:
            # First extract content based on file type
            file_ext = os.path.splitext(input_path)[1].lower()
            text_content = ""

            if file_ext == '.docx':
                temp_md_path = os.path.join(self.paths.get_output_dir(), "temp_req.md")
                if self._convert_docx_to_markdown(input_path, temp_md_path):
                    with open(temp_md_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    os.remove(temp_md_path)
            elif file_ext in ['.md', '.txt']:
                with open(input_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
            else:
                self.output_handler.log_error(f"Unsupported file format for requirements parsing: {file_ext}")
                return False

            # Use AI to parse requirements
            prompt = f"""
            Parse the following document and extract all requirements in a structured format.
            For each requirement, identify:
            1. A requirement ID (REQ-XXX format)
            2. The requirement description
            3. The requirement type/category
            4. Priority (if available)
            5. Dependencies (if available)

            Document content:
            {text_content[:4000]}... (truncated for brevity)

            Return the requirements in a structured JSON format like:
            {{
                "requirements": [
                    {{
                        "id": "REQ-001",
                        "description": "The system shall...",
                        "type": "Functional",
                        "priority": "High",
                        "dependencies": ["REQ-002"]
                    }}
                ]
            }}
            """

            parsed_requirements = self.dmaic_handler.interact(prompt)

            # Extract the JSON part
            json_match = re.search(r'```(?:json)?\n(.*?)```', parsed_requirements, re.DOTALL)
            if json_match:
                parsed_requirements = json_match.group(1)

            # Try to parse the JSON directly
            try:
                req_data = json.loads(parsed_requirements)
            except json.JSONDecodeError:
                # If direct parsing fails, use a more forgiving approach
                req_data = self._parse_requirements_from_text(parsed_requirements)

            # Save to output file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(req_data, f, indent=2)

            self.output_handler.log_info(f"Requirements parsed and saved to {output_path}")
            return True
        except Exception as e:
            self.output_handler.log_error(f"Failed to parse requirements: {e}")
            return False

    def _parse_requirements_from_text(self, requirements_text: str) -> List[Dict[str, Any]]:
        """Parse requirements from AI-generated text into structured format"""
        requirements_list = []

        # Pattern for a requirement item
        req_pattern = re.compile(
            r'(?:[\-\*]\s*)?'  # Optional bullet point
            r'(?:(?P<id>[A-Z0-9\-]+)[:\.]\s*)?'  # Optional ID
            r'(?P<description>.*?)'  # Description (non-greedy)
            r'(?:\s*\((?P<priority>High|Medium|Low)\))?'  # Optional priority in parentheses
            r'(?:\s*\[(?P<category>[A-Za-z\s]+)\])?'  # Optional category in brackets
            r'$',  # End of line
            re.MULTILINE
        )

        # Find all requirements in the text
        lines = requirements_text.split('\n')
        current_req = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = req_pattern.match(line)
            if match:
                # If we were processing a requirement, add it to the list
                if current_req:
                    requirements_list.append(current_req)

                # Start a new requirement
                current_req = {
                    "id": match.group("id") or f"REQ-{len(requirements_list) + 1:03d}",
                    "description": match.group("description").strip() if match.group("description") else "",
                    "priority": match.group("priority") or "Medium",
                    "category": match.group("category") or "Functional"
                }
            elif line.lower().startswith(("id:", "req-id:", "requirement id:")):
                # This is an ID line
                parts = line.split(":", 1)
                if len(parts) == 2 and current_req:
                    current_req["id"] = parts[1].strip()
            elif line.lower().startswith(("description:", "desc:")):
                # This is a description line
                parts = line.split(":", 1)
                if len(parts) == 2 and current_req:
                    current_req["description"] = parts[1].strip()
            elif line.lower().startswith(("priority:", "prio:")):
                # This is a priority line
                parts = line.split(":", 1)
                if len(parts) == 2 and current_req:
                    current_req["priority"] = parts[1].strip()
            elif line.lower().startswith(("category:", "type:")):
                # This is a category/type line
                parts = line.split(":", 1)
                if len(parts) == 2 and current_req:
                    current_req["category"] = parts[1].strip()
            elif current_req and "description" in current_req:
                # This is a continuation of the description
                current_req["description"] += " " + line

        # Add the last requirement if there is one
        if current_req:
            requirements_list.append(current_req)

        return requirements_list

    def handle_code_analysis(self, message: AgentMessage) -> StandardAgentResponse:
        """Handle request to analyze code"""
        content = message.content
        if not validate_input(content, ["file_path"]):
            return {"status": "error", "message": "No file path provided for analysis.", "data": None, "error_details": "Missing 'file_path'", "markdown_content": None}

        file_path = content["file_path"]
        self.output_handler.log_info(f"Analyzing code in {file_path}")

        try:
            if not os.path.exists(file_path):
                return {"status": "error", "message": f"File not found: {file_path}", "data": {"file_path": file_path}, "error_details": "File system error", "markdown_content": None}

            with open(file_path, 'r', encoding='utf-8') as f:
                code_snippet = f.read(5000)  # Increased from 1000 to 5000

            prompt = f"Analyze the following code snippet from '{os.path.basename(file_path)}' for potential issues, improvements, and complexity:\n\n```\n{code_snippet}\n```"
            analysis_text = self.dmaic_handler.interact(prompt)

            analysis_result = {
                "file": file_path,
                "summary": analysis_text,
            }
            markdown_report = f"### Code Analysis for: `{file_path}`\n\n**Summary:**\n{analysis_text}"

            return {
                "status": "success",
                "message": "Code analysis completed.",
                "data": analysis_result,
                "error_details": None,
                "markdown_content": markdown_report
            }
        except Exception as e:
            self.output_handler.log_error(f"Error during code analysis of {file_path}: {e}")
            return {"status": "error", "message": "Code analysis failed.", "data": {"file_path": file_path}, "error_details": str(e), "markdown_content": None}

    def handle_generate_code(self, message: AgentMessage) -> StandardAgentResponse:
        """Handle request to generate code"""
        content = message.content
        if not validate_input(content, ["requirement"]):
            return {"status": "error", "message": "No requirement provided for code generation.", "data": None, "error_details": "Missing 'requirement'", "markdown_content": None}

        language = content.get("language", "python")
        requirement = content["requirement"]
        output_path = content.get("output_path")

        try:
            code = self.generate_code(language, requirement, output_path)
            markdown_code = f"### Generated {language} code for: {requirement}\n\n``` {language.lower()}\n{code}\n```"
            if output_path:
                markdown_code += f"\n\nSaved to: `{output_path}`"

            return {
                "status": "success",
                "message": "Code generated successfully.",
                "data": {
                    "language": language,
                    "requirement": requirement,
                    "code": code,
                    "output_path": output_path
                },
                "error_details": None,
                "markdown_content": markdown_code
            }
        except Exception as e:
            self.output_handler.log_error(f"Error during code generation: {e}")
            return {"status": "error", "message": "Code generation failed.", "data": {"language": language, "requirement": requirement}, "error_details": str(e), "markdown_content": None}

    def handle_convert_file(self, message: AgentMessage) -> StandardAgentResponse:
        """Handle request to convert a file"""
        content = message.content
        if not validate_input(content, ["input_path", "output_path", "conversion_type"]):
            return {"status": "error", "message": "Missing parameters for file conversion.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        input_path = content["input_path"]
        output_path = content["output_path"]
        conversion_type_str = content["conversion_type"]

        try:
            conversion_type = ConversionType[conversion_type_str.upper()]
            result = self.convert_file(input_path, output_path, conversion_type)

            if result:
                return {
                    "status": "success",
                    "message": f"File converted from {conversion_type_str} and saved to {output_path}.",
                    "data": {"input_path": input_path, "output_path": output_path, "conversion_type": conversion_type_str},
                    "error_details": None,
                    "markdown_content": f"File `{input_path}` converted via `{conversion_type_str}` to `{output_path}`."
                }
            else:
                return {
                    "status": "error",
                    "message": "File conversion failed.",
                    "data": {"input_path": input_path, "output_path": output_path, "conversion_type": conversion_type_str},
                    "error_details": "Conversion process returned false.",
                    "markdown_content": None
                }
        except KeyError:
            return {"status": "error", "message": f"Invalid conversion type: {conversion_type_str}.", "data": None, "error_details": "Unknown conversion type", "markdown_content": None}
        except Exception as e:
            self.output_handler.log_error(f"Error during file conversion: {e}")
            return {"status": "error", "message": "File conversion process encountered an exception.", "data": {"input_path": input_path}, "error_details": str(e), "markdown_content": None}

    def handle_extract_requirements(self, message: AgentMessage) -> StandardAgentResponse:
        """Handle request to extract requirements from a document"""
        content = message.content
        if not validate_input(content, ["document_path"]):
            return {"status": "error", "message": "No document path provided.", "data": None, "error_details": "Missing 'document_path'", "markdown_content": None}

        doc_path = content["document_path"]
        output_format = content.get("output_format", "json")

        try:
            output_file_path = self.extract_requirements_from_docs(doc_path, output_format)

            if not output_file_path:
                return {"status": "error", "message": "Failed to extract requirements.", "data": {"document_path": doc_path}, "error_details": "Extraction process failed to produce an output file.", "markdown_content": None}

            extracted_content_preview = ""
            if os.path.exists(output_file_path):
                with open(output_file_path, 'r', encoding='utf-8') as f:
                    extracted_content_preview = f.read(500) + "..."

            return {
                "status": "success",
                "message": f"Requirements extracted to {output_file_path}.",
                "data": {"document_path": doc_path, "output_path": output_file_path, "format": output_format},
                "error_details": None,
                "markdown_content": f"### Requirements Extracted\n\n- **Source:** `{doc_path}`\n- **Output:** `{output_file_path}`\n- **Format:** `{output_format}`\n\n**Preview:**\n```\n{extracted_content_preview}\n```"
            }
        except Exception as e:
            self.output_handler.log_error(f"Error extracting requirements: {e}")
            return {"status": "error", "message": "Requirement extraction failed.", "data": {"document_path": doc_path}, "error_details": str(e), "markdown_content": None}

    def handle_analyze_repository(self, message: AgentMessage) -> StandardAgentResponse:
        """Handle request to analyze a repository"""
        content = message.content
        if not validate_input(content, ["repository_path"]):
            return {"status": "error", "message": "No repository path provided.", "data": None, "error_details": "Missing 'repository_path'", "markdown_content": None}

        repo_path = content["repository_path"]

        try:
            analysis_summary = self.analyze_repository(repo_path)

            md_report = f"### Repository Analysis: `{repo_path}`\n\n"
            md_report += f"- **File Count:** {analysis_summary.get('file_count', 'N/A')}\n"
            md_report += f"- **Directory Count:** {analysis_summary.get('directory_count', 'N/A')}\n"
            md_report += f"- **File Types:** {json.dumps(analysis_summary.get('file_types', {}))}\n"
            if analysis_summary.get('git_info', {}).get('is_git_repo'):
                md_report += f"- **Git Branch:** {analysis_summary['git_info'].get('current_branch', 'N/A')}\n"

            return {
                "status": "success",
                "message": "Repository analysis complete.",
                "data": {"repository_path": repo_path, "analysis_summary": analysis_summary},
                "error_details": None,
                "markdown_content": md_report
            }
        except Exception as e:
            self.output_handler.log_error(f"Error analyzing repository: {e}")
            return {"status": "error", "message": "Repository analysis failed.", "data": {"repository_path": repo_path}, "error_details": str(e), "markdown_content": None}

    def handle_generate_report(self, message: AgentMessage) -> StandardAgentResponse:
        """Handle request to generate a report"""
        content = message.content
        if not validate_input(content, ["report_type", "data"]):
            return {"status": "error", "message": "Missing parameters for report generation.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        report_type = content["report_type"]
        data_for_report = content["data"]
        output_path = content.get("output_path")

        try:
            report_content_md = self.generate_report(report_type, data_for_report, output_path)

            return {
                "status": "success",
                "message": f"{report_type} report generated.",
                "data": {"report_type": report_type, "output_path": output_path, "source_data_preview": str(data_for_report)[:200]+"..." },
                "error_details": None,
                "markdown_content": report_content_md
            }
        except Exception as e:
            self.output_handler.log_error(f"Error generating report: {e}")
            return {"status": "error", "message": "Report generation failed.", "data": {"report_type": report_type}, "error_details": str(e), "markdown_content": None}

    def process_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """Process incoming messages without specific handlers"""
        self.output_handler.log_info(
            f"Copilot agent received message from {message.source}: {message.message_type}"
        )

        return {
            "status": "received",
            "message": f"Received {message.message_type}, but no specific handler is available",
            "agent": "copilot_agent"
        }

    # New Message Handlers
    def handle_generate_bash_script(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["task_description", "output_path"]):
            return {"status": "error", "message": "Missing task_description or output_path.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        task_description = content["task_description"]
        output_path = content["output_path"]
        try:
            script_file_path = self.generate_bash_script(task_description, output_path)
            if script_file_path:
                with open(script_file_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                md_content = f"### Bash Script Generated\n\n**Task:** {task_description}\n**Saved to:** `{script_file_path}`\n\n```bash\n{script_content}\n```"
                return {"status": "success", "message": "Bash script generated.", "data": {"output_path": script_file_path, "task_description": task_description}, "error_details": None, "markdown_content": md_content}
            else:
                return {"status": "error", "message": "Failed to generate bash script.", "data": None, "error_details": "Script generation returned empty path", "markdown_content": None}
        except Exception as e:
            return {"status": "error", "message": "Failed to generate bash script.", "data": None, "error_details": str(e), "markdown_content": None}

    def handle_execute_bash_script(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["script_path"]):
            return {"status": "error", "message": "Missing script_path.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        script_path = content["script_path"]
        args = content.get("args", [])
        try:
            execution_result = self.execute_bash_script(script_path, args)
            md_content = f"### Bash Script Execution Result\n\n**Script:** `{script_path}`\n**Success:** {execution_result.get('success')}\n**Return Code:** {execution_result.get('return_code')}\n\n**Stdout:**\n```\n{execution_result.get('stdout', '')}\n```\n\n**Stderr:**\n```\n{execution_result.get('stderr', '')}\n```"
            return {"status": "success" if execution_result.get("success") else "error", "message": "Bash script execution completed.", "data": execution_result, "error_details": execution_result.get("error"), "markdown_content": md_content}
        except Exception as e:
            return {"status": "error", "message": "Failed to execute bash script.", "data": None, "error_details": str(e), "markdown_content": None}

    def handle_generate_deployment_config(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["project_type"]):
            return {"status": "error", "message": "Missing project_type.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        project_type = content["project_type"]
        output_path = content.get("output_path")
        try:
            config_content = self.generate_deployment_config(project_type, output_path)
            md_content = f"### Deployment Configuration Generated\n\n**Project Type:** {project_type}\n"
            if output_path:
                md_content += f"**Saved to:** `{output_path}`\n"
            md_content += f"\n```yaml\n{config_content[:1000]}...\n```"  # Preview
            return {"status": "success", "message": "Deployment configuration generated.", "data": {"project_type": project_type, "output_path": output_path, "config_content_preview": config_content[:200]+"..." }, "error_details": None, "markdown_content": md_content}
        except Exception as e:
            return {"status": "error", "message": "Failed to generate deployment configuration.", "data": None, "error_details": str(e), "markdown_content": None}

    def handle_generate_github_actions_workflow(self, message: AgentMessage) -> StandardAgentResponse:
        content = message.content
        if not validate_input(content, ["project_type", "workflow_name"]):
            return {"status": "error", "message": "Missing project_type or workflow_name.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        project_type = content["project_type"]
        workflow_name = content["workflow_name"]
        output_path = content.get("output_path")
        try:
            workflow_content = self.github_actions_workflow(project_type, workflow_name, output_path)
            md_content = f"### GitHub Actions Workflow Generated\n\n**Project Type:** {project_type}\n**Workflow Name:** {workflow_name}\n"
            if output_path:
                md_content += f"**Saved to:** `{output_path}`\n"
            md_content += f"\n```yaml\n{workflow_content[:1000]}...\n```"  # Preview
            return {"status": "success", "message": "GitHub Actions workflow generated.", "data": {"project_type": project_type, "workflow_name": workflow_name, "output_path": output_path, "workflow_content_preview": workflow_content[:200]+"..." }, "error_details": None, "markdown_content": md_content}
        except Exception as e:
            return {"status": "error", "message": "Failed to generate GitHub Actions workflow.", "data": None, "error_details": str(e), "markdown_content": None}
