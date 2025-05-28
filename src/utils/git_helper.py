#!/usr/bin/env python3
"""
Git helper utilities for the RTM Automation project.
"""
import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class GitHelper:
    """Helper class for Git operations."""

    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize Git helper.

        Args:
            repo_path: Path to Git repository (default: current directory)
        """
        self.repo_path = repo_path or os.getcwd()

    def is_git_repo(self) -> bool:
        """Check if the directory is a Git repository."""
        git_dir = os.path.join(self.repo_path, ".git")
        return os.path.isdir(git_dir)

    def get_status(self, show_untracked: bool = True) -> Dict[str, Any]:
        """
        Get Git repository status.

        Args:
            show_untracked: Whether to show untracked files

        Returns:
            Dictionary with status information
        """
        if not self.is_git_repo():
            return {"error": "Not a Git repository"}

        try:
            # Get current branch
            branch_cmd = ["git", "-C", self.repo_path, "rev-parse", "--abbrev-ref", "HEAD"]
            branch = subprocess.check_output(branch_cmd, text=True).strip()

            # Get status
            status_cmd = ["git", "-C", self.repo_path, "status", "--porcelain"]
            if show_untracked:
                status_cmd.append("-uall")

            status_output = subprocess.check_output(status_cmd, text=True)

            # Parse status
            modified = []
            staged = []
            untracked = []

            for line in status_output.splitlines():
                if not line:
                    continue

                status = line[:2]
                file_path = line[3:]

                if status[0] == "M":
                    staged.append(file_path)
                elif status[1] == "M":
                    modified.append(file_path)
                elif status == "??":
                    untracked.append(file_path)

            return {
                "branch": branch,
                "clean": len(status_output) == 0,
                "staged": staged,
                "modified": modified,
                "untracked": untracked,
                "staged_count": len(staged),
                "modified_count": len(modified),
                "untracked_count": len(untracked)
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"Git command failed: {e.stderr if hasattr(e, 'stderr') else str(e)}"}
        except Exception as e:
            return {"error": f"Error getting Git status: {str(e)}"}

    def commit_changes(self, message: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Commit changes to the repository.

        Args:
            message: Commit message
            files: List of files to commit (None for all)

        Returns:
            Dictionary with commit result
        """
        if not self.is_git_repo():
            return {"error": "Not a Git repository"}

        try:
            # Add files
            add_cmd = ["git", "-C", self.repo_path, "add"]
            if files:
                add_cmd.extend(files)
            else:
                add_cmd.append(".")

            subprocess.check_call(add_cmd)

            # Commit
            commit_cmd = ["git", "-C", self.repo_path, "commit", "-m", message]
            commit_output = subprocess.check_output(commit_cmd, text=True)

            return {
                "status": "success",
                "message": "Changes committed successfully",
                "output": commit_output
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"Git command failed: {e.stderr if hasattr(e, 'stderr') else str(e)}"}
        except Exception as e:
            return {"error": f"Error committing changes: {str(e)}"}

    def push_changes(self, remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Push commits to remote repository.

        Args:
            remote: Remote repository name
            branch: Branch to push (None for current branch)

        Returns:
            Dictionary with push result
        """
        if not self.is_git_repo():
            return {"error": "Not a Git repository"}

        try:
            # Get current branch if not specified
            if not branch:
                branch_cmd = ["git", "-C", self.repo_path, "rev-parse", "--abbrev-ref", "HEAD"]
                branch = subprocess.check_output(branch_cmd, text=True).strip()

            # Push changes
            push_cmd = ["git", "-C", self.repo_path, "push", remote, branch]
            push_output = subprocess.check_output(push_cmd, text=True)

            return {
                "status": "success",
                "message": f"Changes pushed to {remote}/{branch} successfully",
                "output": push_output
            }

        except subprocess.CalledProcessError as e:
            return {"error": f"Git command failed: {e.stderr if hasattr(e, 'stderr') else str(e)}"}
        except Exception as e:
            return {"error": f"Error pushing changes: {str(e)}"}

def main():
    """Command-line interface for GitHelper."""
    import argparse

    parser = argparse.ArgumentParser(description="Git helper utilities")
    parser.add_argument("--repo", help="Repository path")
    parser.add_argument("--status", action="store_true", help="Show repository status")
    parser.add_argument("--commit", help="Commit changes with message")
    parser.add_argument("--push", action="store_true", help="Push changes to remote")
    parser.add_argument("--files", nargs="+", help="Files to commit")

    args = parser.parse_args()

    git_helper = GitHelper(args.repo)

    if args.status:
        status = git_helper.get_status()
        print(f"Branch: {status.get('branch', 'Unknown')}")
        print(f"Clean: {status.get('clean', False)}")
        print(f"Modified files: {len(status.get('modified', []))}")
        print(f"Staged files: {len(status.get('staged', []))}")
        print(f"Untracked files: {len(status.get('untracked', []))}")

    if args.commit:
        result = git_helper.commit_changes(args.commit, args.files)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(result["output"])

    if args.push:
        result = git_helper.push_changes()
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(result["output"])

if __name__ == "__main__":
    main()
