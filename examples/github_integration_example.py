import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from config.openai_integration import (
    initialize_openai,
    create_agent,
)  # create_agent might be deprecated if using orchestrator
from config.config_loader import get_project_paths
from dmaic import DMAICHandler  # Needed for orchestrator
from utils.output_handler import OutputHandler  # Needed for orchestrator
from agents.agent_orchestrator import AgentOrchestrator
from agents.agent_common import AgentMessage, AgentPriority, AgentCapability

# Load GitHub settings from paths.yaml.fixed
paths_config = get_project_paths()  # Renamed to avoid conflict
if not paths_config:
    print("Error: Failed to load project paths configuration. Exiting.")
    sys.exit(1)
github_config = paths_config.get("github", {})

# GitHub API configuration (some might be used by GitAgent internally or for setup)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = github_config.get("user_name") or os.getenv("GITHUB_USERNAME")
# REPO_NAME will be derived from repo_url or passed directly to agent
REPO_URL = github_config.get("repo_url")
if not REPO_URL and GITHUB_USERNAME and os.getenv("GITHUB_REPO"):
    REPO_URL = f"https://github.com/{GITHUB_USERNAME}/{os.getenv('GITHUB_REPO')}"


def main():
    print("Starting GitHub Integration Example...")

    # --- Sanity Checks ---
    print("\n--- Sanity Checks ---")
    if not os.path.isdir(project_root):
        print(f"Error: Project root directory not found: {project_root}")
        return
    print(f"Project root: {project_root} (Exists)")

    if not GITHUB_TOKEN:
        print(
            "Warning: GITHUB_TOKEN environment variable not set. GitHub operations will likely fail."
        )
    else:
        print("GITHUB_TOKEN: Set")

    if not REPO_URL:
        print(
            "Warning: Repository URL (github.repo_url in paths.yaml or GITHUB_USERNAME/GITHUB_REPO env vars) not configured. Some operations may fail."
        )
    else:
        print(f"Repository URL: {REPO_URL}")

    # Check for OpenAI API Key (for fallback)
    if not os.getenv("OPENAI_API_KEY"):
        print(
            "Warning: OPENAI_API_KEY environment variable not set. Fallback OpenAI calls will fail."
        )
    else:
        print("OPENAI_API_KEY: Set (for fallback)")
    # --- End Sanity Checks ---

    print("\nInitializing DMAIC Handler and Output Handler for Orchestrator...")
    # Initialize necessary components for the orchestrator
    dmaic_handler = DMAICHandler("GitHubIntegrationExampleProject")
    if not dmaic_handler:  # Basic check, DMAICHandler constructor doesn't typically fail unless major issues
        print("Error: Failed to initialize DMAICHandler.")
        return
    print("DMAIC Handler: Initialized.")

    output_handler_path = os.path.join(project_root, "outputs", "github_example_logs")
    try:
        os.makedirs(output_handler_path, exist_ok=True)
        output_handler = OutputHandler(output_handler_path)
        print(f"Output Handler: Initialized (logs at {output_handler_path}).")
    except OSError as e:
        print(
            f"Error: Could not create or access output directory for OutputHandler: {output_handler_path}. {e}"
        )
        return

    print("\nInitializing Agent Orchestrator...")
    orchestrator = AgentOrchestrator(dmaic_handler, output_handler)
    if not orchestrator:  # Basic check
        print("Error: Failed to initialize AgentOrchestrator.")
        return
    print("Agent Orchestrator: Initialized.")

    orchestrator.initialize_standard_agents()  # This should register GitAgent
    print(
        "Standard agents (including GitAgent if available): Initialization attempted."
    )

    git_agent_id = None
    if (
        orchestrator.git_agent
    ):  # Check if git_agent was specifically initialized by initialize_standard_agents
        git_agent_id = orchestrator.git_agent.agent_id
        print(f"GitAgent: Found and registered with ID: {git_agent_id}")
    else:  # Fallback to capability check if direct attribute not reliable
        git_agents_found = orchestrator.find_agent_by_capability(
            AgentCapability.GIT_STATUS_CHECK
        )
        if git_agents_found:
            git_agent_id = git_agents_found[0]
            print(
                f"GitAgent: Found via capability GIT_STATUS_CHECK with ID: {git_agent_id}"
            )
        else:
            print(
                "Warning: GitAgent not found or does not have GIT_STATUS_CHECK capability."
            )

    copilot_agents = orchestrator.find_agent_by_capability(
        AgentCapability.CODE_ANALYSIS
    )
    copilot_agent_id = None
    if not copilot_agents:
        print("Warning: No Copilot agent found with CODE_ANALYSIS capability.")
    else:
        copilot_agent_id = copilot_agents[0]
        print(
            f"CopilotAgent: Found via capability CODE_ANALYSIS with ID: {copilot_agent_id}"
        )

    # Print project and GitHub configuration
    print("\nProject configuratie:")
    print(f"  Repository URL: {REPO_URL or 'Niet geconfigureerd'}")
    print(f"  Branch: {github_config.get('branch', 'main')}")
    print(f"  Gebruiker: {GITHUB_USERNAME or 'Niet geconfigureerd'}")
    print(f"  GitHub integratie ingeschakeld: {github_config.get('enabled', False)}")

    if not GITHUB_TOKEN:
        print(
            "\nWaarschuwing: GITHUB_TOKEN omgevingsvariabele niet ingesteld. GitHub operations will likely fail."
        )

    if not REPO_URL:
        print(
            "Waarschuwing: Repository URL (github.repo_url in paths.yaml) niet geconfigureerd. Kan geen issues of PRs ophalen."
        )
        return

    # Example 1: Issues ophalen via GitAgent
    print("\nGitHub issues ophalen via GitAgent...")
    if (
        git_agent_id and orchestrator.git_agent
    ):  # Check if git_agent was initialized and ID is known
        try:
            print("Fetching issues (conceptual - GitAgent method needs to exist)...")
            print(
                "Issue fetching via agent is a more advanced topic requiring specific GitAgent methods or message handling."
            )
        except Exception as e:
            print(f"Fout bij ophalen issues via GitAgent: {e}")
    else:
        print("GitAgent niet beschikbaar in orchestrator.")

    # Example 2: Code-review simuleren met CopilotAgent
    print("\nCode-review simuleren met CopilotAgent...")
    if copilot_agent_id:
        example_file_path = os.path.abspath(__file__)

        with open(example_file_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        AgentMessage(
            source="github_example_main",
            target=copilot_agent_id,
            message_type="code_analysis_request",  # Assuming CopilotAgent handles this
            content={
                "code_content": code_content,
                "language": "python",
                "file_path": example_file_path,  # Optional: for context
            },
            priority=AgentPriority.MEDIUM,
            requires_response=True,
        )

        print(f"Verzoek om code review naar CopilotAgent ({copilot_agent_id})...")
        print(
            "Code review via CopilotAgent is conceptual here. Response handling needs async/callback or direct method."
        )

        if not copilot_agent_id:  # Or if the above is too complex
            print(
                "Fallback to direct OpenAI call for code review as CopilotAgent interaction is complex for sync example."
            )
            client = initialize_openai()
            if client:
                print("OpenAI client for fallback: Initialized successfully.")
                code_review_agent_direct = create_agent(
                    system_prompt="""Je bent een deskundige code-reviewer.
Analyseer de Python-code en geef constructieve feedback over verbeteringen, bugs of beste praktijken.
Beperk je antwoord tot relevante technische feedback.""",
                    client=client,
                    model="gpt-3.5-turbo",
                )
                prompt = f"Analyseer deze Python-code en geef feedback:\n\n```python\n{code_content}\n```"
                analysis, _ = code_review_agent_direct(prompt)
                print("\nAI Code Review (direct OpenAI):")
                print(analysis)
            else:
                print(
                    "OpenAI client kon niet worden geïnitialiseerd voor fallback review."
                )
    else:
        print("CopilotAgent niet beschikbaar voor code-review.")

    # Example 3: Pull Request Analysis Workflow (Conceptual)
    print("\nSimuleren van Pull Request Analyse Workflow via Orchestrator...")
    if REPO_URL:
        pr_number_example = 1  # Example PR number
        {
            "repository_url": REPO_URL,
            "pr_number": pr_number_example,
            "branch": github_config.get("branch", "main"),  # Or specific PR branch
        }
        print(
            f"Conceptuele workflow 'pull_request_impact_analysis' voor PR #{pr_number_example} in {REPO_URL}."
        )
        print("Implementatie van deze workflow in AgentOrchestrator is vereist.")
    else:
        print(
            "Repository URL niet geconfigureerd, kan PR analyse workflow niet simuleren."
        )

    print(
        "\nDit script demonstreert hoe de Agent Orchestrator kan worden gebruikt voor GitHub workflows."
    )
    print(
        "Voor volledige functionaliteit, stel de GITHUB_TOKEN omgevingsvariabele in en implementeer de nodige agent methoden/berichten."
    )


if __name__ == "__main__":
    main()
