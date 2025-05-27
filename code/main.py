#!/usr/bin/env python3
"""
Main entry point for DOCX RTM Automation
"""

import os
import sys
import logging
from pathlib import Path
import yaml  # Added for YAML processing

# Determine Project Root assuming main.py is in a subdirectory like 'code/'
PROJECT_ROOT_DIR = Path(__file__).parent.parent.resolve()

def setup_logging():
    """Setup logging with automatic directory creation"""
    logs_dir = PROJECT_ROOT_DIR / "logs"  # Use project root for logs
    logs_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "process.log", mode="a"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def load_openai_key():
    """Load the OpenAI API key from the path specified in config/paths.yaml."""
    logger = logging.getLogger(__name__)  # Use existing logger setup
    config_file_path = PROJECT_ROOT_DIR / "config" / "paths.yaml"

    if not config_file_path.exists():
        logger.error(f"Configuration file not found: {config_file_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")

    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration file {config_file_path}: {e}")
        raise ValueError(f"Error parsing YAML configuration file: {e}")
    except Exception as e:
        logger.error(f"Unexpected error reading configuration file {config_file_path}: {e}")
        raise

    try:
        openai_key_file_path_str = config_data['secrets']['openai_key_path']
        openai_key_file_path = Path(os.path.expandvars(openai_key_file_path_str))

        if not openai_key_file_path.is_absolute():
            pass

        if not openai_key_file_path.exists():
            logger.error(f"OpenAI API key file not found: {openai_key_file_path}")
            raise FileNotFoundError(f"OpenAI API key file not found: {openai_key_file_path}")

        with open(openai_key_file_path, 'r', encoding='utf-8') as key_file:
            openai_key = key_file.read().strip()
        
        if not openai_key:
            logger.error(f"OpenAI API key file is empty: {openai_key_file_path}")
            raise ValueError(f"OpenAI API key file is empty: {openai_key_file_path}")
            
        return openai_key

    except KeyError:
        logger.error("'openai_key_path' not found in secrets section of config/paths.yaml")
        raise KeyError("'openai_key_path' not found in secrets section of config/paths.yaml")
    except FileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading the OpenAI key: {e}")
        raise

def commit_outputs_to_git(files_to_commit, config_data):
    """Commit output files to git"""
    logger = setup_logging()
    original_cwd = os.getcwd()
    os.chdir(PROJECT_ROOT_DIR)  # Change to actual project root for git operations

    absolute_files_to_commit = []
    for f_rel in files_to_commit:
        abs_path = (PROJECT_ROOT_DIR / f_rel).resolve()
        if abs_path.exists():
            absolute_files_to_commit.append(str(abs_path))
        else:
            logger.warning(f"File {abs_path} not found for git add. Skipping.")
    if not absolute_files_to_commit:
        logger.warning("No existing files to commit. Skipping git add/commit.")
        os.chdir(original_cwd)
        return
    # Add your git add/commit logic here

def main():
    """Main function"""
    os.chdir(PROJECT_ROOT_DIR)  # Ensure CWD is project root
    logger = setup_logging()
    logger.info("Starting DOCX RTM Automation")
    print("DOCX RTM Automation - Main Entry Point")

    required_dirs = ["input", "output", "config", "src", "logs"]
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            logger.info(f"Directory exists: {dir_name}")
        else:
            logger.warning(f"Directory missing: {dir_name}")

    try:
        openai_key = load_openai_key()
        logger.info("OpenAI key loaded successfully")
    except FileNotFoundError as e:
        logger.error(e)
        return 1

    print("Hello")

    return 0

if __name__ == "__main__":
    sys.exit(main())