import os

import yaml


def sync_outline_files():
    """Sync outline files from OneDrive to local project folder"""
    # Load configuration
    # Assuming paths.yaml is in the same directory as this script (config/)
    # or the path is relative to the execution directory.
    # For consistency with config_loader.py, let's ensure it's clear.
    # If this script is run from the project root, 'config/paths.yaml' is correct.
    # If run from config/, then 'paths.yaml' would be correct.
    # Given typical project structures, 'config/paths.yaml' when run from root is common.
    paths_config_file = "config/paths.yaml"
    if not os.path.exists(paths_config_file):
        # Fallback if script is inside config and paths.yaml is also there
        alt_paths_config_file = os.path.join(os.path.dirname(__file__), "paths.yaml")
        if os.path.exists(alt_paths_config_file):
            paths_config_file = alt_paths_config_file
        else:
            print(f"Warning: Paths configuration file {paths_config_file} not found.")
            return

    with open(paths_config_file) as file:
        yaml.safe_load(file)

    # Define file mappings (external → local)
