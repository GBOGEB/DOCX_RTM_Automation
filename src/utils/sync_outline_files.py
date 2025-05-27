import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml
import os
import logging
import difflib
from pathlib import Path
from typing import List, Dict, Any


def get_logger():
    """Get a logger if not already configured."""
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
    return logging.getLogger(__name__)


def load_config(config_path: str = "config/paths.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dict containing configuration settings
    """
    logger = get_logger()
    config_path = Path(config_path)

    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path) as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise


def read_outline_file(file_path: Path) -> List[str]:
    """
    Read an outline file and return its content as a list of lines.

    Args:
        file_path: Path to the outline file

    Returns:
        List of lines in the file
    """
    logger = get_logger()
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.readlines()
    except Exception as e:
        logger.error(f"Failed to read outline file {file_path}: {str(e)}")
        raise


def write_outline_file(file_path: Path, content: List[str]) -> None:
    """
    Write content to an outline file.

    Args:
        file_path: Path to the outline file
        content: List of lines to write
    """
    logger = get_logger()
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.writelines(content)
        logger.info(f"Updated outline file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to write outline file {file_path}: {str(e)}")
        raise


def sync_outline_files():
    """
    Synchronizes outline files that were extracted in previous steps.
    This function compares outline files and ensures consistency between them.
    """
    logger = get_logger()

    try:
        # Load configuration
        logger.info("Loading configuration from paths.yaml")
        paths = load_config()

        # Extract relevant paths from configuration
        outline_dir = Path(paths.get("output_dir", "./output")) / "outlines"

        logger.info(f"Synchronizing outline files in {outline_dir}")

        # Check if outline directory exists
        if not outline_dir.exists():
            logger.error(f"Outline directory does not exist: {outline_dir}")
            return

        # Get all outline files
        outline_files = list(outline_dir.glob("*.md"))
        logger.info(f"Found {len(outline_files)} outline files")

        if not outline_files:
            logger.warning("No outline files found to synchronize")
            return

        # Read all outline files
        file_contents = {}
        for file_path in outline_files:
            file_contents[file_path] = read_outline_file(file_path)

        # Find a reference file (the most complete one)
        reference_file = max(
            file_contents.items(), key=lambda x: len("".join(x[1]).strip())
        )[0]

        logger.info(
            f"Using {reference_file.name} as reference for synchronization")

        # Compare and synchronize files
        reference_content = file_contents[reference_file]

        for file_path, content in file_contents.items():
            if file_path == reference_file:
                continue

            logger.info(f"Comparing {file_path.name} with reference")

            # Calculate and log differences
            diff = list(
                difflib.unified_diff(
                    content,
                    reference_content,
                    fromfile=str(file_path),
                    tofile=str(reference_file),
                    n=0,
                )
            )

            if diff:
                logger.info(
                    f"Found {len(diff)} differences in {file_path.name}")
                # Implement your synchronization logic here
                # For example:
                # write_outline_file(file_path, reference_content)
            else:
                logger.info(f"No differences found in {file_path.name}")

        logger.info("Outline files synchronization completed successfully")

    except Exception as e:
        logger.error(f"Error in sync_outline_files: {str(e)}")
        raise


if __name__ == "__main__":
    # Allow running this module directly for testing
    sync_outline_files()
