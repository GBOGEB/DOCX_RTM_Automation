import yaml
import json
import re
import sys
from pathlib import Path

# Determine project root (assuming this script is in code/ subdirectory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main():
    paths_config_file = PROJECT_ROOT / "config" / "paths.yaml"
    if not paths_config_file.exists():
        print(f"Error: Configuration file not found at {paths_config_file}")
        sys.exit(1)

    with open(paths_config_file, "r", encoding="utf-8") as file:
        paths = yaml.safe_load(file)

    md_output_key = paths.get(
        "md_output", "output/default_master.md"
    )  # Default if not in config
    md_file_path = PROJECT_ROOT / md_output_key

    if not md_file_path.exists():
        print(f"Error: Markdown input file not found: {md_file_path}")
        sys.exit(1)

    with open(md_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = {
        "requirements": [
            l.strip() for l in lines if re.match(r"^QQQ_[0-9]{3}", l)
        ],  # Assuming QQQ_ is a requirement prefix
        "headings": [l.strip() for l in lines if re.match(r"^#{1,7}\s", l)],
    }

    yaml_output_key = paths.get(
        "yaml_output", "output/parsed_md_data.yaml"
    )  # Default if not in config
    json_output_key = paths.get(
        "json_output", "output/parsed_md_data.json"
    )  # Default if not in config

    yaml_output_file = PROJECT_ROOT / yaml_output_key
    json_output_file = PROJECT_ROOT / json_output_key

    # Ensure output directories exist
    yaml_output_file.parent.mkdir(parents=True, exist_ok=True)
    json_output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(yaml_output_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True)

    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Markdown ({md_file_path.name}) → YAML/JSON parsing complete.")
    print(f"   YAML output: {yaml_output_file}")
    print(f"   JSON output: {json_output_file}")


if __name__ == "__main__":
    main()
