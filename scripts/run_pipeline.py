#!/usr/bin/env python3
"""
DOCX RTM Automation Pipeline Runner

This script runs the complete document processing pipeline:
1. Convert Word documents to Markdown
2. Extract document structure
3. Generate Requirements Traceability Matrix
"""

import yaml
import os
import subprocess
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import re
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("pipeline.log"), logging.StreamHandler()],
)
logger = logging.getLogger("rtm-pipeline")


def git_operation(command, error_message, check=True):
    """Execute a git command and handle errors"""
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Git command successful: {' '.join(command)}")
        else:
            logger.warning(f"Git command warning: {' '.join(command)}")
            logger.warning(f"Output: {result.stderr}")
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"{error_message}: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None, e.returncode


def expand_variables(text, config):
    """Expand ${var} placeholders in strings using config values"""
    if not isinstance(text, str):
        return text

    # Find all ${variable} patterns and replace with config values
    pattern = r"\${([^}]*)}"

    def replace_var(match):
        var_name = match.group(1)
        if var_name in config:
            return str(config[var_name])
        return match.group(0)  # Return original if not found

    return re.sub(pattern, replace_var, text)


def expand_args_list(args_list, config):
    """Expand variables in a list of arguments"""
    if not args_list:
        return []

    expanded_args = []
    for arg in args_list:
        expanded_args.append(expand_variables(arg, config))

    return expanded_args


def setup_git_environment(config):
    """Setup or update Git repository environment"""
    repo_url = config.get("github", {}).get("repo_url")
    branch = config.get("github", {}).get("branch", "main")
    repo_path = config.get("github", {}).get("local_path", os.getcwd())

    logger.info("Setting up GitHub integration")

    # Check if we're in a git repo already
    if not os.path.exists(os.path.join(repo_path, ".git")):
        # Initialize a new repo
        logger.info(f"Initializing new Git repository in {repo_path}")

        # Initialize the repository
        output, code = git_operation(["git", "init"], "Failed to initialize repository")
        if code != 0:
            return False

        # Add the remote
        output, code = git_operation(
            ["git", "remote", "add", "origin", repo_url], "Failed to add remote"
        )
        if code != 0:
            return False

    else:
        # We're already in a git repo, make sure remote is correctly set
        logger.info(f"Using existing Git repository in {repo_path}")

        # Check if origin remote exists
        output, code = git_operation(
            ["git", "remote", "get-url", "origin"],
            "Failed to get remote URL",
            check=False,
        )

        if code != 0:
            # Add the remote if it doesn't exist
            output, code = git_operation(
                ["git", "remote", "add", "origin", repo_url], "Failed to add remote"
            )
            if code != 0:
                return False
        elif output != repo_url:
            # Update the remote URL if it's different
            output, code = git_operation(
                ["git", "remote", "set-url", "origin", repo_url],
                "Failed to update remote URL",
            )
            if code != 0:
                return False

        # Try to fetch but don't fail if it doesn't work (might be first push)
        git_operation(
            ["git", "fetch", "origin"],
            "Warning: Could not fetch from remote (this might be normal for new repositories)",
            check=False,
        )

        # Try to checkout branch, create if it doesn't exist
        output, code = git_operation(
            ["git", "checkout", branch],
            f"Failed to checkout branch {branch}",
            check=False,
        )

        if code != 0:
            # Create the branch if it doesn't exist
            output, code = git_operation(
                ["git", "checkout", "-b", branch], f"Failed to create branch {branch}"
            )
            if code != 0:
                return False

    # Configure Git identity if provided in config
    git_user = config.get("github", {}).get("user_name")
    git_email = config.get("github", {}).get("user_email")

    if git_user:
        git_operation(
            ["git", "config", "user.name", git_user], "Failed to set git user name"
        )

    if git_email:
        git_operation(
            ["git", "config", "user.email", git_email], "Failed to set git user email"
        )

    logger.info("Git environment setup completed successfully")
    return True


