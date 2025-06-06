#!/usr/bin/env python3
"""
Repository Cloner for DOCX RTM Automation

This utility helps clone and manage external Git repositories needed by the project.
It supports both initial cloning and updating existing repositories.
"""

import os
import subprocess
import json
from pathlib import Path

# ANSI colors for terminal output


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


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
            ["git", "--version"], capture_output=True, text=True, check=False
        )

        if result.returncode == 0:
            return True, result.stdout.strip()
        return (
            False,
            (
                result.stderr.strip()
                if result.stderr
                else "Git command failed without specific error."
            ),
        )
    except FileNotFoundError:
        return (
            False,
            "Git executable not found in PATH. Please ensure Git is installed and in your system's PATH.",
        )
    except Exception as e:
        return False, f"An unexpected error occurred while checking Git version: {e}"


def get_repo_list():
    """Get list of repositories to clone from config or use defaults"""
    config_dir = Path("config")
    repos_file = config_dir / "repositories.json"

    # Create default repositories list if file doesn't exist
    if not repos_file.exists():
        default_repos_data = {
            "repositories": [
                {
                    "name": "DOCX_RTM_Automation",
                    "url": "https://github.com/GBOGEB/DOCX_RTM_Automation.git",
                    "branch": "main",
                    "target_dir": "external/DOCX_RTM_Automation",
                    "description": "Main RTM automation repository",
                },
                {
                    "name": "pandoc-word-reader",
                    "url": "https://github.com/pandoc/pandoc-word-reader.git",
                    "branch": "main",
                    "target_dir": "external/pandoc-word-reader",
                    "description": "Pandoc Word reader extension",
                },
                {
                    "name": "example-openai-utils",
                    "url": "https://github.com/example_user/example-openai-utils.git",
                    "branch": "main",
                    "target_dir": "external/example-openai-utils",
                    "description": "Example utility repository for OpenAI integrations (replace with actual)",
                },
                {
                    "name": "example-markdown-tools",
                    "url": "https://github.com/example_user/example-markdown-tools.git",
                    "branch": "main",
                    "target_dir": "external/example-markdown-tools",
                    "description": "Example repository for Markdown processing tools (replace with actual)",
                },
            ]
        }

        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)

        # Save default repositories file
        try:
            with open(repos_file, "w", encoding="utf-8") as f:
                json.dump(default_repos_data, f, indent=2)
            print_status("INFO", f"Created default repositories file: {repos_file}")
            return default_repos_data["repositories"]
        except IOError as e:
            print_status(
                "ERROR", f"Failed to write default repositories file {repos_file}: {e}"
            )
            return []

    # Load existing repositories file
    try:
        with open(repos_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("repositories", [])
    except json.JSONDecodeError as e:
        print_status("ERROR", f"Invalid JSON in {repos_file}: {e}")
        return []
    except IOError as e:
        print_status("ERROR", f"Failed to load repositories file {repos_file}: {e}")
        return []
    except Exception as e:
        print_status(
            "ERROR", f"An unexpected error occurred while loading {repos_file}: {e}"
        )
        return []


def clone_repository(repo_info, update=True):
    """Clone or update a Git repository"""
    url = repo_info.get("url")
    branch = repo_info.get("branch", "main")
    target_dir_str = repo_info.get("target_dir")
    name = repo_info.get("name", url.split("/")[-1].replace(".git", ""))

    if not all([url, target_dir_str]):
        print_status(
            "ERROR",
            "Repository info is missing URL or target_dir.",
            f"Details: {repo_info}",
        )
        return False

    target_dir = Path(target_dir_str)

    print_header(f"Processing repository: {name}")
    print(f"  URL: {url}")
    print(f"  Branch: {branch}")
    print(f"  Target directory: {target_dir}")

    # Check if directory already exists
    if target_dir.exists():
        print_status("INFO", f"Directory already exists: {target_dir}")

        # Check if it's a git repository
        if not (target_dir / ".git").is_dir():
            print_status(
                "ERROR", f"Directory exists but is not a Git repository: {target_dir}"
            )
            return False

        # Update existing repository if requested
        if update:
            print_status("INFO", "Updating existing repository...")
            original_cwd = Path.cwd()
            try:
                os.chdir(target_dir)

                # Fetch all branches
                fetch_result = subprocess.run(
                    ["git", "fetch", "--all", "--prune"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if fetch_result.returncode != 0:
                    print_status(
                        "WARNING",
                        "Failed to fetch updates.",
                        fetch_result.stderr.strip(),
                    )

                # Check current branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                current_branch = (
                    branch_result.stdout.strip()
                    if branch_result.returncode == 0
                    else ""
                )

                # Checkout specified branch if different or no current branch
                if current_branch != branch:
                    print_status(
                        "INFO",
                        f"Switching from branch '{current_branch or 'detached HEAD'}' to '{branch}'",
                    )
                    checkout_result = subprocess.run(
                        ["git", "checkout", branch],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if checkout_result.returncode != 0:
                        print_status(
                            "WARNING",
                            f"Failed to switch branch to '{branch}'.",
                            checkout_result.stderr.strip(),
                        )

                # Pull latest changes
                pull_result = subprocess.run(
                    ["git", "pull", "origin", branch],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if pull_result.returncode == 0:
                    print_status("SUCCESS", "Repository updated successfully.")
                    if (
                        pull_result.stdout.strip()
                        and pull_result.stdout.strip() != "Already up to date."
                    ):
                        print(f"       Changes: {pull_result.stdout.strip()}")
                    return True
                print_status(
                    "WARNING",
                    f"Failed to pull changes for branch '{branch}'.",
                    pull_result.stderr.strip(),
                )
                return False
            except Exception as e:
                print_status(
                    "ERROR",
                    f"An unexpected error occurred during repository update: {e}",
                )
                return False
            finally:
                os.chdir(original_cwd)
        else:
            print_status("INFO", "Repository exists and update is disabled.")
