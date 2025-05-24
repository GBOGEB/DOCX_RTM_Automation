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

def print_file_info(file_path):
    """Print information about a file"""
    path = Path(file_path)
    
    if not path.exists():
        print(f"\n{path}:")
        print("  Status: MISSING")
        return
    
    file_size = path.stat().st_size
    print(f"\n{path}:")
    print(f"  Size: {file_size} bytes")
    
    # Read first few lines of the file
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            first_lines = [next(f) for _ in range(10) if f]
        
        print("  First few lines:")
        for line in first_lines:
            print(f"    {line.rstrip()}")
        
        # Try to parse if YAML or JSON
        suffix = path.suffix.lower()
        if suffix in ['.yaml', '.yml']:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                print("  YAML structure: VALID")
                
                # Check for expected outline structure
                if isinstance(data, dict) and 'sections' in data:
                    section_count = len(data.get('sections', []))
                    print(f"  Outline format: VALID (contains {section_count} sections)")
                elif isinstance(data, list) and data and isinstance(data[0], dict) and 'title' in data[0]:
                    print(f"  Outline format: PARTIAL (contains {len(data)} list items with titles)")
                else:
                    print("  Outline format: INVALID (missing expected structure)")
            except yaml.YAMLError as e:
                print(f"  YAML structure: INVALID - {str(e)}")
        
        elif suffix == '.json':
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print("  JSON structure: VALID")
                
                # Check for expected outline structure
                if isinstance(data, dict) and 'sections' in data:
                    section_count = len(data.get('sections', []))
                    print(f"  Outline format: VALID (contains {section_count} sections)")
                else:
                    print("  Outline format: INVALID (missing expected structure)")
            except json.JSONDecodeError as e:
                print(f"  JSON structure: INVALID - {str(e)}")
        
    except Exception as e:
        print(f"  Error reading file: {str(e)}")

def main():
    """Check all project files"""
    print("=== Checking DOCX RTM Automation Project Files ===")
    
    # Files to check
    files_to_check = [
        # Input files
        "input/MASTER_1805_1144.docx",
        "input/MASTER_outline.yaml",
        "input/MASTER_outline.json",
        "input/MASTER_numbered_outline.yaml",
        "input/MASTER_numbered_outline.json",
        
        # Output files
        "output/MASTER_outline.yaml",
        "output/MASTER_outline.json",
        "output/MASTER_1805_1144.md",
        "output/MASTER_1805_1144.yaml",
        "output/MASTER_1805_1144.json",
        "output/RTM_QQQ.yaml",
        
        # Config files
        "config/paths.yaml",
        "config/rtm_config.yaml"
    ]
    
    for file_path in files_to_check:
        print_file_info(file_path)
    
    print("\n=== File Check Complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
