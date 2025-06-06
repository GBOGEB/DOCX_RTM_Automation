# Git Integration & CI/CD Workflows

This document explains the Git integration workflows available in the RTM Automation system and how to test them.

## Available Git Workflows

The system provides several Git workflows through the `GitAgent`:

### 1. Repository Analysis Workflow

```bash
python examples/agent_orchestration_example.py
```

This workflow:
1. Clones/pulls a repository
2. Analyzes its structure
3. Generates a detailed report

### 2. Code Modification & Push Workflow

Currently implemented in `debug_full_pipeline.py` but not exposed as a standalone script.
This workflow:

1. Creates/checks out a feature branch
2. Makes code changes (via Copilot agent)
3. Commits the changes
4. Optionally creates a pull request

## Testing Git Operations

### Manual Testing

```bash
# Run the debug pipeline script and choose option 2
python debug_full_pipeline.py
# Select "2. Git operations only"
```

This will:
- Create a test repository
- Initialize git
- Create sample files
- Perform git add/commit
- Create a branch
- Make additional changes
- Test git status

### Automated Testing

To test the Git integration more comprehensively:

1. Create a dedicated test file:

```python
# test_git_workflows.py
import os
from config.openai_integration import initialize_openai
from dmaic import DMAICHandler
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager
from agents.git_agent import GitAgent

# Initialize components
client = initialize_openai()
paths = PathsManager()
output = OutputHandler(paths.get_output_dir())
dmaic = DMAICHandler("Git Testing", client)

# Create Git agent
git_agent = GitAgent("test_git_agent", dmaic, output)

# Test repository operations
def test_repo_operations():
    # Create test repo
    repo_path = os.path.join(paths.get_output_dir(), "test_repo")
    os.makedirs(repo_path, exist_ok=True)

    # Initialize git
    os.chdir(repo_path)
    os.system("git init .")
    os.system("git config user.name 'Test User'")
    os.system("git config user.email 'test@example.com'")

    # Create a test file
    with open(os.path.join(repo_path, "test.txt"), 'w') as f:
        f.write("Test content\n")

    # Register repo with agent
    git_agent.repositories["test_repo"] = {
        "name": "test_repo",
        "path": repo_path,
        "url": repo_path
    }

    # Test commit
    result = git_agent.create_commit("test_repo", "Initial commit", ["test.txt"])
    print(f"Commit result: {result}")

    # Test branch creation
    os.system("git checkout -b feature/test")

    # Test status
    status = git_agent._git_status(repo_path)
    print(f"Status: {status}")

    # You can't test push/PR without a remote repository

if __name__ == "__main__":
    test_repo_operations()
```

## GitHub API Integration

The system has basic GitHub integration through the `git_agent.py` file:

- `_create_github_pr` method can create pull requests
- `_create_gitlab_mr` method can create merge requests

However, these methods currently return instructions instead of making actual API calls.

### Adding GitHub API Support

To enable full GitHub API integration:

1. Install the GitHub API library:
```bash
pip install PyGithub
```

2. Modify the GitAgent class in `agents/git_agent.py`:

```python
from github import Github

# In the GitAgent class, add a proper GitHub PR creation method:
def _create_github_pr(self, repo_info: Dict[str, Any], title: str,
                    source_branch: str, target_branch: str, description: str) -> Dict[str, Any]:
    """Create a GitHub pull request"""
    try:
        # Get GitHub token from environment or config
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_token:
            return {
                "status": "error",
                "message": "GitHub token not found. Set GITHUB_TOKEN environment variable."
            }

        # Extract owner and repo name from URL
        repo_url = repo_info["url"]
        url_parts = repo_url.rstrip("/").split("/")
        if "github.com" in url_parts:
            idx = url_parts.index("github.com")
            if len(url_parts) >= idx + 3:
                owner = url_parts[idx + 1]
                repo_name = url_parts[idx + 2].replace(".git", "")

                # Create GitHub client
                g = Github(github_token)
                repo = g.get_repo(f"{owner}/{repo_name}")

                # Create the PR
                pr = repo.create_pull(
                    title=title,
                    body=description,
                    head=source_branch,
                    base=target_branch
                )

                return {
                    "status": "success",
                    "platform": "GitHub",
                    "pr_number": pr.number,
                    "pr_url": pr.html_url,
                    "message": f"PR #{pr.number} created successfully"
                }

        return {
            "status": "error",
            "message": "Could not extract owner/repo from URL"
        }
    except Exception as e:
        self.output_handler.log_error(f"GitHub PR creation error: {e}")
        return {
            "status": "error",
            "message": f"Failed to create PR: {str(e)}"
        }
```

