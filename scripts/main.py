#!/usr/bin/env python3
"""
Main entry point for the RTM Automation System
Implements the DMAIC workflow for requirements traceability
"""

import os
import sys
import argparse
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to path if needed
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from dmaic import DMAICHandler, DMAICPhase
from config.openai_integration import initialize_openai
from utils.paths_manager import PathsManager
from utils.output_handler import OutputHandler
from utils.docx_converter import DocxConverter
from utils.document_parser import DocumentParser
from agents.agent_orchestrator import AgentOrchestrator


class WorkflowController:
    """Controller class for the DMAIC RTM Automation workflow"""

    def __init__(self):
        """Initialize the workflow controller"""
        # Setup paths
        self.paths = PathsManager()
        self.output_dir = self.paths.get_output_dir(create_timestamped=True)
        self.output = OutputHandler(self.output_dir)

        # Initialize OpenAI client
        self.client = initialize_openai()
        if not self.client:
            self.output.log_error("Failed to initialize OpenAI client")
            raise RuntimeError("OpenAI client initialization failed")

        # Initialize DMAIC handler
        self.dmaic = DMAICHandler("RTM Automation", self.client)

        # Initialize agent orchestrator
        self.orchestrator = AgentOrchestrator(self.dmaic, self.output)

        # Initialize document tools
        self.docx_converter = DocxConverter(self.output)
        self.doc_parser = DocumentParser(self.output)

        # Project state
        self.project_name = ""
        self.project_data = {}

        self.output.log_info("Workflow controller initialized")

    def initialize_project(self, project_name: str) -> Dict[str, Any]:
        """Initialize a new RTM automation project"""
        self.project_name = project_name
        self.output.log_info(f"Initializing project: {project_name}")

        # Initialize standard agents
        self.orchestrator.initialize_standard_agents()

        # Initialize project data
        self.project_data = {
            "name": project_name,
            "created_at": time.time(),
            "output_dir": self.output_dir,
            "phases": {},
            "artifacts": {},
        }

        return self.project_data

    def run_workflow(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run the DMAIC workflow for RTM automation"""
        if not self.project_name:
            self.initialize_project("RTM Automation Project")

        # DEFINE PHASE
        self.output.log_info("Starting DEFINE phase")
        self.dmaic.start_phase(DMAICPhase.DEFINE)

        # Process Define phase
        define_questions = config.get(
            "define_questions",
            [
                "What are the key objectives for automating the requirements traceability matrix?",
                "Who are the stakeholders for this RTM automation project?",
                "What are the boundaries and scope of this project?",
            ],
        )

        define_outputs = {}
        for question in define_questions:
            self.output.log_info(f"Define question: {question}")
            response = self.dmaic.interact(question)
            self.output.log_interaction(question, response)

        # If define outputs are provided, use them
        if "define_outputs" in config:
            define_outputs = config["define_outputs"]
        else:
            # Otherwise use default outputs
            define_outputs = {
                "problem_statement": "Manual RTM creation and maintenance is time-consuming and error-prone.",
                "goal": "Automate 90% of RTM creation and updates, reducing time by 70% and errors by 80%.",
                "scope": "DOCX requirements documents and their traceability to other artifacts.",
            }

        self.dmaic.complete_phase(define_outputs)
        self.project_data["phases"]["define"] = define_outputs

        # MEASURE PHASE
        self.output.log_info("Starting MEASURE phase")
        self.dmaic.start_phase(DMAICPhase.MEASURE)

        # Process document conversion if input files exist
        input_files_config = config.get("input_files", [])
        processed_input_files: List[Path] = []  # Store Path objects

        # Conceptual: Discover input files from configured sub-repositories
        # This would typically involve reading sub_repository paths from a global config
        # and scanning them for relevant files (e.g., *.docx, *.md).
        # Example:
        # sub_repo_paths = self.paths.get_sub_repository_paths() # Assuming PathsManager can provide these
        # for sub_repo_path_str in sub_repo_paths:
        #     sub_repo_path = Path(sub_repo_path_str)
        #     if sub_repo_path.is_dir():
        #         self.output.log_info(f"Scanning sub-repository: {sub_repo_path}")
        #         for item in sub_repo_path.rglob('*.docx'): # Or other patterns
        #             input_files_config.append(str(item.resolve()))
        #         for item in sub_repo_path.rglob('*.md'):
        #             input_files_config.append(str(item.resolve()))
        # # Remove duplicates that might have been added if already in config
        # input_files_config = sorted(list(set(input_files_config)))

        for file_path_str in input_files_config:
            # Conceptual: Handle GitHub URLs or other remote sources
            # if file_path_str.startswith("https://github.com/") or file_path_str.startswith("git@github.com:"):
            #     self.output.log_info(f"Attempting to fetch remote file: {file_path_str}")
            #     # Placeholder for a method to download/clone and get local path
            #     # local_file_path = self.paths.fetch_remote_file(file_path_str, self.output_dir / "remote_inputs")
            #     # if local_file_path and local_file_path.is_file():
            #     #     processed_input_files.append(local_file_path)
            #     #     self.output.log_info(f"Successfully fetched and using: {local_file_path}")
            #     # else:
            #     #     self.output.log_warning(f"Could not fetch or resolve remote file: {file_path_str}")
            #     # continue # Skip to next file_path_str
            #     pass # Fall through to local file handling for now

            input_file = Path(file_path_str)
            if not input_file.is_absolute():
                # Try resolving relative to project root if not absolute
                input_file = (Path(project_root) / file_path_str).resolve()
            else:
                input_file = input_file.resolve()

            if input_file.is_file():
                processed_input_files.append(input_file)
            else:
                self.output.log_warning(
                    f"Input file not found: {file_path_str} (resolved to {input_file}), skipping."
                )

        converted_files = []
        for input_file_path_obj in processed_input_files:  # Iterate over Path objects
            file_suffix_lower = input_file_path_obj.suffix.lower()
            if file_suffix_lower == ".docx":
                self.output.log_info(f"Converting DOCX file: {input_file_path_obj}")
                md_path_str = self.docx_converter.convert_to_markdown(
                    str(input_file_path_obj)
                )
                if md_path_str:
                    converted_files.append(md_path_str)
            elif file_suffix_lower == ".md":
                self.output.log_info(
                    f"Using existing Markdown file: {input_file_path_obj}"
                )
                # Ensure the path is stored as a string, consistent with md_path_str from conversion
                converted_files.append(str(input_file_path_obj))
            else:
                self.output.log_info(
                    f"File {input_file_path_obj} is not a DOCX or MD, skipping conversion."
                )

        # Extract requirements
        requirements = []
        for file_path_str in converted_files:  # These are already strings
            self.output.log_info(f"Extracting requirements from: {file_path_str}")
            req_path = self.doc_parser.extract_requirements(file_path_str)
            if req_path:
                try:
                    with open(req_path, "r", encoding="utf-8") as f:  # Added encoding
                        req_data = json.load(f)
                        if "requirements" in req_data:
                            requirements.extend(req_data["requirements"])
                except Exception as e:  # Catch specific exceptions if possible
                    self.output.log_error(
                        f"Failed to load requirements from {req_path}: {e}"
                    )

        # Measure outputs
        measure_outputs = {
            "input_files": [
                str(f) for f in processed_input_files
            ],  # Store original processed files as strings
            "converted_files": converted_files,
            "requirements_count": len(requirements),
            "requirements": requirements,
        }

        self.dmaic.complete_phase(measure_outputs)
        self.project_data["phases"]["measure"] = measure_outputs

        # Save project data
        self.save_project()

        # Return project data
        return self.project_data

    def validate_requirements(self) -> Dict[str, Any]:
        """Validate extracted requirements against product requirements"""
        if "measure" not in self.project_data.get("phases", {}):
            self.output.log_error("No requirements available for validation")
            return {"status": "error", "message": "No requirements available"}

        requirements = self.project_data["phases"]["measure"].get("requirements", [])
        if not requirements:
            return {"status": "error", "message": "No requirements found"}

        # Request AI validation of requirements
        validation_prompt = f"""
        Validate the following {len(requirements)} requirements against best practices:

        {json.dumps(requirements[:20], indent=2)}  # Limiting to first 20 for brevity

        For each requirement, check:
        1. Clear and unambiguous language
        2. Testability
        3. Uniqueness (no duplication)
        4. Completeness
        5. Consistent format and structure

        Provide a validation report with:
        - Overall quality score (0-100%)
        - Number of quality issues found
        - Examples of good requirements
        - Examples of requirements needing improvement
        - Improvement suggestions
        """

        validation_result = self.dmaic.interact(validation_prompt)

        # Save validation results
        validation_data = {
            "timestamp": time.time(),
            "requirements_validated": len(requirements),
            "validation_report": validation_result,
        }

        if "artifacts" not in self.project_data:
            self.project_data["artifacts"] = {}

        self.project_data["artifacts"]["validation"] = validation_data

        # Save validation report to file
        report_path = os.path.join(self.output_dir, "requirements_validation.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Requirements Validation Report\n\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Project:** {self.project_name}\n\n")
            f.write(f"**Requirements Validated:** {len(requirements)}\n\n")
            f.write("## Validation Results\n\n")
            f.write(validation_result)

        self.output.log_info(f"Requirements validation report saved to: {report_path}")

        return {
            "status": "success",
            "requirements_validated": len(requirements),
            "report_path": report_path,
        }

    def generate_rtm(self, artifacts: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a Requirements Traceability Matrix"""
        if "measure" not in self.project_data.get("phases", {}):
            self.output.log_error("No requirements available for RTM generation")
            return {"status": "error", "message": "No requirements available"}

        requirements = self.project_data["phases"]["measure"].get("requirements", [])
        if not requirements:
            return {"status": "error", "message": "No requirements found"}

        # Default artifacts if none provided
        if not artifacts:
            artifacts = [
                {
                    "name": "Design Document",
                    "items": ["Design-001", "Design-002", "Design-003"],
                },
                {
                    "name": "Test Cases",
                    "items": ["TC-001", "TC-002", "TC-003", "TC-004"],
                },
                {"name": "Code", "items": ["Module-A", "Module-B", "Module-C"]},
            ]

        # Request AI to generate RTM
        rtm_prompt = f"""
        Generate a Requirements Traceability Matrix (RTM) for the following requirements:

        {json.dumps(requirements[:20], indent=2)}  # Limiting to first 20 for brevity

        And the following artifacts:
        {json.dumps(artifacts, indent=2)}

        Create a markdown RTM showing which requirements trace to which artifacts.
        Use your knowledge to make realistic assumptions about traceability relationships.
        The RTM should be properly formatted as a markdown table.
        """

        rtm_content = self.dmaic.interact(rtm_prompt)

        # Save RTM to file
        rtm_path = os.path.join(self.output_dir, "requirements_traceability_matrix.md")
        with open(rtm_path, "w", encoding="utf-8") as f:
            f.write("# Requirements Traceability Matrix\n\n")
            f.write(f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Project:** {self.project_name}\n\n")
            f.write(rtm_content)

        # Save RTM data
        rtm_data = {
            "timestamp": time.time(),
            "requirements_count": len(requirements),
            "artifacts": artifacts,
            "rtm_path": rtm_path,
        }

        if "artifacts" not in self.project_data:
            self.project_data["artifacts"] = {}

        self.project_data["artifacts"]["rtm"] = rtm_data
        self.save_project()

        self.output.log_info(f"Requirements Traceability Matrix saved to: {rtm_path}")

        return {
            "status": "success",
            "rtm_path": rtm_path,
            "requirements_count": len(requirements),
            "artifacts_count": len(artifacts),
        }

    def save_project(self) -> str:
        """Save the project data to file"""
        project_file = os.path.join(self.output_dir, "project_data.json")
        with open(project_file, "w") as f:
            json.dump(self.project_data, f, indent=2)

        self.output.log_info(f"Project data saved to: {project_file}")
        return project_file


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="RTM Automation using DMAIC methodology"
    )
    parser.add_argument("--input", "-i", help="Path to input document(s)", nargs="+")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument(
        "--validate", "-v", action="store_true", help="Validate requirements"
    )
    parser.add_argument("--rtm", "-r", action="store_true", help="Generate RTM")

    args = parser.parse_args()

    try:
        workflow = WorkflowController()
        workflow.initialize_project("RTM Automation")

        config = {"input_files": args.input if args.input else []}

        result = workflow.run_workflow(config)
        print(f"Workflow completed. Output directory: {workflow.output_dir}")

        if args.validate:
            validation_result = workflow.validate_requirements()
            print(f"Requirements validation: {validation_result['status']}")
            if validation_result["status"] == "success":
                print(f"Validation report: {validation_result['report_path']}")

        if args.rtm:
            rtm_result = workflow.generate_rtm()
            print(f"RTM generation: {rtm_result['status']}")
            if rtm_result["status"] == "success":
                print(f"RTM: {rtm_result['rtm_path']}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
