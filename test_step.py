#!/usr/bin/env python3
"""
Test individual pipeline steps for RTM Automation
"""

import os
import sys
import argparse
import importlib.util
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define the project root
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def load_module_from_path(file_path):
    """
    Dynamically load a Python module from a file path

    Args:
        file_path (str): Path to the Python file

    Returns:
        module: The loaded Python module or None if loading failed
    """
    try:
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error loading module from {file_path}: {e}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Test individual pipeline steps for RTM Automation"
    )
    parser.add_argument(
        "step",
        help="The pipeline step to test (word_to_md, extract_outline, etc.)"
    )
    parser.add_argument(
        "--input",
        help="Input file or directory (default: from config)"
    )
    parser.add_argument(
        "--output",
        help="Output file or directory (default: from config)"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file (default: config/paths.yaml)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    # Parse only known arguments, allowing others to pass to the target script
    args, unknown_args = parser.parse_known_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Map step names to file paths
    step_paths = {
        "word_to_md": os.path.join(PROJECT_ROOT, "src", "core", "word_to_md.py"),
        "extract_outline": os.path.join(PROJECT_ROOT, "src", "extractors", "extract_outline.py"),
        "extract_rtm": os.path.join(PROJECT_ROOT, "src", "extractors", "extract_rtm.py"),
        "md_to_json_yaml": os.path.join(PROJECT_ROOT, "src", "core", "md_to_json_yaml.py"),
        "sync_outline_files": os.path.join(PROJECT_ROOT, "src", "utils", "sync_outline_files.py")
    }

    if args.step not in step_paths:
        logger.error(f"Unknown step: {args.step}")
        logger.info(f"Available steps: {', '.join(step_paths.keys())}")
        return 1

    step_file = step_paths[args.step]
    if not os.path.isfile(step_file):
        logger.error(f"Step file not found: {step_file}")
        return 1

    # Load the module
    logger.info(f"Loading module for step '{args.step}' from {step_file}")
    module = load_module_from_path(step_file)
    if not module:
        return 1

    # Prepare arguments for the module's main function
    sys_args = [step_file]

    # Add explicit arguments
    if args.input:
        sys_args.extend(["--input", args.input])

    if args.output:
        sys_args.extend(["--output", args.output])

    if args.config:
        sys_args.extend(["--config", args.config])

    if args.verbose:
        sys_args.append("--verbose")

    # Add any unknown arguments passed through
    sys_args.extend(unknown_args)

    # If no input/output specified, use default directories
    if "--input-dir" not in " ".join(sys_args) and "--input" not in " ".join(sys_args):
        sys_args.extend(["--input-dir", os.path.join(PROJECT_ROOT, "input")])

    if "--output-dir" not in " ".join(sys_args) and "--output" not in " ".join(sys_args) and "-o" not in " ".join(sys_args):
        sys_args.extend(["--output-dir", os.path.join(PROJECT_ROOT, "output")])

    # Replace sys.argv with our arguments
    old_argv = sys.argv
    sys.argv = sys_args

    try:
        # Call the module's main function
        logger.info(f"Executing {args.step} with args: {sys_args[1:]}")
        result = module.main()
        return result
    except Exception as e:
        logger.error(f"Error executing {args.step}: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Restore sys.argv
        sys.argv = old_argv

if __name__ == "__main__":
    sys.exit(main())