## CI/CD Integration

The CI/CD integration is handled through the `DMAICCICDAgent` and `DMAICCICDIntegration` classes.

You can test CI/CD integration by running:

```bash
python examples/dmaic_cicd_example.py
```

This demonstrates:
- Pipeline analysis with DMAIC methodology
- Metrics collection and analysis
- Improvement plans generation
- Control mechanisms setup

## Working with Sub-repositories (Git Submodules)

If your project utilizes Git submodules to include other repositories (e.g., for shared libraries, specific documentation sets):

1. **Cloning with Submodules**:
    When cloning the main repository, use:
    ```bash
    git clone --recurse-submodules <repository_url>
    ```
    Or, if already cloned:
    ```bash
    git submodule update --init --recursive
    ```

2. **Processing Submodule Content**:
    The RTM automation system can be configured to scan for input documents (e.g., Markdown requirements files) within submodules. This typically involves:
    * Configuring `PathsManager` or input file discovery logic to include submodule directories.
    * Ensuring that relative paths within submodules are correctly resolved.

3. **Updating Submodules**:
    To pull the latest changes within submodules:
    ```bash
    git submodule update --remote
    ```
    Changes within submodules should be committed and pushed within the submodule's own repository first, then the main repository updated to point to the new submodule commit.

## Integrating OpenAI for Enhanced Git Operations

OpenAI (or similar LLMs) can be integrated into Git workflows to assist with:

* **Automated Commit Message Generation**: Analyze staged changes and suggest or generate commit messages.
* **Code Review Assistance**: Provide summaries of changes, identify potential issues, or suggest improvements for pull requests.
* **Documentation Generation/Update**: Assist in generating documentation snippets based on code changes.
* **Branch Name Suggestions**: Suggest branch names based on an issue description or initial commit.

This integration typically involves:
* Using agents (like a specialized `GitCopilotAgent`) that interact with OpenAI APIs.
* Securely managing OpenAI API keys (e.g., via environment variables or a secrets management system).
* Crafting effective prompts to get desired outputs from the LLM.

## Advanced GitHub Integration

Beyond basic Git operations and the `_create_github_pr` example, deeper GitHub integration can include:

* **Fetching Specific Files/Data**: Using the GitHub API (e.g., with `PyGithub`) to download specific files, repository contents, issue data, or PR details without cloning the entire repository.
* **Triggering GitHub Actions**: Programmatically triggering GitHub Actions workflows (e.g., after a local RTM generation, trigger a validation workflow on GitHub).
* **Automated Issue Creation**: Creating GitHub issues based on findings from the RTM automation (e.g., traceability gaps).
* **Updating Wiki Pages or Project Boards**: Automating updates to GitHub project wikis or boards based on RTM status.

This requires:
* Using a GitHub Personal Access Token (PAT) with appropriate permissions.
* Utilizing libraries like `PyGithub` for API interactions.

## Markdown Files as Primary Input in Git Workflows

Markdown files are often a primary source for requirements and documentation within this system. In a Git workflow context:

* **Version Control**: Requirements written in Markdown are easily version-controlled with Git, allowing for clear history and diffs.
* **Branching and Merging**: Standard Git branching strategies can be used for managing different versions or features of requirements.
* **Automated Processing**: CI/CD pipelines can automatically trigger RTM generation or validation whenever Markdown files in specific directories are updated on a branch.
* **Input Discovery**: The system should be configured to locate these Markdown files, whether they are in the main repository or within submodules.