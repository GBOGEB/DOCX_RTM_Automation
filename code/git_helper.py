#!/usr/bin/env python3
"""
Git Helper Script
----------------
This script provides a simplified interface for common Git operations.
It is intended to be run from the root of the Git repository it manages.
"""

import os
import sys
import subprocess
import argparse
import webbrowser
from pathlib import Path


def run_command(command: list, verbose=True, working_dir=None):
    """Run a shell command (provided as a list of arguments) and return the output."""
    command_str_for_log = " ".join(command)

    try:
        result = subprocess.run(
            command,  # Command as a list
            shell=False,  # Use shell=False for security and predictability
            check=True,
            capture_output=True,
            text=True,
            cwd=working_dir,
        )
        if verbose and result.stdout:
            print(result.stdout)
        return result.stdout.strip() if result.stdout else ""
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command_str_for_log}")
        print(f"Error message: {e.stderr.strip() if e.stderr else 'No stderr'}")
        if e.stdout:  # Also print stdout from the error if it exists
            print(f"Stdout: {e.stdout.strip()}")
        return None
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
        print(f"Full command: {command_str_for_log}")
        return None
    except Exception as e_gen:
        print(f"An unexpected error occurred with command: {command_str_for_log}: {e_gen}")
        return None


def git_status():
    """Show the current Git status."""
    print("Current Git status:")
    run_command(["git", "status"])


def git_init():
    """Initialize a new Git repository in the current directory."""
    print("Initializing Git repository...")
    run_command(["git", "init"])

    # Create .gitignore if it doesn't exist
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print("Creating default .gitignore file...")
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("# Python artifacts\n__pycache__/\n*.py[cod]\n*$py.class\n")
            f.write("# Logs and outputs\nlogs/\n*.log\noutput/\n")
            f.write("# IDE files\n.idea/\n.vscode/\n*.swp\n.DS_Store\n")

    # Create README.md if it doesn't exist
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("Creating basic README.md file...")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# DOCX RTM Automation\n\n")
            f.write(
                "This tool automates the process of converting Word documents to markdown, "
            )
            f.write(
                "extracting outlines and requirements traceability matrices (RTM), "
            )
            f.write("and synchronizing the content.\n")


def git_setup_remote(remote_url=None, use_https=True):
    """Set up GitHub remote."""
    if remote_url is None:
        remote_url = (
            "https://github.com/GBOGEB/DOCX_RTM_Automation.git"
            if use_https
            else "git@github.com:GBOGEB/DOCX_RTM_Automation.git"
        )
    elif remote_url.startswith("git@") and use_https:
        remote_url = "https://github.com/" + remote_url.split(":")[-1]
    elif remote_url.startswith("https://") and not use_https:
        parts = remote_url.split("/")
        remote_url = f"git@github.com:{parts[-2]}/{parts[-1]}"

    current_remotes_str = run_command(["git", "remote"], verbose=False)
    current_remotes = current_remotes_str.splitlines() if current_remotes_str else []

    if "origin" in current_remotes:
        print("Updating origin remote...")
        run_command(["git", "remote", "set-url", "origin", remote_url])
    else:
        print("Adding origin remote...")
        run_command(["git", "remote", "add", "origin", remote_url])

    print(f"Remote URL set to: {remote_url}")


def check_git_identity():
    """Check and configure Git user identity if needed."""
    name = run_command(["git", "config", "--global", "user.name"], verbose=False)
    email = run_command(["git", "config", "--global", "user.email"], verbose=False)

    if not name or not name.strip():
        name = None
    if not email or not email.strip():
        email = None

    if not name or not email:
        print("\nGit identity not fully configured. Let's set it up:")

        if not name:
            name_input = input("Enter your name for Git commits: ").strip()
            if name_input:
                run_command(["git", "config", "--global", "user.name", name_input])

        if not email:
            email_input = input("Enter your email for Git commits: ").strip()
            if email_input:
                run_command(["git", "config", "--global", "user.email", email_input])

        print("Git identity configured successfully.")
    return name and email


def check_repo_exists(repo_url):
    """Check if a GitHub repository exists."""
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]

    if repo_url.startswith("https://github.com/"):
        parts = repo_url.split("/")
        if len(parts) < 5:
            print(f"Invalid GitHub URL format: {repo_url}")
            return False
        if not parts[3] or not parts[4]:
            print(f"Invalid GitHub URL format (user/repo part missing): {repo_url}")
            return False
        api_url = f"https://api.github.com/repos/{parts[3]}/{parts[4]}"

        try:
            result = run_command(
                ["curl", "-s", "-o", os.devnull, "-w", "%{http_code}", api_url],
                verbose=False,
            )
            return result and result.strip() == "200"
        except Exception as e:
            print(f"Failed to check repo existence with curl: {e}. Assuming it might not exist or curl is unavailable.")
            return False
    else:
        print(f"Repo check currently only supports https://github.com/ URLs. URL: {repo_url}")
        return False


