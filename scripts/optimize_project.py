import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Add the project root to path if needed
project_root_path = (
    Path(__file__).resolve().parent
)  # Assuming optimize_project.py is in the root
if str(project_root_path) not in sys.path:
    sys.path.append(str(project_root_path))

from config.openai_integration import initialize_openai
from dmaic import DMAICHandler
from utils.paths_manager import PathsManager
from utils.output_handler import OutputHandler
from agents.copilot_agent import CopilotAgent
from utils.markdown_fixer import MarkdownFixer  # Added import


class ProjectOptimizer:
    """Tool for optimizing project structure, documentation and code quality"""

    def __init__(self, output_dir: Optional[str] = None, verbose: bool = True):
        """
        Initialize the project optimizer

        Args:
            output_dir: Custom output directory (optional)
            verbose: Whether to print verbose output
        """
        self.verbose = verbose
        self.paths = PathsManager()

        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = self.paths.get_output_dir(create_timestamped=True)

        self.output_handler = OutputHandler(self.output_dir)
        self.client = initialize_openai()
        self.stats = {
            "start_time": time.time(),
            "files_processed": 0,
            "errors": 0,
            "directories_created": 0,
            "optimizations_applied": 0,
        }

        # Initialize DMAIC handler and Copilot if OpenAI client is available
        if self.client:
            self.dmaic = DMAICHandler("Project Optimization", self.client)
            self.copilot = CopilotAgent(self.dmaic, self.output_handler)
        else:
            self.dmaic = None
            self.copilot = None
            self.log(
                "Warning: OpenAI client not available. AI-assisted features will be disabled."
            )

        self.markdown_fixer = MarkdownFixer(
            project_root=str(project_root_path), output_handler=self.output_handler
        )  # Initialize fixer

    def log(self, message: str):
        """Log a message to the console and log file"""
        if self.verbose:
            print(message)
        self.output_handler.log_info(message)

    def create_project_structure(self, base_dir: str = None) -> bool:
        """
        Create recommended project structure

        Args:
            base_dir: Base directory for project structure

        Returns:
            bool: Success or failure
        """
        if base_dir is None:
            base_dir = str(project_root_path)

        # Enhanced project structure with more detailed organization
        structure = {
            "src": {
                "core": {"models": {}, "services": {}},
                "modules": {"extractors": {}, "converters": {}},
                "extractors": {"docx": {}, "markdown": {}, "code": {}},
                "utils": {"formatting": {}, "validation": {}},
            },
            "config": {"templates": {}},
            "scripts": {"setup": {}, "maintenance": {}},
            "input": {"documents": {}, "code_samples": {}},
            "output": {"reports": {}, "converted": {}, "analyzed": {}},
            "docs": {"api": {}, "guides": {}, "examples": {}},
            "tests": {"unit": {}, "integration": {}, "fixtures": {}},
        }

        dirs_created = 0
        for dir_name, subdirs in structure.items():
            dir_path = os.path.join(base_dir, dir_name)

            try:
                os.makedirs(dir_path, exist_ok=True)
                dirs_created += 1

                # Create subdirectories recursively
                self._create_subdirectories(dir_path, subdirs)

            except Exception as e:
                self.output_handler.log_error(
                    f"Error creating directory {dir_path}: {e}"
                )
                self.stats["errors"] += 1

        self.stats["directories_created"] = dirs_created
        self.log(
            f"Project structure created in '{base_dir}' ({dirs_created} directories)"
        )
        return True

    def _create_subdirectories(self, parent_dir: str, structure: Dict[str, Any]) -> int:
        """
        Recursively create subdirectories

        Args:
            parent_dir: Parent directory path
            structure: Dictionary of subdirectories and their structure

        Returns:
            int: Number of directories created
        """
        dirs_created = 0
        for subdir, children in structure.items():
            subdir_path = os.path.join(parent_dir, subdir)
            try:
                os.makedirs(subdir_path, exist_ok=True)
                dirs_created += 1

                # Create README files in each directory with descriptions
                self._create_directory_readme(subdir_path, subdir)

                # Recursively create children
                if children:
                    dirs_created += self._create_subdirectories(subdir_path, children)
            except Exception as e:
                self.output_handler.log_error(
                    f"Error creating subdirectory {subdir_path}: {e}"
                )
                self.stats["errors"] += 1

        return dirs_created

    def _create_directory_readme(self, directory: str, dir_name: str):
        """Create a README file in each directory explaining its purpose"""
        readme_path = os.path.join(directory, "README.md")

        # Only create if it doesn't exist
        if os.path.exists(readme_path):
            return

        # Default descriptions for common directory names
        descriptions = {
            "src": "Source code for the RTM automation system",
            "core": "Core functionality and critical components",
            "modules": "Modular components that extend system functionality",
            "extractors": "Modules for extracting data from various sources",
            "utils": "Utility functions and helper classes",
            "config": "Configuration files and templates",
            "scripts": "Utility scripts for maintenance and automation",
            "input": "Input files for processing",
            "output": "Generated output files",
            "docs": "Documentation files",
            "tests": "Unit and integration tests",
            "models": "Data models and schemas",
            "services": "Service implementations",
            "formatting": "Text and data formatting utilities",
            "validation": "Validation utilities",
            "unit": "Unit tests",
            "integration": "Integration tests",
            "fixtures": "Test fixtures and sample data",
            "api": "API documentation",
            "guides": "User guides and tutorials",
            "examples": "Example usage scenarios",
        }

        description = descriptions.get(dir_name, f"Directory for {dir_name} components")

        try:
            with open(readme_path, "w") as f:
                f.write(f"# {dir_name.capitalize()}\n\n")
                f.write(f"{description}\n")
        except Exception as e:
            self.output_handler.log_error(f"Error creating README in {directory}: {e}")

    def create_sample_files(self, content_type: str = "basic") -> bool:
        """
        Create sample files for testing

        Args:
            content_type: Type of content to generate (basic, detailed)
                          Future enhancement: content_type could specify 'github:owner/repo/file.md'
                          or 'openai:generate_requirements_doc' to fetch/generate dynamic content.

        Returns:
            bool: Success or failure
        """
        input_dir = project_root_path / "input"
        (input_dir / "documents").mkdir(parents=True, exist_ok=True)
        (input_dir / "code_samples").mkdir(parents=True, exist_ok=True)

        # Create document sample files
        document_files = {
            "requirements_specification.docx": self._generate_requirements_content(
                content_type
            ),
            # Example: "downloaded_spec.md": self._fetch_from_github("owner/repo/specs/main_spec.md")
            "system_architecture.docx": self._generate_architecture_content(
                content_type
            ),
            "test_plan.docx": self._generate_test_plan_content(content_type),
            # Example: "ai_generated_test_plan.txt": self._generate_with_openai("test_plan_prompt")
        }

        # Create code sample files
        code_files = {
            "sample_module.py": self._generate_python_sample(content_type),
            "sample_component.js": self._generate_js_sample(content_type),
            "sample_config.yaml": self._generate_yaml_sample(content_type),
        }

        files_created = 0
        # Create document files
        for file_name, content in document_files.items():
            file_path = input_dir / "documents" / file_name
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                files_created += 1
            except Exception as e:
                self.output_handler.log_error(f"Error creating file {file_path}: {e}")
                self.stats["errors"] += 1

        # Create code files
        for file_name, content in code_files.items():
            file_path = input_dir / "code_samples" / file_name
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                files_created += 1
            except Exception as e:
                self.output_handler.log_error(f"Error creating file {file_path}: {e}")
                self.stats["errors"] += 1

        self.stats["files_processed"] += files_created
        self.log(f"Created {files_created} sample files in the input directory")
        return True

    def _optimize_single_file(self, refactor, file_path: str) -> bool:
        """Optimize imports for a single file"""
        rel_path = os.path.relpath(file_path, str(project_root_path))
        try:
            self.output_handler.log_info(f"Optimizing imports for: {rel_path}")
            refactor.refactor_file(file_path, "modernize")
            return True
        except Exception as e:
            self.output_handler.log_error(f"Error optimizing {rel_path}: {e}")
            return False

    def optimize_docstrings(self, paths_to_process: List[str] = None) -> bool:
        """
        Optimize docstrings across Python files

        Args:
            paths_to_process: Specific paths to process (default: all Python files)

        Returns:
            bool: Success or failure
        """
        if not self.client or not self.copilot:
            self.log("OpenAI client not available. Docstring optimization skipped.")
            return False

        # Find Python files to process
        python_files = []
        if paths_to_process:
            for path in paths_to_process:
                if os.path.isfile(path) and path.endswith(".py"):
                    python_files.append(path)
                elif os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        if "venv" in root or ".git" in root or "__pycache__" in root:
                            continue
                        for file in files:
                            if file.endswith(".py"):
                                python_files.append(os.path.join(root, file))
        else:
            # Prioritize key directories to process
            priority_dirs = ["agents", "utils", "dmaic"]
            for priority_dir in priority_dirs:
                dir_path = project_root_path / priority_dir
                if dir_path.is_dir():
                    for root_str, _, files in os.walk(str(dir_path)):
                        for file in files:
                            if file.endswith(".py"):
                                python_files.append(os.path.join(root_str, file))

        # Limit files to process to avoid excessive API calls
        MAX_FILES = 10
        if len(python_files) > MAX_FILES:
            self.log(f"Limiting docstring optimization to {MAX_FILES} files")
            python_files = python_files[:MAX_FILES]

        total_files = len(python_files)
        self.log(f"Found {total_files} Python files for docstring optimization")

        processed = 0
        errors = 0

        for i, file_path in enumerate(python_files):
            rel_path = os.path.relpath(file_path, str(project_root_path))
            self.log(f"Optimizing docstrings for: {rel_path} ({i + 1}/{total_files})")

            try:
                if self._optimize_file_docstrings(file_path):
                    processed += 1
                else:
                    errors += 1
            except Exception as e:
                self.output_handler.log_error(
                    f"Error optimizing docstrings for {rel_path}: {e}"
                )
                errors += 1

        self.stats["files_processed"] += processed
        self.stats["errors"] += errors
        self.stats["optimizations_applied"] += processed

        self.log(
            f"Docstring optimization completed: {processed} files processed, {errors} errors"
        )
        return errors == 0

    def generate_documentation(self, output_formats: List[str] = ["markdown"]) -> bool:
        """
        Generate comprehensive project documentation

        Args:
            output_formats: List of output formats (markdown, html)

        Returns:
            bool: Success or failure
        """
        if not self.client or not self.copilot:
            self.log("OpenAI client not available. Documentation generation skipped.")
            return False

        # Create docs directory if it doesn't exist
        docs_dir = project_root_path / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Create directory structure for docs
        for subdir_name in ["api", "guides", "examples"]:
            (docs_dir / subdir_name).mkdir(exist_ok=True)

        # Scan project for modules and structure
        modules, structure = self._scan_project_structure()

        # Generate main documentation files
        self._generate_main_readme(modules, structure, docs_dir)
        self._generate_architecture_doc(structure, docs_dir)
        self._generate_user_guide(docs_dir)
        self._generate_api_docs(modules, docs_dir)

        # Convert markdown to HTML if requested
        if "html" in output_formats and "markdown" in output_formats:
            self._convert_docs_to_html(docs_dir)

        self.log(f"Documentation generated in {docs_dir}")
        return True

    def _scan_project_structure(self) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """Scan project structure and collect module information"""
        modules = {}
        structure = {"directories": {}, "files": {}}

        # Count files by type
        file_counts = {}

        for root_str, dirs, files in os.walk(str(project_root_path)):
            root_path = Path(root_str)
            # Skip certain directories, including common ones for submodules or build outputs
            # .git is crucial to skip if scanning a directory that might be a submodule's root
            dirs[:] = [
                d
                for d in dirs
                if d
                not in [
                    "venv",
                    ".git",
                    "__pycache__",
                    "outputs",
                    "node_modules",
                    "build",
                    "dist",
                ]
            ]

            rel_path_str = os.path.relpath(root_str, str(project_root_path))
            if rel_path_str == ".":
                rel_path_str = ""

            # Add directory to structure
            if rel_path_str:
                path_parts = rel_path_str.split(os.path.sep)
                current_level = structure["directories"]
                for part in path_parts:
                    if part not in current_level:
                        current_level[part] = {"files": {}, "directories": {}}
                    current_level = current_level[part]["directories"]

            # Process files
            for file in files:
                file_path_obj = root_path / file
                rel_file_path_str = os.path.relpath(
                    str(file_path_obj), str(project_root_path)
                )

                # Count by extension
                ext = file_path_obj.suffix.lower()
                if ext in file_counts:
                    file_counts[ext] += 1
                else:
                    file_counts[ext] = 1

                # Store Python modules for API docs
                if file.endswith(".py") and not file.startswith("__"):
                    try:
                        with open(file_path_obj, "r", encoding="utf-8") as f:
                            content = f.read()
                        modules[rel_file_path_str] = content[
                            :1000
                        ]  # Just store the beginning

                        # Add to structure
                        if rel_path_str:
                            path_parts = rel_path_str.split(os.path.sep)
                            current_level = structure["directories"]
                            for part in path_parts:
                                current_level = current_level[part]["directories"]
                            current_level["files"][file] = {"type": "python"}
                        else:
                            structure["files"][file] = {"type": "python"}
                    except Exception as e:
                        self.output_handler.log_error(
                            f"Error reading {file_path_obj}: {e}"
                        )

        structure["file_counts"] = file_counts
        return modules, structure
