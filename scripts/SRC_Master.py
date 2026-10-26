#!/usr/bin/env python3
"""
Master script for the project.
This script integrates pandoc conversion, ASCII diagram generation, markdown linting,
and RTM generation.
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the current directory (scripts/) to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Add the project root directory (one level up from scripts/) to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Add the directory containing all modules to the Python path
modules_path = os.path.join(os.path.dirname(__file__), "modules")
if not os.path.exists(modules_path):
    print(
        f"Error: 'modules' directory not found at {modules_path}. Ensure it exists and contains the required files."
    )
    sys.exit(1)
sys.path.insert(0, modules_path)

# Import dummy placeholders for demonstration if modules not available
# In a real implementation, these would be properly implemented modules


def dummy_convert_document(input_file):
    """Dummy implementation for demonstration"""
    print(f"[DEMO] Converting document: {input_file}")
    return True


def dummy_generate_ascii_diagram():
    """Dummy implementation for demonstration"""
    return """
    +----------------+
    |  RTM Generator |
    +----------------+
          |
          v
    +----------------+
    | Output Formats |
    +----------------+
    """


def dummy_lint_markdown(file_path):
    """Dummy implementation for demonstration"""
    print(f"[DEMO] Linting markdown file: {file_path}")
    return True


# Try to import real modules, fall back to dummy implementations
print("Warning: pandoc_integration module not found. Using dummy implementation.")
convert_document = dummy_convert_document

try:
    from ascii_diagram import generate_ascii_diagram
except ImportError:
    print("Warning: ascii_diagram module not found. Using dummy implementation.")
    generate_ascii_diagram = dummy_generate_ascii_diagram

try:
    from markdown_lint import lint_markdown
except ImportError:
    print("Warning: markdown_lint module not found. Using dummy implementation.")
    lint_markdown = dummy_lint_markdown

# Import the RTM generation functionality (this is at the project root)
try:
    from generate_rtm import main as generate_rtm_main
    from generate_rtm import extract_document_outline, load_config
    from src.core.dependency_manager import validate_dependencies
    from src.core.pipeline_debugger import debug_pipeline
except ImportError as e:
    print(f"Error importing RTM generation module: {e}")
    print("This functionality is required and cannot be replaced with a dummy.")
    sys.exit(1)

# Import the outline extraction script
try:
    from scripts.extract_outline import main as extract_outline_main
except ImportError as e:
    print(f"Warning: Could not import outline extraction module: {e}")
    print("The 'outline' command will not be available.")
    extract_outline_main = None

# Import the GitHub integration functionality
try:
    from src.utils.github_integration import debug_github_integration, GitHubIntegration
except ImportError as e:
    print(f"Warning: Could not import GitHub integration module: {e}")
    print("The 'github' command will not be available.")
    debug_github_integration = None
    GitHubIntegration = None

# Import pipeline executor functionality
try:
    from src.core.pipeline_executor import run_pipeline
except ImportError as e:
    print(f"Warning: Could not import pipeline executor module: {e}")
    print("The 'pipeline' command will not be available.")
    run_pipeline = None


def main():
    if len(sys.argv) < 2:
        print("Usage: master.py <command> [arguments]")
        print(
            "Available commands: convert, diagram, lint, rtm, outline, check-deps, debug, github, pipeline"
        )
        sys.exit(1)

    command = sys.argv[1]
    args_for_command = sys.argv[2:]

    if command == "convert":
        if not args_for_command:
            print("Usage: master.py convert <input_file>")
            sys.exit(1)
        input_file = args_for_command[0]
        convert_document(input_file)
    elif command == "diagram":
        diagram = generate_ascii_diagram()
        print(diagram)
    elif command == "lint":
        if not args_for_command:
            print("Usage: master.py lint <markdown_file>")
            sys.exit(1)
        markdown_file = args_for_command[0]
        lint_markdown(markdown_file)
    elif command == "rtm":
        print(f"Executing RTM generation with args: {args_for_command}")
        original_argv = list(sys.argv)
        # Set sys.argv for generate_rtm.py's argparse
        # The first arg is script name, then the rest are parameters for generate_rtm.py
        sys.argv = ["generate_rtm.py"] + args_for_command
        try:
            rtm_exit_code = generate_rtm_main()
        finally:
            sys.argv = original_argv  # Restore original sys.argv

        if rtm_exit_code != 0:
            print(f"RTM generation failed with exit code {rtm_exit_code}")
            sys.exit(rtm_exit_code)
        else:
            print("RTM generation completed successfully.")
    elif command == "outline" and extract_outline_main is not None:
        print(f"Executing outline extraction with args: {args_for_command}")
        original_argv = list(sys.argv)
        # Set sys.argv for extract_outline.py's argparse
        sys.argv = ["extract_outline.py"] + args_for_command
        try:
            outline_exit_code = extract_outline_main()
        finally:
            sys.argv = original_argv  # Restore original sys.argv

        if outline_exit_code != 0:
            print(f"Outline extraction failed with exit code {outline_exit_code}")
            sys.exit(outline_exit_code)
        else:
            print("Outline extraction completed successfully.")
    elif command == "outline" and extract_outline_main is None:
        print("Error: outline extraction module is not available.")
        sys.exit(1)
    elif command == "check-deps":
        print("Checking dependencies...")
        # Load config
        config_data = load_config()
        # Validate dependencies
        deps_ok, errors, warnings = validate_dependencies(config_data)

        if errors:
            for error in errors:
                print(f"ERROR: {error}")

        if warnings:
            for warning in warnings:
                print(f"WARNING: {warning}")

        if deps_ok:
            print("All critical dependencies are available.")
            return 0
        else:
            print("Some dependencies are missing or misconfigured.")
            return 1
    elif command == "debug":
        print("Starting RTM pipeline debugger...")
        config_data = load_config()
        debug_exit_code = debug_pipeline(config_data, interactive=True)
        if debug_exit_code != 0:
            print(f"Debug session ended with errors (exit code: {debug_exit_code})")
            sys.exit(debug_exit_code)
        else:
            print("Debug session completed successfully.")
    elif command == "github":
        if debug_github_integration is None:
            print("Error: GitHub integration module is not available.")
            sys.exit(1)

        print("Debugging GitHub integration...")
        config_data = load_config()
        github_exit_code = debug_github_integration(config_data)
        if github_exit_code != 0:
            print(f"GitHub integration test failed with exit code {github_exit_code}")
            sys.exit(github_exit_code)
        else:
            print("GitHub integration test completed successfully.")
    elif command == "pipeline":
        if run_pipeline is None:
            print("Error: Pipeline executor module is not available.")
            sys.exit(1)

        print("Executing RTM processing pipeline...")
        config_data = load_config()

        try:
            success, summary = run_pipeline(
                config_data, verbose="--verbose" in args_for_command
            )

            if success:
                print("Pipeline execution completed successfully.")
            else:
                print("Pipeline execution failed.")
        except Exception as e:
            print(f"An error occurred during pipeline execution: {e}")
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)
