import os
import sys
import subprocess
import re
import json
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum, auto

from dmaic import DMAICHandler
from utils.paths_manager import PathsManager
from utils.output_handler import OutputHandler
from agents.agent_common import BaseAgent, AgentRole, AgentMessage, AgentPriority, StandardAgentResponse, AgentCapability, validate_input

class GitOperation(Enum):
    """Supported Git operations"""
    CLONE = auto()
    PULL = auto()
    PUSH = auto()
    COMMIT = auto()
    BRANCH = auto()
    CHECKOUT = auto()
    STATUS = auto()
    CREATE_PR = auto()
    MERGE = auto()

class GitAgent(BaseAgent):
    """
    Agent responsible for Git repository operations including
    cloning, pushing, creating PRs, and analyzing repository content.
    """

    def __init__(self, agent_id: str, dmaic_handler: DMAICHandler, output_handler: OutputHandler):
        """Initialize the Git agent"""
        super().__init__(agent_id, AgentRole.REPOSITORY, output_handler)
        self.dmaic_handler = dmaic_handler
        self.paths = PathsManager()

        # Directory for storing repositories
        self.repos_dir = os.path.join(self.paths.get_data_dir(), "repositories")
        os.makedirs(self.repos_dir, exist_ok=True)

        # Track repositories
        self.repositories: Dict[str, Dict[str, Any]] = {}

        # Register capabilities
        self.register_capability(AgentCapability.GIT_CLONE)
        self.register_capability(AgentCapability.GIT_PULL)
        self.register_capability(AgentCapability.GIT_PUSH)
        self.register_capability(AgentCapability.GIT_COMMIT)
        self.register_capability(AgentCapability.GIT_PR_CREATE)
        self.register_capability(AgentCapability.REPO_ANALYSIS)
        self.register_capability(AgentCapability.GIT_STATUS_CHECK)

        # Register message handlers
        self.register_message_handler("git_operation", self.handle_git_operation)
        self.register_message_handler("repository_query", self.handle_repository_query)

    def handle_git_operation(self, message: AgentMessage) -> StandardAgentResponse:
        """Handle Git operation requests from other agents"""
        content = message.content

        if not validate_input(content, ["operation"]):
            return {"status": "error", "message": "Operation not specified in content.", "data": None, "error_details": "Missing 'operation'", "markdown_content": None}

        operation_str = content["operation"]
        response_data: Dict[str, Any] = {}
        error_occurred = False
        error_message = ""

        try:
            if operation_str == "clone":
                if not validate_input(content, ["url"]):
                    return {"status": "error", "message": "Missing 'url' for clone operation.", "data": None, "error_details": "Invalid input", "markdown_content": None}
                response_data = self._handle_clone_operation(content)
            elif operation_str == "pull":
                if not validate_input(content, ["repository"]):
                    return {"status": "error", "message": "Missing 'repository' for pull operation.", "data": None, "error_details": "Invalid input", "markdown_content": None}
                response_data = self._handle_pull_operation(content)
            elif operation_str == "push":
                if not validate_input(content, ["repository"]):
                    return {"status": "error", "message": "Missing 'repository' for push operation.", "data": None, "error_details": "Invalid input", "markdown_content": None}
                response_data = self._handle_push_operation(content)
            elif operation_str == "commit":
                if not validate_input(content, ["repository", "message"]):
                    return {"status": "error", "message": "Missing 'repository' or 'message' for commit operation.", "data": None, "error_details": "Invalid input", "markdown_content": None}
                response_data = self._handle_commit_operation(content)
            elif operation_str == "create_pr":
                if not validate_input(content, ["repository", "title", "source_branch"]):
                    return {"status": "error", "message": "Missing 'repository', 'title', or 'source_branch' for create_pr.", "data": None, "error_details": "Invalid input", "markdown_content": None}
                response_data = self._handle_create_pr_operation(content)
            elif operation_str == "status":
                if not validate_input(content, ["repository"]):
                    return {"status": "error", "message": "Missing 'repository' for status operation.", "data": None, "error_details": "Invalid input", "markdown_content": None}
                response_data = self._handle_status_operation(content)
            else:
                error_occurred = True
                error_message = f"Unsupported operation: {operation_str}"
        except Exception as e:
            self.output_handler.log_error(f"Error in Git operation {operation_str}: {e}")
            error_occurred = True
            error_message = str(e)

        if error_occurred or response_data.get("status") == "error":
            return {
                "status": "error",
                "message": f"Git operation '{operation_str}' failed.",
                "data": {"operation": operation_str, **response_data.get("data", {})},
                "error_details": error_message or response_data.get("error"),
                "markdown_content": None
            }
        else:
            return {
                "status": "success",
                "message": f"Git operation '{operation_str}' completed successfully.",
                "data": response_data,
                "error_details": None,
                "markdown_content": None
            }

    def handle_repository_query(self, message: AgentMessage) -> StandardAgentResponse:
        """Handle repository information queries from other agents"""
        content = message.content

        if not validate_input(content, ["query_type", "repository"]):
            return {"status": "error", "message": "Missing 'query_type' or 'repository' in content.", "data": None, "error_details": "Invalid input", "markdown_content": None}

        query_type = content.get("query_type")
        repo_name = content.get("repository")

        if not repo_name or repo_name not in self.repositories:
            return {"status": "error", "message": f"Unknown repository: {repo_name}", "data": None, "error_details": "Repository not found", "markdown_content": None}

        repo_info = self.repositories[repo_name]
        query_response_data: Dict[str, Any] = {}
        error_occurred = False
        error_message = ""

        try:
            if query_type == "structure":
                query_response_data = self._get_repository_structure(repo_info)
            elif query_type == "files":
                query_response_data = self._get_repository_files(repo_info, content.get("path", ""))
            elif query_type == "commits":
                query_response_data = self._get_repository_commits(repo_info, content.get("count", 10))
            elif query_type == "branches":
                query_response_data = self._get_repository_branches(repo_info)
            else:
                error_occurred = True
                error_message = f"Unsupported query type: {query_type}"
        except Exception as e:
            self.output_handler.log_error(f"Error in repository query {query_type}: {e}")
            error_occurred = True
            error_message = str(e)

        if error_occurred or query_response_data.get("status") == "error":
            return {
                "status": "error",
                "message": f"Repository query '{query_type}' failed for {repo_name}.",
                "data": {"query_type": query_type, "repository": repo_name, **query_response_data.get("data", {})},
                "error_details": error_message or query_response_data.get("error"),
                "markdown_content": None
            }
        else:
            return {
                "status": "success",
                "message": f"Repository query '{query_type}' for {repo_name} completed.",
                "data": query_response_data,
                "error_details": None,
                "markdown_content": None
            }

    def _handle_clone_operation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle clone operation, returns data for StandardAgentResponse or raises error."""
        repo_url = content["url"]
        branch = content.get("branch", "main")
        repo_path = self.clone_or_pull_repository(repo_url, branch)
        repo_name = self._extract_repo_name(repo_url)
        return {
            "operation": "clone",
            "repository": repo_name,
            "path": repo_path,
            "branch": self._get_current_branch(repo_path)
        }

    def _handle_pull_operation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull operation, returns data for StandardAgentResponse or raises error."""
        repo_name = content["repository"]
        branch = content.get("branch")
        repo_path = self.repositories[repo_name]["path"]
        output = self._git_pull(repo_path, branch)
        return {
            "operation": "pull",
            "repository": repo_name,
            "output": output
        }

    def _handle_push_operation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle push operation, returns data for StandardAgentResponse or raises error."""
        repo_name = content["repository"]
        branch = content.get("branch")
        repo_path = self.repositories[repo_name]["path"]
        output = self._git_push(repo_path, branch)
        return {
            "operation": "push",
            "repository": repo_name,
            "output": output
        }

    def _handle_commit_operation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle commit operation, returns data for StandardAgentResponse or raises error."""
        repo_name = content["repository"]
        message = content["message"]
        files = content.get("files")
        result = self.create_commit(repo_name, message, files)
        return {
            "operation": "commit",
            "repository": repo_name,
            "commit_hash": result.get("commit_hash"),
            "message": message
        }

    def _handle_create_pr_operation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create PR operation, returns data for StandardAgentResponse or raises error."""
        repo_name = content["repository"]
        title = content["title"]
        source_branch = content["source_branch"]
        target_branch = content.get("target_branch", "main")
        description = content.get("description", "")
        return self.create_pull_request(
            repo_name, title, source_branch, target_branch, description
        )

    def _handle_status_operation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status operation, returns data for StandardAgentResponse or raises error."""
        repo_name = content["repository"]
        repo_path = self.repositories[repo_name]["path"]
        status_output = self._git_status(repo_path)
        current_branch = self._get_current_branch(repo_path)
        return {
            "operation": "status",
            "repository": repo_name,
            "current_branch": current_branch,
            "git_status": status_output
        }

    def _get_repository_structure(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get the structure of a repository. Returns data payload."""
        repo_path = repo_info["path"]
        structure = {}
        try:
            for item in os.listdir(repo_path):
                item_path = os.path.join(repo_path, item)
                if os.path.isdir(item_path):
                    structure[item] = "directory"
                else:
                    structure[item] = "file"
            return {"repository": repo_info["name"], "structure": structure, "message": "Basic structure retrieved."}
        except Exception as e:
            self.output_handler.log_error(f"Error getting repo structure for {repo_info['name']}: {e}")
            raise

    def _get_repository_files(self, repo_info: Dict[str, Any], path_filter: str) -> Dict[str, Any]:
        """Get the files in a specific path of the repository. Returns data payload."""
        repo_path = repo_info["path"]
        target_path = os.path.join(repo_path, path_filter) if path_filter else repo_path

        if not os.path.exists(target_path) or not os.path.isdir(target_path):
            raise ValueError(f"Target path does not exist or is not a directory: {target_path}")

        files_list = []
        try:
            for item in os.listdir(target_path):
                if os.path.isfile(os.path.join(target_path, item)):
                    files_list.append(item)
            return {"repository": repo_info["name"], "path": path_filter, "files": files_list}
        except Exception as e:
            self.output_handler.log_error(f"Error listing files for {repo_info['name']} at {path_filter}: {e}")
            raise

    def _get_repository_commits(self, repo_info: Dict[str, Any], count: int) -> Dict[str, Any]:
        """Get the commit history of the repository. Returns data payload."""
        repo_path = repo_info["path"]
        return {
            "repository": repo_info["name"],
            "commits": self._analyze_commit_history(repo_path, count)
        }

    def _get_repository_branches(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get the branches of the repository. Returns data payload."""
        repo_path = repo_info["path"]
        return {
            "repository": repo_info["name"],
            "branches": self._get_branches(repo_path),
            "current_branch": self._get_current_branch(repo_path)
        }
