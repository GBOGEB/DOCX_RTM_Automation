import os
import sys
import json
import yaml

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from config.openai_integration import initialize_openai, create_agent
from config.config_loader import get_project_paths


def main():
    """Example showing integration between OpenAI and project paths configuration"""
    print("Starting RTM Paths Integration Example...")

    # --- Configuration and Initialization Checks ---
    print("\n--- Sanity Checks ---")
    # Check project_root
    if not os.path.isdir(project_root):
        print(f"Error: Project root directory not found: {project_root}")
        return
    print(f"Project root: {project_root} (Exists)")

    # Check for OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "Warning: OPENAI_API_KEY environment variable not set. OpenAI calls will likely fail."
        )
    else:
        print("OPENAI_API_KEY: Set")

    # Initialize OpenAI
    client = initialize_openai()
    if not client:
        print(
            "Error: Failed to initialize OpenAI client. Check API key and connectivity."
        )
        return
    print("OpenAI client: Initialized successfully.")
    # --- End Sanity Checks ---

    # Get project configuration
    paths = get_project_paths()
    if not paths:
        print("Error: Failed to load project paths configuration.")
        return
    print("Project paths: Loaded successfully.")

    # Print project details
    print("\nProject Configuration:")
    if "project" in paths:
        for key, value in paths["project"].items():
            print(f"  {key}: {value}")

    # Initialize OpenAI
    client = initialize_openai()

    # Create a specialized agent for requirements analysis with project context
    system_prompt = f"""You are a requirements engineering expert for the {paths.get("project", {}).get("name", "RTM Automation")} project.

This project is described as: {paths.get("project", {}).get("description", "A requirements traceability matrix generator")}
Version: {paths.get("project", {}).get("version", "1.0.0")}

You should understand the structure of requirements in this project. Here's a sample requirement:
{json.dumps(paths.get("requirements", [{"id": "REQ-001", "text": "The system shall provide user authentication"}])[0], indent=2)}

The project uses the following LCP phases:
{yaml.dump(paths.get("lcp_phases", {}))}

Your job is to analyze requirements and suggest improvements.
"""

    rtm_agent = create_agent(system_prompt, client)
    if not rtm_agent:
        print("Error: Failed to create RTM agent.")
        return
    print("RTM Agent: Created successfully.")

    # Test the agent with a requirement
    test_requirement = (
        "REQ-002: The system should allow users to reset their passwords via email"
    )
    print("\nAnalyzing requirement:")
    print(test_requirement)

    response, _ = rtm_agent(
        f"Analyze this requirement and suggest improvements: {test_requirement}"
    )

    print("\nAI Analysis:")
    print(response)

    # Show how to use output paths from configuration
    if "output_dir" in paths:
        output_dir_path = paths["output_dir"]
        if not os.path.isabs(output_dir_path):
            output_dir_path = os.path.join(project_root, output_dir_path)

        print(f"Output directory specified: {output_dir_path}")
        try:
            os.makedirs(output_dir_path, exist_ok=True)
            print(f"Output directory ensured: {output_dir_path}")

            output_file = os.path.join(output_dir_path, "ai_analysis.txt")
            with open(output_file, "w") as f:
                f.write(f"Requirement: {test_requirement}\n\n")
                f.write(f"Analysis:\n{response}")
            print(f"\nAnalysis saved to {output_file}")
        except OSError as e:
            print(
                f"Error: Could not create or write to output directory {output_dir_path}. {e}"
            )
    else:
        print(
            "Warning: 'output_dir' not specified in project paths configuration. Cannot save analysis."
        )

    print("\nExample completed!")


if __name__ == "__main__":
    main()
