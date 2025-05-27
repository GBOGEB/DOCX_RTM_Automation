#!/usr/bin/env python3
"""
Utility to examine all the relevant files in the project
and report on their status.
"""

import os
import sys
import yaml
import json
from pathlib import Path

# ANSI Colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.ENDC}")

def print_file_info(file_path_str: str):
    """Print information about a file"""
    path = Path(file_path_str)
    print(f"\n--- Checking: {Colors.BOLD}{path}{Colors.ENDC} ---")

    if not path.exists():
        print_colored(f"  Status: MISSING", Colors.RED)
        return

    try:
        file_size = path.stat().st_size
        print(f"  Size: {file_size} bytes")

        if file_size == 0:
            print_colored("  Content: EMPTY FILE", Colors.YELLOW)
            if path.suffix.lower() in [".yaml", ".yml", ".json"]:
                print_colored(f"  {path.suffix.upper()} structure: EMPTY (cannot parse)", Colors.YELLOW)
            return

        # Read first few lines of the file
        try:
            preview_content = ""
            line_count = 0
            max_lines = 10
            max_bytes = 1024

            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if len(preview_content.encode('utf-8')) + len(line.encode('utf-8')) > max_bytes:
                        break
                    preview_content += line
                    line_count += 1
                    if line_count >= max_lines:
                        break

            if preview_content:
                print("  First few lines (or up to 1KB):")
                for line in preview_content.splitlines()[:max_lines]:
                    print(f"    {line.rstrip()}")
            else:
                print_colored("  Content: Could not read preview (possibly binary or very short).", Colors.YELLOW)

        except Exception as read_exc:
            print_colored(f"  Error reading file preview: {read_exc}", Colors.RED)

        # Try to parse if YAML or JSON
        suffix = path.suffix.lower()
        if suffix in [".yaml", ".yml"]:
            try:
                content = path.read_text(encoding="utf-8")
                if not content.strip():
                    print_colored("  YAML structure: EMPTY (whitespace only)", Colors.YELLOW)
                else:
                    data = yaml.safe_load(content)
                    print_colored("  YAML structure: VALID", Colors.GREEN)
                    check_outline_format(data, "YAML")
            except yaml.YAMLError as e:
                print_colored(f"  YAML structure: INVALID - {e}", Colors.RED)
            except Exception as e:
                print_colored(f"  Error processing YAML file {path}: {e}", Colors.RED)

        elif suffix == ".json":
            try:
                content = path.read_text(encoding="utf-8")
                if not content.strip():
                    print_colored("  JSON structure: EMPTY (whitespace only)", Colors.YELLOW)
                else:
                    data = json.loads(content)
                    print_colored("  JSON structure: VALID", Colors.GREEN)
                    check_outline_format(data, "JSON")
            except json.JSONDecodeError as e:
                print_colored(f"  JSON structure: INVALID - {e}", Colors.RED)
            except Exception as e:
                print_colored(f"  Error processing JSON file {path}: {e}", Colors.RED)

    except Exception as e:
        print_colored(f"  General error checking file {path}: {e}", Colors.RED)

def check_outline_format(data, file_type: str):
    """Checks for a basic outline structure in parsed data."""
    if isinstance(data, dict) and "sections" in data:
        if isinstance(data["sections"], list):
            section_count = len(data["sections"])
            valid_sections = 0
            if section_count > 0:
                for sec in data["sections"][:3]:
                    if isinstance(sec, dict) and "title" in sec and "level" in sec:
                        valid_sections += 1
                if valid_sections > 0:
                    print_colored(f"  {file_type} Outline: Appears VALID (found {section_count} sections, first {valid_sections} look ok)", Colors.GREEN)
                else:
                    print_colored(f"  {file_type} Outline: PARTIAL (found {section_count} sections, but structure mismatch)", Colors.YELLOW)
            else:
                print_colored(f"  {file_type} Outline: VALID (contains 'sections' key, but it's an empty list)", Colors.YELLOW)
        else:
            print_colored(f"  {file_type} Outline: INVALID ('sections' key is not a list)", Colors.RED)

    elif isinstance(data, list) and data:
        if isinstance(data[0], dict) and "title" in data[0]:
            print_colored(f"  {file_type} Outline: PARTIAL (list of {len(data)} items with titles, may need processing)", Colors.YELLOW)
        else:
            print_colored(f"  {file_type} Outline: UNKNOWN (list format, but not recognized section items)", Colors.YELLOW)
    else:
        print_colored(f"  {file_type} Outline: UNKNOWN or N/A (data is {type(data)}, not a recognized outline structure)", Colors.YELLOW)

def main():
    """Check all project files"""
    print_colored("=== Checking DOCX RTM Automation Project Files ===", Colors.BLUE + Colors.BOLD)

    files_to_check = [
        "input/MASTER_1805_1144.docx",
        "input/MASTER_outline.yaml",
        "output/MASTER_outline.yaml",
        "output/MASTER_outline.json",
        "output/MASTER_1805_1144.md",
        "output/MASTER_1805_1144.yaml",
        "output/MASTER_1805_1144.json",
        "output/RTM_QQQ.yaml",
        "config/paths.yaml",
        "config/rtm_config.yaml",
        "config/repositories.json",
        "run_pipeline.py",
        "src/core/generate_rtm.py",
        "scripts/clean_repository.py",
        "README.md",
        ".yamllint"
    ]

    for file_path_str in files_to_check:
        print_file_info(file_path_str)

    print_colored("\n=== File Check Complete ===", Colors.BLUE + Colors.BOLD)
    return 0

if __name__ == "__main__":
    sys.exit(main())
