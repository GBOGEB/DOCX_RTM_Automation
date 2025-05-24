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

def load_file(file_path: str) -> Dict[str, Any]:
    """Load data from either JSON or YAML file"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    suffix = path.suffix.lower()
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if suffix == '.json':
                return json.load(f)
            elif suffix in ['.yaml', '.yml']:
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
    
    diff = list(unified_diff(
        json_lines, 
        yaml_json_lines,
        fromfile='JSON', 
        tofile='YAML',
        lineterm=''
    ))
    
    for line in diff:
        print(line)
    
    return False

def compare_files(json_file: str, yaml_file: str) -> bool:
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
    
    hash1 = hashlib.md5(json_str1.encode('utf-8')).hexdigest()
    hash2 = hashlib.md5(json_str2.encode('utf-8')).hexdigest()
    
    return hash1 == hash2

def find_paired_files(directory: str) -> List[Tuple[str, str]]:
    """Find paired JSON and YAML files with the same base name"""
    paired_files = []
    
    dir_path = Path(directory)
    if not dir_path.exists():
        print(f"Directory not found: {directory}")
        return paired_files
    
    # Get all JSON files
    json_files = {file.stem: file for file in dir_path.glob('*.json')}
    
    # Find matching YAML files
    for yaml_file in dir_path.glob('*.yaml'):
        stem = yaml_file.stem
        if stem in json_files:
            paired_files.append((str(json_files[stem]), str(yaml_file)))
    
    return paired_files

def main():
    """Main function"""
    # Parse command line arguments
    if len(sys.argv) > 2:
        # Compare specific files
        json_file = sys.argv[1]
        yaml_file = sys.argv[2]
        success = compare_files(json_file, yaml_file)
        return 0 if success else 1
    
    elif len(sys.argv) > 1:
        # Check all paired files in directory
        directory = sys.argv[1]
        paired_files = find_paired_files(directory)
        
        if not paired_files:
            print(f"No paired JSON/YAML files found in {directory}")
            return 1
        
        print(f"Found {len(paired_files)} paired files to compare")
        
        all_success = True
        for json_file, yaml_file in paired_files:
            print("\n" + "=" * 50)
            success = compare_files(json_file, yaml_file)
            all_success = all_success and success
            print("=" * 50)
        
        if all_success:
            print("\nAll files compared successfully!")
        else:
            print("\nSome comparisons failed!")
        
        return 0 if all_success else 1
    
    else:
        # Default to checking output directory
        output_dir = 'output'
        if not os.path.exists(output_dir):
            print(f"Output directory not found: {output_dir}")
            print("Please run the pipeline to generate output files first.")
            return 1
        
        paired_files = find_paired_files(output_dir)
        
        if not paired_files:
            print("No paired JSON/YAML files found in output directory")
            print("Please run the pipeline to generate both formats first.")
            return 1
        
        print(f"Found {len(paired_files)} paired files to compare")
        
        all_success = True
        for json_file, yaml_file in paired_files:
            print("\n" + "=" * 50)
            success = compare_files(json_file, yaml_file)
            all_success = all_success and success
            print("=" * 50)
        
        if all_success:
            print("\nAll files compared successfully!")
        else:
            print("\nSome comparisons failed!")
        
        return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
