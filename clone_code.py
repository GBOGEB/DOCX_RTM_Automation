#!/usr/bin/env python3
"""
Repository Cloner for DOCX RTM Automation

This utility helps clone and manage external Git repositories needed by the project.
It supports both initial cloning and updating existing repositories.
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
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
    """Print formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print("=" * len(text))

def print_status(status, message, details=None):
    """Print status message with appropriate color"""
    if status == "SUCCESS":
        color = Colors.GREEN
    elif status == "WARNING":
        color = Colors.YELLOW
    elif status == "ERROR":
        color = Colors.RED
    else:
        color = Colors.BLUE
        
    print(f"{color}{status}{Colors.ENDC}: {message}")
    if details:
        print(f"     {details}")

def check_git_installed():
    """Check if Git is installed and available"""
    try:
        result = subprocess.run(
            ['git', '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception:
        return False, "Git executable not found in PATH"

def get_repo_list():
    """Get list of repositories to clone from config or use defaults"""
    repos_file = Path('config/repositories.json')
    
    # Create default repositories list if file doesn't exist
    if not repos_file.exists():
        default_repos = {
            "repositories": [
                {
                    "name": "DOCX_RTM_Automation",
                    "url": "https://github.com/GBOGEB/DOCX_RTM_Automation.git",
                    "branch": "main",
                    "target_dir": "external/DOCX_RTM_Automation",
                    "description": "Main RTM automation repository"
                },
                {
                    "name": "pandoc-word-reader",
                    "url": "https://github.com/pandoc/pandoc-word-reader.git",
                    "branch": "main",
                    "target_dir": "external/pandoc-word-reader",
                    "description": "Pandoc Word reader extension"
                }
            ]
        }
        
        # Create config directory if it doesn't exist
        repos_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save default repositories file
        with open(repos_file, 'w') as f:
            json.dump(default_repos, f, indent=2)
            
        print_status("INFO", f"Created default repositories file: {repos_file}")
        return default_repos["repositories"]
    
    # Load existing repositories file
    try:
        with open(repos_file, 'r') as f:
            data = json.load(f)
        return data.get("repositories", [])
    except Exception as e:
        print_status("ERROR", f"Failed to load repositories file: {e}")
        return []

def clone_repository(repo_info, update=True):
    """Clone or update a Git repository"""
    url = repo_info.get("url")
    branch = repo_info.get("branch", "main")
    target_dir = repo_info.get("target_dir")
    name = repo_info.get("name", url.split('/')[-1].split('.')[0])
    
    print_header(f"Processing repository: {name}")
    print(f"URL: {url}")
    print(f"Branch: {branch}")
    print(f"Target directory: {target_dir}")
    
    # Check if directory already exists
    if os.path.exists(target_dir):
        print_status("INFO", f"Directory already exists: {target_dir}")
        
        # Check if it's a git repository
        if not os.path.exists(os.path.join(target_dir, '.git')):
            print_status("ERROR", f"Directory exists but is not a Git repository: {target_dir}")
            return False
            
        # Update existing repository if requested
        if update:
            print_status("INFO", f"Updating existing repository...")
            
            # Save current directory
            current_dir = os.getcwd()
            
            try:
                # Change to target directory
                os.chdir(target_dir)
                
                # Fetch all branches
                fetch_result = subprocess.run(
                    ['git', 'fetch', '--all'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                if fetch_result.returncode != 0:
                    print_status("WARNING", f"Failed to fetch updates: {fetch_result.stderr}")
                
                # Check current branch
                branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                current_branch = branch_result.stdout.strip()
                
                # Checkout specified branch if different
                if current_branch != branch:
                    print_status("INFO", f"Switching from branch '{current_branch}' to '{branch}'")
                    checkout_result = subprocess.run(
                        ['git', 'checkout', branch],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        check=False
                    )
                    
                    if checkout_result.returncode != 0:
                        print_status("WARNING", f"Failed to switch branch: {checkout_result.stderr}")
                
                # Pull latest changes
                pull_result = subprocess.run(
                    ['git', 'pull', 'origin', branch],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                if pull_result.returncode == 0:
                    print_status("SUCCESS", f"Repository updated successfully")
                    return True
                else:
                    print_status("WARNING", f"Failed to pull changes: {pull_result.stderr}")
                    return False
            finally:
                # Return to original directory
                os.chdir(current_dir)
        else:
            print_status("INFO", f"Repository exists and update is disabled