def create_github_repo(repo_name, username=None):
    """Open browser to create a new GitHub repository."""
    if username:
        repo_name = f"{username}/{repo_name}"

    print(f"\nRepository '{repo_name}' doesn't exist on GitHub.")
    print("Opening GitHub to create a new repository...\n")

    if "/" in repo_name:
        repo_name = repo_name.split("/")[-1]

    webbrowser.open(f"https://github.com/new?name={repo_name}")

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
    status = run_command(["git", "status", "--porcelain"], verbose=False)
    if not status:
        print("No changes to commit. Repository is clean.")
        return False

    if not check_git_identity():
        print("Git identity configuration required before committing.")
        return False

    print("Adding all files...")
    run_command(["git", "add", "."])

    print("Committing files...")
    result = run_command(["git", "commit", "-m", "Initial commit"], verbose=False)

    if result:
        print("Files committed successfully.")
        return True
    else:
        print("Commit failed. Please check previous error messages.")
        return False


def git_push(branch="main"):
    """Push changes to GitHub."""
    current_branch_result = run_command(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], verbose=False
    )
    current_branch = current_branch_result.strip() if current_branch_result else None

    if not current_branch:
        print("Could not determine current branch. Aborting push.")
        return

    if current_branch != branch:
        print(f"Switching to {branch} branch...")
        result = run_command(["git", "checkout", branch], verbose=False)

        if result is None:
            print(f"Creating {branch} branch...")
            run_command(["git", "checkout", "-b", branch])

    print(f"Pushing to GitHub ({branch} branch)...")
    run_command(["git", "push", "-u", "origin", branch])


def git_clone(repo_url=None, target_dir=None):
    """Clone the repository."""
    if repo_url is None:
        repo_url = "https://github.com/GBOGEB/DOCX_RTM_Automation.git"

    command_list = ["git", "clone", repo_url]

    if target_dir:
        command_list.append(target_dir)

    print(f"Cloning repository from {repo_url}...")
    run_command(command_list)


def create_project_structure():
    """Create basic project structure if it doesn't exist."""
    directories = [
        "config",
        "input",
        "output",
        "output/outlines",
        "logs",
        "scripts",
        "code",
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    config_path = Path("config/paths.yaml")
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("# Configuration paths\n")
            f.write("input_dir: './input'\n")
            f.write("output_dir: './output'\n")
            f.write("temp_dir: './temp'\n")

    print("Project structure created/verified.")


def git_setup_repo():
    """Set up a complete GitHub repository with proper structure."""
    is_git_repo = Path(".git").exists()
    if not is_git_repo:
        git_init()
    else:
        print("Git repository already initialized.")

    create_project_structure()

    repo_url = "https://github.com/GBOGEB/DOCX_RTM_Automation.git"

    parts = repo_url.split("/")
    username = parts[3]
    repo_name = parts[4].replace(".git", "")

    exists = check_repo_exists(repo_url)
    if not exists:
        create_github_repo(repo_name, username)

    git_setup_remote(repo_url, use_https=True)

    committed = git_first_commit()

    if committed:
        git_push()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Git Helper Script")
    parser.add_argument(
        "action",
        nargs="?",
        help="Git action to perform (status, init, setup_remote, first_commit, push, clone, setup_repo)",
    )
    parser.add_argument("--url", help="Repository URL for clone or remote setup")
    parser.add_argument("--dir", help="Target directory for clone")
    parser.add_argument("--branch", default="main", help="Branch for push operation")
    parser.add_argument("--https", action="store_true", help="Use HTTPS for remote URL (default)")
    parser.add_argument("--ssh", action="store_false", dest="use_https", help="Use SSH for remote URL")

    args = parser.parse_args()

    if not args.action:
        git_status()

    action = args.action.lower()

    if action == "status":
        git_status()
    elif action == "init":
        git_init()
    elif action == "setup_remote":
        git_setup_remote(args.url, args.use_https)
    elif action == "first_commit":
        git_first_commit()
    elif action == "push":
        git_push(args.branch)
    elif action == "clone":
        git_clone(args.url, args.dir)
    elif action == "setup_repo":
        git_setup_repo()
    else:
        print(f"Unknown action: {args.action}")
        parser.print_help()
