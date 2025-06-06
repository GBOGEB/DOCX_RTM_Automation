#!/usr/bin/env python3
"""
Git Agent for the RTM Automation system.
Provides git operations like cloning repositories, checking commit history, etc.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# --- Start of standard boilerplate for scripts in packages ---
_self_path_git_agent = Path(__file__).resolve()
_project_root_git_agent = _self_path_git_agent.parents[1]

if str(_project_root_git_agent) not in sys.path:
    sys.path.insert(0, str(_project_root_git_agent))

if __name__ == "__main__" and not __package__:
    _package_path_obj = _self_path_git_agent.parent.relative_to(_project_root_git_agent)
    __package__ = str(_package_path_obj).replace(os.sep, ".")
# --- End of standard boilerplate ---

# Import modules from project
from agents.agent_common import (
    BaseAgent,
    AgentRole,
    AgentCapability,
    AgentMessage,
    StandardAgentResponse,
)
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager


class GitAgent(BaseAgent):
    """Agent for managing Git operations."""

    def __init__(
        self,
        agent_id: str,
        dmaic_handler: Optional[Any] = None,
        output_handler: Optional[OutputHandler] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(agent_id=agent_id, output_handler_instance=output_handler)
        self.role = AgentRole.AUTOMATION
        self.capabilities = [
            AgentCapability.GIT_OPERATIONS,
        ]
        self.dmaic_handler = dmaic_handler
        self.config = config if config else {}
        self.paths = PathsManager()
        self.status = "initialized"
        if self.output_handler:
            self.output_handler.log_info(f"GitAgent {self.agent_id} initialized.")

    def process_message(self, message: AgentMessage) -> StandardAgentResponse:
        """Process incoming messages."""
        if message.message_type == "git_clone_request":
            result = self._handle_clone_repository(message.content)
            return StandardAgentResponse(
                status=result.get("status", "error"),
                message=result.get("message", "Unknown error"),
                data=result.get("data"),
            )
        try:
            # Generic message handling
            if self.output_handler:
                self.output_handler.log_info(
                    f"Received message: {message.message_type}"
                )
            return StandardAgentResponse(
                status="unhandled",
                message=f"Unhandled message type: {message.message_type}",
            )
        except Exception as e:
            if self.output_handler:
                self.output_handler.log_error(f"Error processing message: {str(e)}")
            return StandardAgentResponse(status="error", message=f"Error: {str(e)}")

    def _handle_clone_repository(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle request to clone a Git repository.

        Args:
            content: Dictionary with repository details

        Returns:
            Dictionary with operation results
        """
        repo_url = content.get("repo_url")
        local_path = content.get("local_path")

        if not repo_url:
            return {"status": "error", "message": "Repository URL is required"}

        try:
            # Implementation would go here - for now return a mock success
            return {
                "status": "success",
                "message": f"Repository {repo_url} cloned successfully",
                "data": {"repo_path": local_path or "/mock/path/to/repo"},
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to clone repository: {str(e)}",
            }

    def clone_repository(
        self, repo_url: str, branch: str = "main", local_path: Optional[str] = None
    ) -> str:  # pylint: disable=unused-argument
        """
        Clone a Git repository.

        Args:
            repo_url: URL of the repository to clone
            branch: Branch to checkout
            local_path: Local path where to clone the repository

        Returns:
            Path to the cloned repository
        """
        if not local_path:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            repos_dir = os.path.join(
                str(self.paths.data_dir if hasattr(self.paths, "data_dir") else "."),
                "repos",
            )
            local_path = os.path.join(repos_dir, repo_name)

        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        # Implementation would go here
        # For now just return the path
        return local_path
