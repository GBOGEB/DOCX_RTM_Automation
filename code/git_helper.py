#!/usr/bin/env python3
"""
Git Helper Script
----------------
This script provides a simplified interface for common Git operations.
"""

import os
import sys
import subprocess
import argparse
import webbrowser
from pathlib import Path

def run_command(command, verbose=True):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True,
            capture_output=True,
            text=True
        )
        if verbose and result.stdout:
            print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return None

def git_status():
    """Show the current Git status."""
    print("Current Git status:")
    run_command("git status")

def git_init():
    """Initialize a new Git repository."""
    print("Initializing Git repository...")
    run_command("git init")
    
    # Create .gitignore if it doesn't exist
    if not Path(".gitignore").exists():
        print("Creating default .gitignore file...")
        with open(".gitignore", "w") as f:
            f.write("# Python artifacts\n__pycache__/\n*.py[cod]\n*$py.class\n")
            f.write("# Logs and outputs\nlogs/\n*.log\noutput/\n")
            f.write("# IDE files\n.idea/\n.vscode/\n*.swp\n.DS_Store\n")
    
    # Create README.md if it doesn't exist
    if not Path("README.md").exists():
        print("Creating basic README.md file...")
        with open("README.md", "w") as f:
            f.write("# DOCX RTM Automation\n\n")
            f.write("This tool automates the process of converting Word documents to markdown, ")
            f.write("extracting outlines and requirements traceability matrices (RTM), ")
            f.write("and synchronizing the content.\n")

def git_setup_remote(remote_url=None, use_https=True):
    """Set up GitHub remote."""
    if remote_url is None:
        remote_url = "https://github.com/GBOGEB/DOCX_RTM_Automation.git" if use_https else "git@github.com:GBOGEB/DOCX_RTM_Automation.git"
    elif remote_url.startswith("git@") and use_https:
        # Convert SSH URL to HTTPS
        remote_url = "https://github.com/" + remote_url.split(":")[-1]
    elif remote_url.startswith("https://") and not use_https:
        # Convert HTTPS URL to SSH
        parts = remote_url.split("/")
        remote_url = f"git@github.com:{parts[-2]}/{parts[-1]}"
    
    # Check if remote exists
    remotes = run_command("git remote", verbose=False)
    if remotes and "origin" in remotes:
        print("Updating origin remote...")
        run_command(f"git remote set-url origin {remote_url}")
    else:
        print("Adding origin remote...")
        run_command(f"git remote add origin {remote_url}")
    
    print(f"Remote URL set to: {remote_url}")

def check_git_identity():
    """Check and configure Git user identity if needed."""
    name = run_command("git config --global user.name", verbose=False)
    email = run_command("git config --global user.email", verbose=False)
    
    if not name or not email:
        print("\nGit identity not fully configured. Let's set it up:")
        
        if not name:
            name = input("Enter your name for Git commits: ")
            if name:
                run_command(f'git config --global user.name "{name}"')
        
        if not email:
            email = input("Enter your email for Git commits: ")
            if email:
                run_command(f'git config --global user.email "{email}"')
                
        print("Git identity configured successfully.")
    return name and email

def check_repo_exists(repo_url):
    """Check if a GitHub repository exists."""
    # Convert the URL to the API endpoint
    if repo_url.endswith('.git'):
        repo_url = repo_url[:-4]
    
    if repo_url.startswith('https://github.com/'):
        parts = repo_url.split('/')
        api_url = f'https://api.github.com/repos/{parts[3]}/{parts[4]}'
        
        # Use curl to check if the repo exists
        result = run_command(f'curl -s -o /dev/null -w "%{{http_code}}" {api_url}', verbose=False)
        return result and result.strip() == '200'
    
    return False

def create_github_repo(repo_name, username=None):
    """Open browser to create a new GitHub repository."""
    if username:
        repo_name = f"{username}/{repo_name}"
    
    print(f"\nRepository '{repo_name}' doesn't exist on GitHub.")
    print("Opening GitHub to create a new repository...\n")
    
    # Extract repository name from URL if needed
    if '/' in repo_name:
        repo_name = repo_name.split('/')[-1]
    
    # Open the GitHub new repository page
    webbrowser.open(f'https://github.com/new?name={repo_name}')
    
    print("Please complete these steps:")
    print("1. Sign in to GitHub if prompted")
    print("2. Enter repository name: " + repo_name)
    print("3. Add a description (optional)")
    print("4. Choose public or private")
    print("5. DO NOT initialize with README, .gitignore, or license")
    print("6. Click 'Create repository'")
    
    input("\nAfter creating the repository, press Enter to continue...")

def git_first_commit():
    """Make initial commit with all files."""
    # Check if there are any changes to commit
    status = run_command("git status --porcelain", verbose=False)
    if not status:
        print("No changes to commit. Repository is clean.")
        return False
    
    # Ensure Git identity is configured
    if not check_git_identity():
        print("Git identity configuration required before committing.")
        return False
    
    print("Adding all files...")
    run_command("git add .")
    
    print("Committing files...")
    result = run_command('git commit -m "Initial commit"', verbose=False)
    
    if result:
        print("Files committed successfully.")
        return True
    else:
        print("Commit failed. Please check previous error messages.")
        return False

def git_push(branch="main"):
    """Push changes to GitHub."""
    # Check current branch
    current_branch = run_command("git rev-parse --abbrev-ref HEAD", verbose=False).strip()
    
    if current_branch != branch:
        # Try to checkout the branch
        print(f"Switching to {branch} branch...")
        result = run_command(f"git checkout {branch}", verbose=False)
        
        # If branch doesn't exist, create it
        if not result:
            print(f"Creating {branch} branch...")
            run_command(f"git checkout -b {branch}")
    
    print(f"Pushing to GitHub ({branch} branch)...")
    run_command(f"git push -u origin {branch}")

def git_clone(repo_url=None, target_dir=None):
    """Clone the repository."""
    if repo_url is None:
        repo_url = "https://github.com/GBOGEB/DOCX_RTM_Automation.git"
    
    command = f"git clone {repo_url}"
    
    if target_dir:
        command += f" {target_dir}"
    
    print(f"Cloning repository from {repo_url}...")
    run_command(command)

def create_project_structure():
    """Create basic project structure if it doesn't exist."""
    directories = [
        "config", 
        "input", 
        "output", 
        "output/outlines", 
        "logs", 
        "scripts",
        "code"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Create a sample config file if it doesn't exist
    config_path = Path("config/paths.yaml")
    if not config_path.exists():
        with open(config_path, "w") as f:
            f.write("# Configuration paths\n")
            f.write("input_dir: './input'\n")
            f.write("output_dir: './output'\n")
            f.write("temp_dir: './temp'\n")
    
    print("Project structure created/verified.")

def git_setup_repo():
    """Set up a complete GitHub repository with proper structure."""
    # Check if already a Git repo
    is_git_repo = Path(".git").exists()
    if not is_git_repo:
        git_init()
    else:
        print("Git repository already initialized.")
    
    # Create project structure
    create_project_structure()
    
    # Configure remote
    repo_url = "https://github.com/GBOGEB/DOCX_RTM_Automation.git"
    
    # Extract username and repo name for GitHub check
    parts = repo_url.split("/")
    username = parts[3]
    repo_name = parts[4].replace(".git", "")
    
    # Check if repo exists on GitHub
    exists = check_repo_exists(repo_url)
    if not exists:
        create_github_repo(repo_name, username)
    
    # Set up remote
    git_setup_remote(repo_url, use_https=True)
    
    # Make initial commit
    committed = git_first_commit()
    
    # If commit