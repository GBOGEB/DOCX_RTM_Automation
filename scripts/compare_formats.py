#!/usr/bin/env python3
"""
Compare JSON and YAML output files to ensure consistency between formats
"""

import os
import json
import yaml
import sys
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple, List
from difflib import unified_diff

# Define project root assuming script is in a subdirectory (e.g., scripts/)
# This helps in defining default paths relative to the project.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"


def load_file(file_path: Path) -> Dict[str, Any]:
    """Load data from either JSON or YAML file"""
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            if suffix == ".json":
                return json.load(f)
            elif suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return {}


def compare_structures(json_data: Dict[str, Any], yaml_data: Dict[str, Any]) -> bool:
    """Compare JSON and YAML structures for equivalence"""
    # Convert both to JSON strings and compare
    json_str = json.dumps(json_data, sort_keys=True)
    yaml_json_str = json.dumps(yaml_data, sort_keys=True)

    # If they're identical, return True
    if json_str == yaml_json_str:
        return True

    # Otherwise print differences
    print("Differences found between JSON and YAML:")

    json_lines = json.dumps(json_data, indent=2).splitlines()
    yaml_json_lines = json.dumps(yaml_data, indent=2).splitlines()

    diff = list(
        unified_diff(
            json_lines, yaml_json_lines, fromfile="JSON", tofile="YAML", lineterm=""
        )
    )

    for line in diff:
        print(line)

    return False


def compare_files(json_file: Path, yaml_file: Path) -> bool:
    """Compare a JSON and YAML file with the same base name"""
    print(f"Comparing: {json_file} <-> {yaml_file}")

    try:
        json_data = load_file(json_file)
        yaml_data = load_file(yaml_file)

        if not json_data or not yaml_data:
            print("One or both files failed to load properly")
            return False

        checksum_equal = check_data_checksums(json_data, yaml_data)
        if checksum_equal:
            print("✓ Files have identical content")
            return True
        else:
            return compare_structures(json_data, yaml_data)

    except Exception as e:
        print(f"Error comparing files: {e}")
        return False


def check_data_checksums(data1: Dict[str, Any], data2: Dict[str, Any]) -> bool:
    """Compare data checksums to check if content is identical"""
    json_str1 = json.dumps(data1, sort_keys=True)
    json_str2 = json.dumps(data2, sort_keys=True)

    hash1 = hashlib.md5(json_str1.encode("utf-8")).hexdigest()
    hash2 = hashlib.md5(json_str2.encode("utf-8")).hexdigest()

    return hash1 == hash2


def find_paired_files(directory: Path) -> List[Tuple[Path, Path]]:
    """Find paired JSON and YAML files with the same base name"""
    paired_files = []

    if not directory.exists():
        print(f"Directory not found: {directory}")
        return paired_files

    # Get all JSON files
    json_files = {file.stem: file for file in directory.glob("*.json")}

    # Find matching YAML files
    for yaml_file in directory.glob("*.yaml"):
        stem = yaml_file.stem
        if stem in json_files:
            paired_files.append((json_files[stem], yaml_file))

    return paired_files


def main():
    """Main function"""
    # Parse command line arguments
    args = sys.argv[1:]
    num_args = len(args)

    all_success = True

    if num_args == 2:
        # Compare specific files
        json_file = Path(args[0])
        yaml_file = Path(args[1])
        if not json_file.suffix == ".json" or not yaml_file.suffix in [".yaml", ".yml"]:
            print("Error: Please provide a .json file as the first argument and a .yaml/.yml file as the second.")
            sys.exit(1)
        all_success = compare_files(json_file, yaml_file)
    elif num_args == 1:
        # Check all paired files in the specified directory
        directory = Path(args[0])
        if not directory.is_dir():
            print(f"Error: {directory} is not a valid directory.")
            sys.exit(1)
        paired_files = find_paired_files(directory)

        if not paired_files:
            print(f"No paired JSON/YAML files found in {directory}")
            all_success = False
        else:
            print(f"Found {len(paired_files)} paired files to compare in {directory}")
            for json_f, yaml_f in paired_files:
                print("\n" + "=" * 50)
                success = compare_files(json_f, yaml_f)
                all_success = all_success and success
                print("=" * 50)
    elif num_args == 0:
        # Default to checking DEFAULT_OUTPUT_DIR
        output_dir = DEFAULT_OUTPUT_DIR
        if not output_dir.exists():
            print(f"Default output directory not found: {output_dir}")
            print("Please run the pipeline to generate output files first or specify a directory.")
            sys.exit(1)

        paired_files = find_paired_files(output_dir)

        if not paired_files:
            print(f"No paired JSON/YAML files found in default output directory: {output_dir}")
            print("Please run the pipeline to generate both formats first or specify a directory.")
            all_success = False
        else:
            print(f"Found {len(paired_files)} paired files to compare in {output_dir}")
            for json_f, yaml_f in paired_files:
                print("\n" + "=" * 50)
                success = compare_files(json_f, yaml_f)
                all_success = all_success and success
                print("=" * 50)
    else:
        print("Usage:")
        print(f"  {sys.argv[0]} <json_file> <yaml_file>  (to compare specific files)")
        print(f"  {sys.argv[0]} <directory>             (to compare all pairs in a directory)")
        print(f"  {sys.argv[0]}                         (to compare all pairs in default '{DEFAULT_OUTPUT_DIR}')")
        sys.exit(1)

    if all_success:
        print("\nAll comparisons completed successfully!" if num_args != 2 else "\nComparison successful!")
    else:
        print("\nSome comparisons failed!" if num_args != 2 else "\nComparison failed!")

    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
