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

def git_first_commit():
    """Make initial commit with all files."""
    print("Adding all files...")
    run_command("git add .")
    
    print("Committing files...")
    run_command('git commit -m "Initial commit"')

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

def fix_permission_denied():
    """Fix 'Permission denied (publickey)' error by switching to HTTPS."""
    print("Fixing 'Permission denied (publickey)' error...")
    git_setup_remote(use_https=True)
    print("\nRemote URL changed to HTTPS. Try pushing again with:")
    print("git push -u origin main")
    print("\nNote: You'll be prompted for your GitHub username and password.")
    print("If you have 2FA enabled, use a personal access token instead of your password.")
    print("\nTo create a personal access token:")
    print("1. Go to GitHub → Settings → Developer settings → Personal access tokens → Generate new token")
    print("2. Select 'repo' scope")
    print("3. Generate and copy the token")
    print("4. Use this token as your password when prompted")

def main():
    """Main function to process command-line arguments."""
    parser = argparse.ArgumentParser(description="Helper script for Git operations")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Git command to run")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Git repository")
    
    # Setup remote command
    remote_parser = subparsers.add_parser("remote", help="Set up GitHub remote")
    remote_parser.add_argument("--url", help="GitHub repository URL", 
                              default="https://github.com/GBOGEB/DOCX_RTM_Automation.git")
    remote_parser.add_argument("--https", action="store_true", help="Use HTTPS instead of SSH", default=True)
    
    # Commit command
    commit_parser = subparsers.add_parser("commit", help="Make initial commit")
    
    # Push command
    push_parser = subparsers.add_parser("push", help="Push to GitHub")
    push_parser.add_argument("--branch", default="main", help="Branch to push to")
    
    # Clone command
    clone_parser = subparsers.add_parser("clone", help="Clone repository")
    clone_parser.add_argument("--url", help="GitHub repository URL", 
                             default="https://github.com/GBOGEB/DOCX_RTM_Automation.git")
    clone_parser.add_argument("--dir", help="Target directory")
    
    # Status command
    subparsers.add_parser("status", help="Show Git status")
    
    # Setup command (init + remote + commit + push)
    setup_parser = subparsers.add_parser("setup", help="Complete setup (init, remote, commit, push)")
    setup_parser.add_argument("--url", help="GitHub repository URL", 
                             default="https://github.com/GBOGEB/DOCX_RTM_Automation.git")
    
    # Fix permission denied command
    subparsers.add_parser("fix-permission", help="Fix 'Permission denied (publickey)' error")
    
    args = parser.parse_args()
    
    # Process commands
    if args.command == "init":
        git_init()
    elif args.command == "remote":
        git_setup_remote(args.url, args.https)
    elif args.command == "commit":
        git_first_commit()
    elif args.command == "push":
        git_push(args.branch)
    elif args.command == "clone":
        git_clone(args.url, args.dir)
    elif args.command == "status":
        git_status()
    elif args.command == "setup":
        git_init()
        git_setup_remote(args.url, True)  # Always use HTTPS for initial setup
        git_first_commit()
        git_push()
    elif args.command == "fix-permission":
        fix_permission_denied()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()