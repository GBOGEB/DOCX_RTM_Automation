#!/usr/bin/env python3
"""
GitHub Integration Module for RTM Automation
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """Handles GitHub repository operations."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize with GitHub configuration."""
        self.config = config
        self.github_config = config.get("github", {})
        self.errors = []
        self.warnings = []

        # Check if GitHub integration is enabled
        self.enabled = self.github_config.get("enabled", False)
        if not self.enabled:
            logger.info("GitHub integration is disabled in configuration")
            return

        # Extract GitHub settings
        self.repo_url = self.github_config.get("repo_url", "")
        self.branch = self.github_config.get("branch", "main")
        self.local_path = self.github_config.get("local_path", "")
        self.user_name = self.github_config.get("user_name", "")
        self.user_email = self.github_config.get("user_email", "")
        self.commit_message = self.github_config.get(
            "commit_message", "Update from RTM automation"
        )

        # Validate configuration
        if not self.repo_url:
            self.errors.append("GitHub repository URL is not configured")
        if not self.local_path:
            self.local_path = str(Path("github_repo").resolve())
            self.warnings.append(f"Local path not configured, using: {self.local_path}")

    def check_git_installation(self) -> bool:
        """Check if git is installed and available."""
        try:
            subprocess.run(
                ["git", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            self.errors.append("Git is not installed or not available in PATH")
            return False

    def clone_repository(self) -> bool:
        """Clone the GitHub repository to the local path."""
        if not self.enabled:
            logger.info("GitHub integration is disabled, skipping clone")
            return False

        if not self.check_git_installation():
            return False

        # Create local directory if it doesn't exist
        local_dir = Path(self.local_path)
        if local_dir.exists() and (local_dir / ".git").exists():
            logger.info(
                f"Repository already exists at {self.local_path}, pulling latest changes instead"
            )
            return self.pull_repository()

        # Create parent directory if needed
        os.makedirs(
            (
                os.path.dirname(self.local_path)
                if os.path.dirname(self.local_path)
                else "."
            ),
            exist_ok=True,
        )

        # Clone the repository
        logger.info(f"Cloning repository {self.repo_url} to {self.local_path}")
        try:
            result = subprocess.run(
                ["git", "clone", self.repo_url, self.local_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            logger.debug(f"Git clone output: {result.stdout}")
            return True
        except subprocess.SubprocessError as e:
            self.errors.append(f"Failed to clone repository: {str(e)}")
            logger.error(f"Git clone error: {e}")
            return False

    def pull_repository(self) -> bool:
        """Pull latest changes from the repository."""
        if not self.enabled:
            return False

        if not self.check_git_installation():
            return False

        # Check if local path exists and is a git repository
        local_dir = Path(self.local_path)
        if not local_dir.exists() or not (local_dir / ".git").exists():
            logger.warning(
                f"{self.local_path} is not a git repository, cloning instead"
            )
            return self.clone_repository()

        # Pull latest changes
        logger.info(f"Pulling latest changes from {self.repo_url}")
        try:
            # Change to repository directory
            current_dir = os.getcwd()
            os.chdir(self.local_path)

            # Pull changes
            result = subprocess.run(
                ["git", "pull"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Return to original directory
            os.chdir(current_dir)

            logger.debug(f"Git pull output: {result.stdout}")
            return True
        except subprocess.SubprocessError as e:
            self.errors.append(f"Failed to pull repository: {str(e)}")
            logger.error(f"Git pull error: {e}")

            # Return to original directory in case of error
            if os.getcwd() != current_dir:
                os.chdir(current_dir)

            return False

    def commit_and_push_changes(
        self, files: List[str], message: Optional[str] = None
    ) -> bool:
        """Commit and push changes to the repository."""
        if not self.enabled:
            logger.info("GitHub integration is disabled, skipping commit and push")
            return False

        if not self.check_git_installation():
            return False

        # Check if local path exists and is a git repository
        local_dir = Path(self.local_path)
        if not local_dir.exists() or not (local_dir / ".git").exists():
            logger.warning(f"{self.local_path} is not a git repository, cloning first")
            if not self.clone_repository():
                return False

        # Use provided message or default
        commit_message = message or self.commit_message

        try:
            # Change to repository directory
            current_dir = os.getcwd()
            os.chdir(self.local_path)

            # Configure git user if provided
            if self.user_name:
                subprocess.run(
                    ["git", "config", "user.name", self.user_name], check=True
                )
            if self.user_email:
                subprocess.run(
                    ["git", "config", "user.email", self.user_email], check=True
                )

            # Add files
            for file in files:
                file_path = Path(file)
                # If absolute path, get relative to repo
                if file_path.is_absolute():
                    try:
                        rel_path = file_path.relative_to(local_dir)
                        file = str(rel_path)
                    except ValueError:
                        # File is not within repo, copy it
                        from shutil import copy2

                        dest = local_dir / file_path.name
                        copy2(file_path, dest)
                        file = file_path.name

                subprocess.run(["git", "add", file], check=True)

            # Commit changes
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Check if commit was created (non-zero exit could mean "nothing to commit")
            if (
                commit_result.returncode != 0
                and "nothing to commit" not in commit_result.stderr
            ):
                self.warnings.append(f"Git commit warning: {commit_result.stderr}")

            # Push changes
            push_result = subprocess.run(
                ["git", "push", "origin", self.branch],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            logger.info(f"Successfully pushed changes to {self.repo_url}")

            # Return to original directory
            os.chdir(current_dir)
            return True

        except subprocess.SubprocessError as e:
            self.errors.append(f"Failed to commit and push changes: {str(e)}")
            logger.error(f"Git commit/push error: {e}")

            # Return to original directory in case of error
            if os.getcwd() != current_dir:
                os.chdir(current_dir)

            return False


def debug_github_integration(config: Dict[str, Any]) -> int:
    """
    Debug GitHub integration setup.

    Args:
        config: Configuration dictionary with GitHub settings

    Returns:
        Exit code (0 on success)
    """
    print("\nDebugging GitHub Integration")
    print("==========================")

    # Initialize GitHub integration
    github = GitHubIntegration(config)

    # Check if GitHub integration is enabled
    if not github.enabled:
        print("GitHub integration is disabled in configuration.")
        print(
            "To enable, set 'enabled: true' in the github section of your configuration."
        )
        return 0

    # Check git installation
    print("\nChecking git installation...")
    if github.check_git_installation():
        print("✓ Git is installed and available")
    else:
        print("✗ Git is not installed or not available in PATH")
        return 1

    # Print configuration
    print("\nGitHub Configuration:")
    print(f"- Repository URL: {github.repo_url}")
    print(f"- Branch: {github.branch}")
    print(f"- Local Path: {github.local_path}")
    print(f"- User Name: {github.user_name}")
    print(f"- User Email: {github.user_email}")

    # Check repository connection
    print("\nTesting repository connection...")
    if github.clone_repository():
        print("✓ Successfully connected to repository")
        return 0
    else:
        print("✗ Failed to connect to repository")
        if github.errors:
            for error in github.errors:
                print(f"  - Error: {error}")
        return 1


# For testing directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Simple test configuration
    test_config = {
        "github": {
            "enabled": True,
            "repo_url": "https://github.com/username/test-repo.git",
            "branch": "main",
            "local_path": "test_repo",
            "user_name": "Test User",
            "user_email": "test@example.com",
        }
    }

    result = debug_github_integration(test_config)
    sys.exit(result)
