#!/usr/bin/env python3
"""
Repository Cleanup Tool

This script cleans up the repository by:
1. Removing empty files
2. Deleting empty directories
3. Organizing files into appropriate directories
4. Creating consistent directory structure
"""

import os
import sys
import shutil
from pathlib import Path
import re
import hashlib
import time

# ANSI colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'

def print_header(text):
    """Print header with formatting"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print("=" * len(text))

def print_status(status, message, details=None):
    """Print status with color coding"""
    if status == "DONE":
        color = Colors.GREEN
    elif status == "SKIP":
        color = Colors.YELLOW
    elif status == "ERROR":
        color = Colors.RED
    else:
        color = Colors.BLUE
        
    print(f"{color}{status}{Colors.ENDC}: {message}")
    if details:
        print(f"     {details}")

def get_file_hash(file_path):
    """Get hash of file contents"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def find_empty_files():
    """Find all empty files in the repository"""
    print_header("Finding Empty Files")
    
    empty_files = []
    for root, _, files in os.walk("."):
        # Skip hidden directories and venv
        if any(part.startswith('.') for part in Path(root).parts) or 'venv' in root or '__pycache__' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if os.path.getsize(file_path) == 0:
                    empty_files.append(file_path)
                    print_status("FOUND", f"Empty file: {file_path}")
            except Exception as e:
                print_status("ERROR", f"Error checking {file_path}: {e}")
    
    if not empty_files:
        print_status("INFO", "No empty files found")
    
    return empty_files

def find_empty_directories():
    """Find all empty directories in the repository"""
    print_header("Finding Empty Directories")
    
    empty_dirs = []
    for root, dirs, files in os.walk(".", topdown=False):
        # Skip hidden directories and venv
        if any(part.startswith('.') for part in Path(root).parts) or 'venv' in root or '__pycache__' in root:
            continue
        
        if not files and not dirs:
            empty_dirs.append(root)
            print_status("FOUND", f"Empty directory: {root}")
    
    if not empty_dirs:
        print_status("INFO", "No empty directories found")
    
    return empty_dirs

def find_duplicate_files():
    """Find duplicate files based on content"""
    print_header("Finding Duplicate Files")
    
    # Build file hash lookup
    file_hashes = {}
    duplicates = []
    
    for root, _, files in os.walk("."):
        # Skip hidden directories and venv
        if any(part.startswith('.') for part in Path(root).parts) or 'venv' in root or '__pycache__' in root:
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            file_hash = get_file_hash(file_path)
            
            if file_hash:
                if file_hash in file_hashes:
                    duplicates.append((file_path, file_hashes[file_hash]))
                    print_status("FOUND", f"Duplicate: {file_path}", f"Same as: {file_hashes[file_hash]}")
                else:
                    file_hashes[file_hash] = file_path
    
    if not duplicates:
        print_status("INFO", "No duplicate files found")
    
    return duplicates

def create_directory_structure():
    """Create standard directory structure for the project"""
    print_header("Creating Directory Structure")
    
    directories = [
        'src/core',
        'src/modules',
        'src/extractors',
        'src/utils',
        'config',
        'input',
        'output',
        'scripts',
        'docs',
        'tests'
    ]
    
    # Create directories
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print_status("DONE", f"Created directory: {directory}")
        except Exception as e:
            print_status("ERROR", f"Failed to create {directory}: {e}")
    
    # Create __init__.py files in Python package directories
    init_dirs = ['src', 'src/core', 'src/modules', 'src/extractors', 'src/utils']
    
    for directory in init_dirs:
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            try:
                with open(init_file, 'w') as f:
                    module_name = os.path.basename(directory)
                    f.write(f'"""\n{module_name.capitalize()} module for DOCX RTM Automation\n"""\n')
                print_status("DONE", f"Created __init__.py in {directory}")
            except Exception as e:
                print_status("ERROR", f"Failed to create __init__.py in {directory}: {e}")

def organize_files():
    """Organize files into appropriate directories based on patterns"""
    print_header("Organizing Files")
    
    # Define file patterns and their target directories
    file_patterns = [
        # Scripts
        (r'clean_.*\.py$', 'scripts'),
        (r'fix_.*\.py$', 'scripts'),
        (r'check_.*\.py$', 'scripts'),
        (r'generate_rtm\.py$', 'src/core'),
        (r'.*_outline\.py$', 'src/extractors'),
        
        # Tests
        (r'test_.*\.py$', 'tests'),
        
        # Documentation
        (r'.*\.md$', 'docs'),
    ]
    
    # Files that should stay in root directory
    root_files = [
        'run_pipeline.py', 
        'README.md',
        'requirements.txt',
        'setup.py',
        'run_tests.py',
        'clean_repository.py'  # This script
    ]
    
    # Process python files in root directory
    for file in os.listdir('.'):
        # Skip directories and non-python files
        if os.path.isdir(file) or not file.endswith('.py'):
            continue
            
        # Skip files that should stay in root
        if file in root_files:
            print_status("SKIP", f"Keeping {file} in root directory")
            continue
            
        # Find target directory based on file pattern
        target_dir = None
        for pattern, directory in file_patterns:
            if re.search(pattern, file):
                target_dir = directory
                break
        
        # Default to src/modules if no specific pattern matched
        if not target_dir:
            target_dir = 'src/modules'
        
        target_path = os.path.join(target_dir, file)
        
        # Skip if file already exists at target location
        if os.path.exists(target_path):
            print_status("SKIP", f"{file} already exists in {target_dir}")
            continue
            
        # Offer to move the file
        print_status("SUGGEST", f"Move {file} to {target_dir}/")

