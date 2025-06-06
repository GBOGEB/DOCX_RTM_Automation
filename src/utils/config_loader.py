#!/usr/bin/env python3
"""
Configuration loader utility.

This module provides functions to load configurations from YAML files.
"""

import logging
from pathlib import Path

import yaml  # Moved yaml import after standard library

import sys
from pathlib import Path

# Add project root to path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


logger = logging.getLogger(__name__)

# Define the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(config_path=None):
    """
    Load configuration from YAML file.

    Args:
        config_path: Path to configuration file. If None, uses default path.

    Returns:
        Dictionary containing configuration or None if loading fails.
    """
    if not config_path:
        # Ensure config_path is a Path object for consistency
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
        return {}  # Return empty dict as per original behavior on error
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML configuration file %s: %s", config_file, e)
        return {}
    except Exception as e:  # pylint: disable=broad-except
        # Catch any other unexpected errors
        logger.error(
            "An unexpected error occurred while loading configuration from %s: %s",
            config_file,
            e,
        )
        return {}


def get_config_value(config, path, default=None):
    """
    Safely retrieve a value from a nested configuration dictionary.

    Args:
        config: Configuration dictionary
        path: List or dot-separated string of keys to traverse
        default: Default value to return if path doesn't exist

    Returns:
        Value at the specified path or default if not found
    """
    if isinstance(path, str):
        path = path.split(".")

    current = config
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current
