#!/usr/bin/env python3
"""
DOCX RTM (Requirements Traceability Matrix) Automation
Main entry point for the RTM automation process.

This script orchestrates the entire RTM generation pipeline.
"""

import sys
import logging
import argparse
from pathlib import Path
import importlib.util
import traceback
import yaml

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
log_dir = PROJECT_ROOT / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_filename = log_dir / "process.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def load_config(config_path=None):
    """Load configuration from YAML file."""
    if not config_path:
        config_file = PROJECT_ROOT / "config" / "paths.yaml"
    else:
        config_file = Path(config_path)

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.info("Configuration loaded from %s", config_file)
            return config
    except FileNotFoundError:
        logger.error("Configuration file not found: %s", config_file)
        return None
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML configuration file %s: %s", config_file, e)
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.error(
            "An unexpected error occurred while loading configuration from %s: %s",
            config_file,
            e,
        )
        return None


def load_openai_api_key(config):
    """Load OpenAI API key from the file specified in config."""
    api_key_file_path_str = (
        None  # Initialize to avoid reference before assignment in except
    )
    try:
        if (
            not config
            or "openai" not in config
            or "api_key_file" not in config["openai"]
        ):
            # Check for secrets section as fallback
            if (
                config
                and "secrets" in config
                and "openai_key_path" in config["secrets"]
            ):
                api_key_file_path_str = config["secrets"]["openai_key_path"]
            else:
                logger.error("'api_key_file' not found in config/paths.yaml.")
                return None
        else:
            api_key_file_path_str = config["openai"]["api_key_file"]

        api_key_path = Path(api_key_file_path_str)
        # Convert to absolute path if it's a relative path
        if not api_key_path.is_absolute():
            api_key_path = PROJECT_ROOT / api_key_path

        # Read the API key from the file
        with open(api_key_path, "r", encoding="utf-8") as f:
            api_key = f.read().strip()

        if not api_key or api_key.startswith("sk-your-openai-api-key-goes-here"):
            logger.warning(
                "API key file at %s contains a placeholder value.", api_key_path
            )
            return None

        logger.info("OpenAI API key loaded successfully from %s.", api_key_path)
        return api_key
    except FileNotFoundError:
        logger.error(
            "API key file not found: %s",
            api_key_path if "api_key_path" in locals() else api_key_file_path_str,
        )
        return None
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error loading OpenAI API key: %s", str(e))
        return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DOCX RTM Automation")

    # Input and output options
    parser.add_argument("--input-dir", help="Directory containing input files")
    parser.add_argument("--output-dir", help="Directory for output files")
    parser.add_argument("--config", help="Path to configuration file")

    # Pipeline options
    parser.add_argument("--steps", nargs="+", help="Specific pipeline steps to run")
    parser.add_argument("--skip-steps", nargs="+", help="Pipeline steps to skip")

    # Miscellaneous options
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )

    return parser.parse_args()


def execute_pipeline_step_via_python(script_path_str, input_dir_str, output_dir_str):
    """Execute a Python script directly using sys.argv modification."""
    script_path = Path(script_path_str)
    input_dir = Path(input_dir_str)
    output_dir = Path(output_dir_str)
    try:
        # Add directory containing the script to sys.path
        script_dir = script_path.parent
        sys.path.insert(0, str(script_dir))

        # Load the module
        module_name = script_path.stem
        spec = importlib.util.spec_from_file_location(module_name, str(script_path))
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        # Execute the module
        spec.loader.exec_module(module)

        # Backup sys.argv and replace with our arguments
        old_argv = sys.argv.copy()
        sys.argv = [
            str(script_path),
            "--input-dir",
            str(input_dir),
            "--output-dir",
            str(output_dir),
        ]

        # Execute the main function if it exists
        if hasattr(module, "main"):
            module.main()

        # Restore sys.argv
        sys.argv = old_argv

        return True
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Error executing Python script %s: %s", script_path, e)
        traceback.print_exc()
        return False


def execute_pipeline(config, args):
    """Execute the RTM automation pipeline based on configuration."""
    logger.info("Executing RTM automation pipeline...")

    # Get pipeline steps from config
    pipeline_steps = []
    if config and "pipeline" in config and "steps" in config["pipeline"]:
        pipeline_steps = config["pipeline"]["steps"]

    if not pipeline_steps:
        logger.error("No pipeline steps defined in configuration")
        return False

    # Filter steps based on command line arguments
    if args.steps:
        pipeline_steps = [step for step in pipeline_steps if step["name"] in args.steps]
    if args.skip_steps:
        pipeline_steps = [
            step for step in pipeline_steps if step["name"] not in args.skip_steps
        ]

    # Get input and output directories
    input_dir_str = args.input_dir
    if not input_dir_str and "paths" in config and "input_dir" in config["paths"]:
        input_dir = PROJECT_ROOT / config["paths"]["input_dir"]
    elif input_dir_str:
        input_dir = Path(input_dir_str)
    else:
        input_dir = PROJECT_ROOT / "input"

    output_dir_str = args.output_dir
    if not output_dir_str and "paths" in config and "output_dir" in config["paths"]:
        output_dir = PROJECT_ROOT / config["paths"]["output_dir"]
    elif output_dir_str:
        output_dir = Path(output_dir_str)
    else:
        output_dir = PROJECT_ROOT / "output"

    # Execute each enabled pipeline step
    for step in pipeline_steps:
        if step.get("enabled", True):
            step_name = step.get("name", "unnamed_step")
            script_path_str = step.get("script")

            if not script_path_str:
                logger.warning("No script defined for step '%s', skipping", step_name)
                continue

            script_path = Path(script_path_str)
            # Convert to absolute path if it's a relative path
            if not script_path.is_absolute():
                script_path = PROJECT_ROOT / script_path

            if not script_path.exists():
                logger.error(
                    "Script not found for step '%s': %s", step_name, script_path
                )
                continue

            if args.dry_run:
                logger.info("[DRY RUN] Would execute: %s", script_path)
                continue

            logger.info("Executing pipeline step '%s': %s", step_name, script_path)
            try:
                # Direct Python execution for better handling of arguments
                success = execute_pipeline_step_via_python(
                    str(script_path), str(input_dir), str(output_dir)
                )

                if not success:
                    logger.error("Step '%s' failed", step_name)
                    return False

                logger.info("Step '%s' completed successfully", step_name)
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Error executing step '%s': %s", step_name, e)
                return False

    logger.info("Pipeline execution completed successfully")
    return True


def main():
    """Main function."""
    logger.info("Starting DOCX RTM Automation process...")

    # Parse command line arguments
    args = parse_arguments()

    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Load configuration
    config = load_config(args.config)
    if not config:
        logger.critical("Failed to load configuration. Exiting.")
        return 1

    # Load OpenAI API key if needed
    api_key = load_openai_api_key(config)
    if not api_key:
        # This is now just a warning as OpenAI might not be required
        logger.warning("Failed to load OpenAI API key. Some features might not work.")

    # Execute the main pipeline
    success = execute_pipeline(config, args)
    if not success:
        logger.critical("Pipeline execution failed. Exiting.")
        return 1

    logger.info("DOCX RTM Automation process completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
