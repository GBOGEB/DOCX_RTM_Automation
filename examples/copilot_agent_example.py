import os
import sys
import json
import time

# Add the project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from dmaic import DMAICHandler
from config.openai_integration import initialize_openai
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager
from agents.copilot_agent import CopilotAgent, ConversionType
from agents.agent_common import AgentMessage, AgentPriority  # Added for potential direct message sending

def run_example():
    """Run an example of the Copilot Agent capabilities"""
    print("Starting Copilot Agent Example...")

    # --- Sanity Checks ---
    print("\n--- Sanity Checks ---")
    if not os.path.isdir(project_root):
        print(f"Error: Project root directory not found: {project_root}")
        return
    print(f"Project root: {project_root} (Exists)")

    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set. OpenAI calls will likely fail.")
    else:
        print("OPENAI_API_KEY: Set")
    # --- End Sanity Checks ---

    print("\nInitializing OpenAI client...")
    client = initialize_openai()
    if not client:
        print("Error: Failed to initialize OpenAI client. Check API key and connectivity. Exiting example.")
        return
    print("OpenAI client: Initialized successfully.")

    # Initialize supporting objects
    print("\nInitializing supporting objects (PathsManager, OutputHandler, DMAICHandler)...")
    paths = PathsManager()
    if not paths: # Basic check
        print("Error: Failed to initialize PathsManager.")
        return
    print("PathsManager: Initialized.")

    output_dir = paths.get_output_dir(create_timestamped=True)
    if not output_dir or not os.path.isdir(os.path.dirname(output_dir)): # Check if parent of timestamped dir exists
        print(f"Error: Output directory path from PathsManager is invalid or its parent does not exist: {output_dir}")
        # Attempt to create project_root/outputs as a fallback
        fallback_output_dir = os.path.join(project_root, "outputs", "copilot_example_logs")
        print(f"Attempting to use fallback output directory: {fallback_output_dir}")
        try:
            os.makedirs(fallback_output_dir, exist_ok=True)
            output_dir = fallback_output_dir
        except OSError as e:
            print(f"Error: Could not create fallback output directory {fallback_output_dir}. {e}")
            return
    output = OutputHandler(output_dir)
    print(f"OutputHandler: Initialized (logs and outputs will be in {output_dir}).")

    dmaic_project_name = "Automation Assistant"
    dmaic = DMAICHandler(dmaic_project_name, client)
    if not dmaic: # Basic check
        print(f"Error: Failed to initialize DMAICHandler for project '{dmaic_project_name}'.")
        return
    print(f"DMAICHandler for '{dmaic_project_name}': Initialized.")

    print("\n=== Copilot Agent Example ===")
    # Create the Copilot agent
    copilot = CopilotAgent(dmaic, output)
    if not copilot: # Basic check
        print("Error: Failed to initialize CopilotAgent.")
        return
    print("CopilotAgent: Initialized successfully.")

    copilot.register_with_orchestrator(None)  # Simulate registration for direct calls if orchestrator isn't used in example
    print(f"CopilotAgent ID (simulated registration): {copilot.agent_id}")

    # Set workspace to project root
    copilot.set_workspace(project_root)
    print(f"CopilotAgent workspace set to: {project_root}")

    # 1. Repository analysis
    print("\n1. Analyzing repository structure...")
    repo_analysis = copilot.analyze_repository()
    print(f"Repository analysis complete. Found {repo_analysis['file_count']} files "
          f"in {repo_analysis['directory_count']} directories.")

    # Print file type breakdown
    print("\nFile types:")
    for file_type, count in repo_analysis['file_types'].items():
        print(f"  - {file_type}: {count}")

    # Create a simple example file for conversion demo
    example_json_path = os.path.join(output_dir, "example_data.json")
    example_yaml_path = os.path.join(output_dir, "example_data.yaml")

    print(f"\nAttempting to write example JSON to: {example_json_path}")
    try:
        os.makedirs(os.path.dirname(example_json_path), exist_ok=True) # Ensure directory exists
        with open(example_json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "project": "RTM Automation",
                "version": "1.0",
                "settings": {
                    "debug": True,
                    "output_dir": "./outputs",
                    "log_level": "info"
                },
                "features": ["docx_parsing", "requirement_extraction", "traceability"]
            }, f, indent=2)
        print(f"Example JSON file created at {example_json_path}")
    except IOError as e:
        print(f"Error: Could not write example JSON file: {e}")
        return

    # 2. File conversion
    print("\n2. Converting files...")
    print(f"Converting JSON to YAML...")
    conversion_result = copilot.convert_file(example_json_path, example_yaml_path, ConversionType.JSON_TO_YAML)
    print(f"Conversion successful: {conversion_result}")

    # 3. Generate a bash script
    print("\n3. Generating a bash script...")
    script_path_target = os.path.join(output_dir, "process_files.sh")
    bash_task = "Create a script that processes all .docx files in a directory, "
    bash_task += "extracts text content, and generates statistics about word count and complexity."

    generated_script_path = copilot.generate_bash_script(bash_task, script_path_target)
    if generated_script_path and os.path.exists(generated_script_path):
        print(f"Bash script generated: {generated_script_path}")
    elif generated_script_path:
        print(f"Bash script generation reported success, but file not found at: {generated_script_path}")
    else:
        print(f"Bash script generation failed or path not returned. Target was: {script_path_target}")

    # 4. Generate Python code
    print("\n4. Generating Python code...")
    code_req = "Create a Python function that parses a DOCX file and extracts all requirements "
    code_req += "based on specific formatting (bold text starting with 'REQ-'). "
    code_req += "The function should return a list of requirement objects."

    code_path_target = os.path.join(output_dir, "requirement_parser.py")
    generated_code_details = copilot.generate_code("Python", code_req, code_path_target)
    if os.path.exists(code_path_target):
        print(f"Python code generated and saved to {code_path_target}")
    else:
        print(f"Python code generation attempted to {code_path_target}, but file not found.")

    # 5. Extract requirements from a document (using the example.py file as source)
    print("\n5. Extracting requirements...")
    example_file_for_req_extraction = os.path.join(project_root, "examples", "dmaic_example.py")
    if os.path.exists(example_file_for_req_extraction):
        req_output_path = os.path.join(output_dir, "extracted_requirements.json")
        print(f"Attempting requirements extraction from {example_file_for_req_extraction} to {output_dir}...")
        copilot.extract_requirements_from_docs(paths_to_docs=[example_file_for_req_extraction], output_dir=output_dir)
        print(f"Requirements extraction attempted. Check logs and {output_dir} for results (e.g., {req_output_path}).")
    else:
        print(f"Example file for requirement extraction not found: {example_file_for_req_extraction}")

    # 6. Generate GitHub Actions workflow
    print("\n6. Generating GitHub Actions workflow...")
    workflow_path_target = os.path.join(output_dir, "github_workflow.yml")
    copilot.github_actions_workflow("Python", "RTM Automation CI", workflow_path_target)
    if os.path.exists(workflow_path_target):
        print(f"GitHub Actions workflow generated: {workflow_path_target}")
    else:
        print(f"GitHub Actions workflow generation attempted to {workflow_path_target}, but file not found.")

    # 7. Generate a report
    print("\n7. Generating analysis report...")
    report_data = {
        "repository_analysis": repo_analysis,
        "requirements": {
            "total": 24,
            "by_priority": {"high": 7, "medium": 12, "low": 5},
            "by_status": {"complete": 18, "in_progress": 4, "not_started": 2}
        }
    }

    report_path_target = os.path.join(output_dir, "project_analysis_report.md")
    copilot.generate_report("project analysis", report_data, report_path_target)
    if os.path.exists(report_path_target):
        print(f"Analysis report generated: {report_path_target}")
    else:
        print(f"Analysis report generation attempted to {report_path_target}, but file not found.")

    # 8. Document Parsing Example (New)
    print("\n8. Parsing a document (e.g., Markdown)...")
    example_md_content = """
# Project Alpha
## Section 1: Requirements
- REQ-001: System shall do X.
- REQ-002: System shall do Y.
## Section 2: Design Notes
Some notes here.
    """
    parsed_data_path_target = os.path.join(output_dir, "parsed_markdown.json")

    parse_message = AgentMessage(
        source="copilot_example_main",
        target=copilot.agent_id,
        message_type="parse_document_command",
        content={
            "document_content": example_md_content,
            "document_type": "markdown",
            "output_path": parsed_data_path_target,
            "parsing_rules": {"extract_sections": True, "find_pattern": "REQ-\\d+"}
        }
    )
    print(f"Conceptual document parsing. Requires 'parse_document_command' handler in CopilotAgent.")
    print(f"If parsing were executed, output would be at {parsed_data_path_target}")

    # 9. Impact Assessment Example (Conceptual)
    print("\n9. Requesting Impact Assessment (Conceptual)...")
    change_description = "Refactoring the authentication module to use OAuth2."
    affected_files = ["auth.py", "user_session.py", "api_endpoints.py"]

    print(f"Conceptual impact assessment")