def commit_changes(config, message="Pipeline execution results"):
    """Commit and push changes after pipeline execution"""
    branch = config.get("github", {}).get("branch", "main")

    logger.info("Committing changes to GitHub")

    # Add all changes
    output, code = git_operation(["git", "add", "."], "Failed to stage changes")
    if code != 0:
        return False

    # Check if there are changes to commit
    output, code = git_operation(
        ["git", "status", "--porcelain"], "Failed to get git status"
    )

    if not output:
        logger.info("No changes to commit")
        return True

    # Commit changes
    output, code = git_operation(
        ["git", "commit", "-m", message], "Failed to commit changes"
    )
    if code != 0:
        return False

    # Push changes - use --set-upstream for first push
    output, code = git_operation(
        ["git", "push", "--set-upstream", "origin", branch],
        f"Failed to push changes to {branch}",
    )
    if code != 0:
        return False

    logger.info("Changes successfully committed and pushed")
    return True


def check_prerequisites():
    """Check if all prerequisites are met"""
    logger.info("Checking prerequisites...")

    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (
        python_version.major == 3 and python_version.minor < 8
    ):
        logger.error(
            f"Python 3.8 or higher required. Current version: {python_version.major}.{python_version.minor}"
        )
        return False

    logger.info(
        f"Python version check passed: {python_version.major}.{python_version.minor}"
    )

    # Check for config directory and paths.yaml
    if not os.path.exists("config/paths.yaml"):
        logger.error("Missing config/paths.yaml configuration file")
        return False

    logger.info("Configuration file check passed")

    # Check for required directories
    required_dirs = ["input", "output", "src"]
    for directory in required_dirs:
        if not os.path.isdir(directory):
            logger.warning(f"Creating missing directory: {directory}")
            os.makedirs(directory, exist_ok=True)

    logger.info("Prerequisite check completed successfully")
    return True


def run_pipeline():
    """Run the document processing pipeline defined in paths.yaml"""
    start_time = time.time()
    logger.info("Starting RTM automation pipeline")

    # Check prerequisites
    if not check_prerequisites():
        logger.error("Prerequisite check failed. Aborting pipeline.")
        return False

    # Load configuration
    try:
        with open("config/paths.yaml", "r") as file:
            config = yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return False

    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Setup Git environment if CI integration is enabled
    if config.get("github", {}).get("enabled", False):
        if not setup_git_environment(config):
            logger.warning(
                "Failed to setup Git environment. Continuing with pipeline..."
            )

    # Get pipeline steps
    pipeline_steps = config.get("pipeline", {}).get("steps", [])
    if not pipeline_steps:
        logger.error("No pipeline steps defined in configuration.")
        return False

    # Execute each enabled step
    python_path = config.get("python_path", "python")
    all_steps_success = True

    for step in pipeline_steps:
        if step.get("enabled", False):
            script_path = step.get("script")
            name = step.get("name", script_path)

            if not script_path:
                logger.warning(f"No script defined for step '{name}', skipping.")
                continue

            step_start_time = time.time()
            logger.info(f"Running pipeline step: {name}")

            # Get arguments for the step and expand any variables
            args = step.get("args", [])
            expanded_args = expand_args_list(args, config)

            # Construct the command
            cmd = [python_path, script_path] + expanded_args

            try:
                process = subprocess.run(cmd, check=True)
                step_duration = time.time() - step_start_time
                logger.info(
                    f"Step '{name}' completed successfully in {step_duration:.2f} seconds."
                )
            except subprocess.CalledProcessError as e:
                step_duration = time.time() - step_start_time
                logger.error(
                    f"Error running step '{name}' after {step_duration:.2f} seconds: {e}"
                )
                all_steps_success = False
                # Decide whether to continue or break based on config
                if config.get("pipeline", {}).get("stop_on_error", True):
                    break

    # Compare JSON and YAML outputs if both exist
    logger.info("Comparing JSON and YAML outputs...")
    compare_script = "scripts/compare_formats.py"
    if os.path.exists(compare_script):
        try:
            subprocess.run([python_path, compare_script], check=False)
        except Exception as e:
            logger.warning(f"Could not compare output formats: {e}")
    else:
        logger.warning("Format comparison script not found. Skipping comparison.")

    # Commit changes if CI integration is enabled and pipeline was successful
    if config.get("github", {}).get("enabled", False) and all_steps_success:
        commit_message = config.get("github", {}).get(
            "commit_message", "Automatic update from pipeline"
        )
        commit_changes(config, commit_message)

    total_duration = time.time() - start_time
    if all_steps_success:
        logger.info(
            f"Pipeline execution completed successfully in {total_duration:.2f} seconds!"
        )
    else:
        logger.warning(
            f"Pipeline execution completed with errors in {total_duration:.2f} seconds."
        )

    return all_steps_success


if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)