def clean_empty_files(files, simulate=True):
    """Delete empty files"""
    print_header("Cleaning Empty Files")
    
    if not files:
        print_status("SKIP", "No empty files to remove")
        return
    
    for file_path in files:
        try:
            if simulate:
                print_status("SIMULATE", f"Would remove: {file_path}")
            else:
                os.remove(file_path)
                print_status("DONE", f"Removed: {file_path}")
        except Exception as e:
            print_status("ERROR", f"Failed to remove {file_path}: {e}")

def clean_empty_dirs(dirs, simulate=True):
    """Delete empty directories"""
    print_header("Cleaning Empty Directories")
    
    if not dirs:
        print_status("SKIP", "No empty directories to remove")
        return
    
    for dir_path in dirs:
        try:
            if simulate:
                print_status("SIMULATE", f"Would remove directory: {dir_path}")
            else:
                os.rmdir(dir_path)
                print_status("DONE", f"Removed directory: {dir_path}")
        except Exception as e:
            print_status("ERROR", f"Failed to remove directory {dir_path}: {e}")

def create_gitkeep_files():
    """Create .gitkeep files to keep empty directories in git"""
    print_header("Creating .gitkeep Files")
    
    # Directories that should have .gitkeep files if empty
    important_dirs = [
        'input',
        'output', 
        'output/markdown',
        'output/json',
        'output/yaml',
        'output/rtm',
        'tests'
    ]
    
    for directory in important_dirs:
        if not os.path.exists(directory):
            continue
            
        # Check if directory is empty
        contents = os.listdir(directory)
        if not contents or (len(contents) == 1 and '.gitkeep' in contents):
            gitkeep_path = os.path.join(directory, '.gitkeep')
            
            if not os.path.exists(gitkeep_path):
                try:
                    with open(gitkeep_path, 'w') as f:
                        f.write("# This file ensures the directory is tracked by git\n")
                    print_status("DONE", f"Created .gitkeep in {directory}")
                except Exception as e:
                    print_status("ERROR", f"Failed to create .gitkeep in {directory}: {e}")

def integrate_with_pipeline():
    """Integrate the clean repository functionality with the pipeline"""
    print_header("Integrating with Pipeline")
    
    # Update paths.yaml to include clean_repository step if it doesn't exist
    try:
        import yaml
        
        config_path = 'config/paths.yaml'
        if not os.path.exists(config_path):
            print_status("ERROR", f"Configuration file not found: {config_path}")
            return
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Check if clean_repository step already exists
        if 'pipeline' in config and 'steps' in config['pipeline']:
            step_exists = any(step.get('name') == 'clean_repository' 
                             for step in config['pipeline']['steps'])
                             
            if not step_exists:
                # Add the clean_repository step
                clean_step = {
                    'name': 'clean_repository',
                    'script': 'clean_repository.py',
                    'enabled': False,
                    'args': ['--simulate']  # Default to simulate mode for safety
                }
                
                config['pipeline']['steps'].append(clean_step)
                
                # Save updated config
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                    
                print_status("DONE", "Added clean_repository step to pipeline configuration")
            else:
                print_status("SKIP", "clean_repository step already exists in pipeline configuration")
    except Exception as e:
        print_status("ERROR", f"Failed to update pipeline configuration: {e}")

def main():
    """Main function"""
    print_header("DOCX RTM Automation Repository Cleanup")
    print("This utility helps clean up and organize your repository structure.\n")
    
    # Parse command line arguments
    simulate = '--simulate' in sys.argv or '-s' in sys.argv
    force = '--force' in sys.argv or '-f' in sys.argv
    
    if simulate:
        print(f"{Colors.YELLOW}Running in simulation mode. No changes will be made.{Colors.ENDC}")
    else:
        print(f"{Colors.RED}Running in execution mode. Changes will be applied.{Colors.ENDC}")
        if not force:
            confirmation = input("Do you want to continue? (y/n): ")
            if confirmation.lower() not in ['y', 'yes']:
                print("Operation cancelled.")
                return 0
    
    # Record start time
    start_time = time.time()
    
    # Create directory structure (always safe to run)
    create_directory_structure()
    
    # Find empty files
    empty_files = find_empty_files()
    
    # Find empty directories
    empty_dirs = find_empty_directories()
    
    # Find duplicate files
    duplicates = find_duplicate_files()
    
    # Clean up empty files
    clean_empty_files(empty_files, simulate=simulate)
    
    # Clean up empty directories
    clean_empty_dirs(empty_dirs, simulate=simulate)
    
    # Organize files
    organize_files()
    
    # Create .gitkeep files
    create_gitkeep_files()
    
    # Integrate with pipeline
    integrate_with_pipeline()
    
    # Print summary
    elapsed_time = time.time() - start_time
    print_header("Cleanup Summary")
    print(f"Found {len(empty_files)} empty files")
    print(f"Found {len(empty_dirs)} empty directories")
    print(f"Found {len(duplicates)} duplicate files")
    print(f"Executed in {elapsed_time:.2f} seconds")
    
    if simulate:
        print(f"\n{Colors.YELLOW}This was a simulation. Run without --simulate to apply changes.{Colors.ENDC}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
