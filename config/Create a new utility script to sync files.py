import os
import shutil

import yaml


def sync_outline_files():
    """Sync outline files from OneDrive to local project folder"""
    # Load configuration
    with open("config/paths.yaml") as file:
        paths = yaml.safe_load(file)

    # Define file mappings (external → local)
    file_mappings = {
        paths.get("outline_yaml_external"): paths.get(
            "outline_yaml", "output/MASTER_outline.yaml"
        ),
        paths.get("numbered_outline_json_external"): paths.get(
            "numbered_outline_json", "output/MASTER_numbered_outline.json"
        ),
        paths.get("numbered_outline_yaml_external"): paths.get(
            "numbered_outline_yaml", "output/MASTER_numbered_outline.yaml"
        ),
        paths.get("outline_json_external"): paths.get(
            "outline_json", "output/MASTER_outline.json"
        ),
    }

    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)

    # Copy files
    for src, dst in file_mappings.items():
        if src and os.path.exists(src):
            print(f"Copying {os.path.basename(src)} to {dst}...")
            shutil.copy2(src, dst)
        else:
            print(f"Warning: Source file {src} not found.")

    print("✅ File synchronization complete.")


if __name__ == "__main__":
    sync_outline_files()
