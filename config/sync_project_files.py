import os
import shutil

import yaml


def sync_outline_files():
    """Sync outline files from OneDrive to local project folder"""
    # Load configuration
    try:
        with open("config/paths.yaml") as file:
            paths = yaml.safe_load(file)
    except FileNotFoundError:
        print("Error: config/paths.yaml not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing config/paths.yaml: {e}")
        return

    if not paths:
        print("Error: config/paths.yaml is empty or invalid.")
        return

    # Define file mappings (external → local)
    file_mappings = {
        paths.get("outline_json_external"): paths.get("outline_json"),
        paths.get("outline_yaml_external"): paths.get("outline_yaml"),
        paths.get("numbered_outline_json_external"): paths.get(
            "local_numbered_outline_json"
        ),
        paths.get("numbered_outline_yaml_external"): paths.get(
            "local_numbered_outline_yaml"
        ),
    }

    # Copy files
    for src, dst in file_mappings.items():
        if src and dst and os.path.exists(src):
            print(f"Copying {os.path.basename(src)} to {dst}...")
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
        elif not src:
            print(f"Warning: Source path for {dst} is not defined in paths.yaml.")
        elif not os.path.exists(src):
            print(f"Warning: Source file {src} not found.")
        elif not dst:
            print(f"Warning: Destination path for {src} is not defined.")

    print("✅ File synchronization complete.")
