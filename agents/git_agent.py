#!/usr/bin/env python3
"""
Git Agent for the RTM Automation system.
Provides git operations like cloning repositories, checking commit history, etc.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import base agent components
from agents.agent_common import BaseAgent, AgentRole, AgentCapability, AgentMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class GitAgent(BaseAgent):
    """
    Agent for interacting with Git repositories.

    This agent provides functionality for:
    - Cloning and pulling repositories
    - Checking repository status
    - Analyzing commit history
    - Working with branches
    """

    def __init__(self, agent_id: str, dmaic_handler=None, output_handler=None):
        """
        Initialize the GitAgent.

        Args:
            agent_id: Unique identifier for this agent
            dmaic_handler: DMAIC handler for accessing project context
            output_handler: Output handler for logging and reporting
        """
        super().__init__()
        self.agent_id = agent_id
        self.role = AgentRole.TOOL
        self.capabilities = [
            AgentCapability.GIT_OPERATIONS,
            AgentCapability.VERSION_CONTROL
        ]
        self.dmaic_handler = dmaic_handler
        self.output_handler = output_handler
        self.status = "initialized"

        if output_handler:
            self.output_handler.log_info(f"GitAgent {agent_id} initialized")
        else:
            logger.info(f"GitAgent {agent_id} initialized without output_handler")

    def process_message(self, message: AgentMessage) -> Dict[str, Any]:
        """
        Process incoming messages directed to this agent.

        Args:
            message: The message to process

        Returns:
            Response dictionary with results
        """
        if message.message_type == "git_clone_request":
            return self._handle_clone_request(message.content)
        elif message.message_type == "git_pull_request":
            return self._handle_pull_request(message.content)
        elif message.message_type == "git_status_request":
            return self._handle_status_request(message.content)
        elif message.message_type == "git_log_request":
            return self._handle_log_request(message.content)
        else:
            return {
                "status": "error",
                "message": f"Unsupported message type: {message.message_type}"
            }

    def _handle_clone_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle git clone requests."""
        repo_url = content.get("repo_url")
        branch = content.get("branch", "main")
        local_path = content.get("local_path", None)

        if not repo_url:
            return {"status": "error", "message": "Repository URL is required"}

        try:
            result = self.clone_repository(repo_url, branch, local_path)
            return {
                "status": "success",
                "message": f"Repository cloned successfully",
                "data": {"local_path": result}
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to clone repository: {e}"}

    def _handle_pull_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle git pull requests."""
        repo_path = content.get("repo_path")
        branch = content.get("branch", "main")

        if not repo_path:
            return {"status": "error", "message": "Repository path is required"}

        try:
            result = self.pull_repository(repo_path, branch)
            return {
                "status": "success",
                "message": "Repository pulled successfully",
                "data": result
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to pull repository: {e}"}

    def _handle_status_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle git status requests."""
        repo_path = content.get("repo_path")

        if not repo_path:
            return {"status": "error", "message": "Repository path is required"}

        try:
            status = self.get_repo_status(repo_path)
            return {
                "status": "success",
                "message": "Repository status retrieved",
                "data": status
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get repository status: {e}"}

    def _handle_log_request(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle git log requests."""
        repo_path = content.get("repo_path")
        count = content.get("count", 10)

        if not repo_path:
            return {"status": "error", "message": "Repository path is required"}

        try:
            commits = self.get_commit_history(repo_path, count)
            return {
                "status": "success",
                "message": f"Retrieved {len(commits)} commits",
                "data": {"commits": commits}
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get commit history: {e}"}

    def clone_repository(self, repo_url: str, branch: str = "main", local_path: Optional[str] = None) -> str:
        """
        Clone a Git repository.

        Args:
            repo_url: URL of the repository to clone
            branch: Branch to clone (default: main)
            local_path: Path where to clone the repository (optional)

        Returns:
            Path to the cloned repository
        """
        # Log the operation
        if self.output_handler:
            self.output_handler.log_info(f"Cloning repository {repo_url} (branch: {branch})")
        else:
            logger.info(f"Cloning repository {repo_url} (branch: {branch})")

        # Determine local path if not provided
        if not local_path:
            # Extract repo name from URL and use it as directory name
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            local_path = os.path.join(project_root, "data", "repos", repo_name)

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Check if repo already exists
        if os.path.exists(os.path.join(local_path, ".git")):
            # Repository exists, pull instead of clone
            if self.output_handler:
                self.output_handler.log_info(f"Repository exists at {local_path}, pulling instead")
            else:
                logger.info(f"Repository exists at {local_path}, pulling instead")
            return self.pull_repository(local_path, branch)

        # Clone the repository
        try:
            cmd = ["git", "clone", "--branch", branch, repo_url, local_path]
            result = subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if self.output_handler:
                self.output_handler.log_info(f"Repository cloned successfully to {local_path}")
            else:
                logger.info(f"Repository cloned successfully to {local_path}")

            return local_path

        except subprocess.CalledProcessError as e:
            error_msg = f"Error cloning repository: {e.stderr}"
            if self.output_handler:
                self.output_handler.log_error(error_msg)
            else:
                logger.error(error_msg)
            raise RuntimeError(error_msg)

    def pull_repository(self, repo_path: str, branch: str = "main") -> Dict[str, Any]:
        """
        Pull updates from a Git repository.

        Args:
            repo_path: Path to the local repository
            branch: Branch to pull (default: main)

        Returns:
            Dictionary with pull results
        """
        if not os.path.exists(os.path.join(repo_path, ".git")):
            error_msg = f"Not a git repository: {repo_path}"
            if self.output_handler:
                self.output_handler.log_error(error_msg)
            else:
                logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)

        try:
            # Make sure we're on the right branch
            subprocess.run(
                ["git", "checkout", branch],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Pull updates
            result = subprocess.run(
                ["git", "pull", "origin", branch],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            return {
                "path": repo_path,
                "branch": branch,
                "output": result.stdout,
                "up_to_date": "Already up to date" in result.stdout
            }

        except subprocess.CalledProcessError as e:
            error_msg = f"Error pulling repository: {e.stderr}"
            if self.output_handler:
                self.output_handler.log_error(error_msg)
            else:
                logger.error(error_msg)
            raise RuntimeError(error_msg)

        finally:
            # Change back to the original directory
            os.chdir(original_dir)

    def get_repo_status(self, repo_path: str) -> Dict[str, Any]:
        """
        Get the status of a Git repository.

        Args:
            repo_path: Path to the local repository

        Returns:
            Dictionary with repository status
        """
        if not os.path.exists(os.path.join(repo_path, ".git")):
            error_msg = f"Not a git repository: {repo_path}"
            if self.output_handler:
                self.output_handler.log_error(error_msg)
            else:
                logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)

        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            current_branch = branch_result.stdout.strip()

            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            status_output = status_result.stdout.strip()

            # Get remote URL
            remote_result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            remote_url = remote_result.stdout.strip()

            # Parse status output
            modified_files = []
            untracked_files = []

            for line in status_output.split("\n"):
                if not line:
                    continue

                status_code = line[:2]
                file_path = line[3:]

                if status_code.startswith("M"):
                    modified_files.append(file_path)
                elif status_code.startswith("??"):
                    untracked_files.append(file_path)

            return {
                "path": repo_path,
                "branch": current_branch,
                "remote_url": remote_url,
                "clean": len(status_output) == 0,
                "modified_files": modified_files,
                "untracked_files": untracked_files,
                "modified_count": len(modified_files),
                "untracked_count": len(untracked_files)
            }

        except subprocess.CalledProcessError as e:
            error_msg = f"Error getting repository status: {e.stderr}"
            if self.output_handler:
                self.output_handler.log_error(error_msg)
            else:
                logger.error(error_msg)
            raise RuntimeError(error_msg)

        finally:
            # Change back to the original directory
            os.chdir(original_dir)

    def get_commit_history(self, repo_path: str, count: int = 10) -> List[Dict[str, str]]:
        """
        Get the commit history of a Git repository.

        Args:
            repo_path: Path to the local repository
            count: Number of commits to retrieve (default: 10)

        Returns:
            List of dictionaries with commit information
        """
        if not os.path.exists(os.path.join(repo_path, ".git")):
            error_msg = f"Not a git repository: {repo_path}"
            if self.output_handler:
                self.output_handler.log_error(error_msg)
            else:
                logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)

        try:
            # Get commit history
            result = subprocess.run(
                [
                    "git", "log",
                    f"-{count}",
                    "--pretty=format:%H|%an|%at|%s"
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) >= 4:
                    commit = {
                        "hash": parts[0],
                        "author": parts[1],
                        "timestamp": parts[2],
                        "message": parts[3]
                    }
                    commits.append(commit)

            return commits

        except subprocess.CalledProcessError as e:
            error_msg = f"Error getting commit history: {e.stderr}"
            if self.output_handler:
                self.output_handler.log_error(error_msg)
            else:
                logger.error(error_msg)
            raise RuntimeError(error_msg)

        finally:
            # Change back to the original directory
            os.chdir(original_dir)
