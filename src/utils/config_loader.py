#!/usr/bin/env python3
"""
Configuration loader utility.

This module provides functions to load configurations from YAML files.
"""

import os
import logging
from pathlib import Path

import yaml  # Moved yaml import after standard library

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
        config_path = os.path.join(PROJECT_ROOT, "config", "paths.yaml")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.info("Configuration loaded from %s", config_path)
            return config
    except Exception as e:  # pylint: disable=broad-except
        logger.error("Failed to load configuration: %s", e)
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
        path = path.split('.')

    current = config
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current
