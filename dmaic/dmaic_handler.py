import os
import sys
from enum import Enum
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from config.openai_integration import create_agent, initialize_openai


class DMAICPhase(Enum):
    DEFINE = "define"
    MEASURE = "measure"
    ANALYZE = "analyze"
    IMPROVE = "improve"
    CONTROL = "control"


class DMAICHandler:
    """Handler for the DMAIC (Define, Measure, Analyze, Improve, Control) process."""

    def __init__(self, project_name, client=None):
        """Initialize the DMAIC handler with OpenAI integration.

        Args:
            project_name: Name of the project for this DMAIC process
            client: Optional pre-initialized OpenAI client
        """
        self.project_name = project_name
        self.client = client if client else initialize_openai()

        self.agent_system_prompts = {
            DMAICPhase.DEFINE: """You are a Define phase specialist in the DMAIC methodology.
Help the user clearly define their problem statement, identify stakeholders,
and establish project objectives. Focus on clarifying the scope and goals.
Use the CTQ (Critical to Quality) framework when appropriate.
Always ask for specific, measurable outcomes.""",
            DMAICPhase.MEASURE: """You are a Measure phase specialist in the DMAIC methodology.
Help the user identify key metrics, establish data collection methods,
and validate measurement systems. Focus on baseline performance and data integrity.
Ask for specific data points and suggest appropriate statistical tools.""",
            DMAICPhase.ANALYZE: """You are an Analyze phase specialist in the DMAIC methodology.
Help the user analyze collected data to identify root causes of problems.
Suggest appropriate analytical tools such as Pareto charts, fishbone diagrams,
or regression analysis. Focus on data-driven insights and hypothesis testing.""",
            DMAICPhase.IMPROVE: """You are an Improve phase specialist in the DMAIC methodology.
Help the user develop and select optimal solutions based on the analysis.
Focus on creative problem-solving, risk assessment, and implementation planning.
Prioritize solutions based on impact, effort, and feasibility.""",
            DMAICPhase.CONTROL: """You are a Control phase specialist in the DMAIC methodology.
Help the user establish control mechanisms to sustain improvements.
Focus on standardization, documentation, monitoring systems, and response plans.
Ensure long-term sustainability of the implemented solutions.""",
        }

        self.project_data = {
            "name": project_name,
            "created_at": datetime.now().isoformat(),
            "phases": {},
            "current_phase": None,
        }
        self.agents = {}
        self._initialize_agents()

    def _initialize_agents(self):
        """Create specialized agents for each DMAIC phase."""
        if not self.client:
            print("Error: OpenAI client not initialized.")
            return

        common_model = "gpt-3.5-turbo"  # Common model for all agents

        for phase, system_prompt_text in self.agent_system_prompts.items():
            self.agents[phase] = create_agent(
                system_prompt=system_prompt_text, client=self.client, model=common_model
            )

    def start_phase(self, phase: DMAICPhase):
        """Start a specific DMAIC phase.

        Args:
            phase: The DMAIC phase to start

        Returns:
            Initial guidance for the selected phase
        """
        if not isinstance(phase, DMAICPhase):
            raise ValueError(
                f"Phase must be a DMAICPhase enum value, got {type(phase)}"
            )

        self.project_data["current_phase"] = phase.value

        if phase.value not in self.project_data["phases"]:
            self.project_data["phases"][phase.value] = {
                "started_at": datetime.now().isoformat(),
                "conversation": [],
                "outputs": {},
                "completed": False,
            }

        phase_messages = {
            DMAICPhase.DEFINE: "Starting Define phase. Let's clarify the problem statement, project goals, and scope.",
            DMAICPhase.MEASURE: "Starting Measure phase. Let's identify key metrics and collect baseline data.",
            DMAICPhase.ANALYZE: "Starting Analyze phase. Let's identify root causes using data analysis.",
            DMAICPhase.IMPROVE: "Starting Improve phase. Let's develop and implement solutions.",
            DMAICPhase.CONTROL: "Starting Control phase. Let's create systems to sustain improvements.",
        }

        return phase_messages.get(phase, "Starting new phase")

    def interact(self, user_input):
        """Interact with the current phase agent.

        Args:
            user_input: User's query or input

        Returns:
            Agent's response
        """
        current_phase = self.project_data.get("current_phase")
        if not current_phase:
            return "No active phase. Please start a phase using start_phase() first."

        phase_enum = DMAICPhase(current_phase)
        agent = self.agents.get(phase_enum)
        if not agent:
            return f"No agent available for {current_phase} phase."

        # Get conversation history for this phase
        conversation_history = self.project_data["phases"][current_phase][
            "conversation"
        ]

        # Interact with the agent
        response, updated_history = agent(user_input, conversation_history)

        # Update the conversation history
        self.project_data["phases"][current_phase]["conversation"] = updated_history

        return response

    def complete_phase(self, outputs=None):
        """Mark the current phase as complete and store outputs.

        Args:
            outputs: Dictionary of phase outputs/deliverables

        Returns:
            Summary of the completed phase
        """
        current_phase = self.project_data.get("current_phase")
        if not current_phase:
            return "No active phase to complete."

        self.project_data["phases"][current_phase]["completed"] = True
        self.project_data["phases"][current_phase][
            "completed_at"
        ] = datetime.now().isoformat()

        if outputs:
            self.project_data["phases"][current_phase]["outputs"] = outputs

        return f"{current_phase.capitalize()} phase completed."

    def save_project(self, filepath=None):
        """Save the project data to a JSON file.

        Args:
            filepath: Optional filepath for the JSON file

        Returns:
            Path to the saved file
        """
        if filepath is None:
            filename = (
                f"{self.project_name.replace(' ', '_').lower()}_dmaic_project.json"
            )
            filepath = os.path.join(project_root, "outputs", filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.project_data, f, indent=2)

        return filepath

    def load_project(self, filepath):
        """Load a project from a JSON file.

        Args:
            filepath: Path to the project JSON file

        Returns:
            Success message
        """
        with open(filepath, "r", encoding="utf-8") as f:
            self.project_data = json.load(f)

        self.project_name = self.project_data.get("name", "Loaded Project")

        return f"Project '{self.project_name}' loaded successfully."

    def get_phase_summary(self, phase=None):
        """Get a summary of a specific phase or the current phase.

        Args:
            phase: Optional specific phase to summarize

        Returns:
            Summary of the phase
        """
        if phase is None:
            phase = self.project_data.get("current_phase")
            if not phase:
                return "No active phase to summarize."
        elif isinstance(phase, DMAICPhase):
            phase = phase.value

        if phase not in self.project_data["phases"]:
            return f"Phase {phase} not started yet."

        phase_data = self.project_data["phases"][phase]

        summary = f"--- {phase.upper()} PHASE SUMMARY ---\n"
        summary += f"Status: {'Completed' if phase_data.get('completed', False) else 'In Progress'}\n"
        summary += f"Started: {phase_data.get('started_at', 'Unknown')}\n"

        if phase_data.get("completed", False):
            summary += f"Completed: {phase_data.get('completed_at', 'Unknown')}\n"

        conversation_count = len(phase_data.get("conversation", []))
        summary += f"Conversation exchanges: {conversation_count}\n"

        outputs = phase_data.get("outputs", {})
        if outputs:
            summary += "Outputs:\n"
            for key, value in outputs.items():
                summary += f"- {key}: {value}\n"

        return summary

    def run_phase_with_openai(
        self, phase: DMAICPhase, openai_config: Optional[Dict[str, Any]] = None
    ):
        """
        Reruns a specific DMAIC phase, re-initializing its agent and resetting its data.

        Args:
            phase: The DMAICPhase enum value to rerun.
            openai_config: Optional dictionary with "system_prompt" or "model"
                           to override the agent's default configuration for this run.

        Returns:
            Initial guidance for the re-initiated phase.
        """
        if not isinstance(phase, DMAICPhase):
            raise ValueError(
                f"Phase must be a DMAICPhase enum value, got {type(phase)}"
            )

        if not self.client:
            # Attempt to initialize client if not already done, though it should be by __init__
            self.client = initialize_openai()
            if not self.client:
                return f"Error: OpenAI client not initialized. Cannot run {phase.value} phase."

        current_openai_config = openai_config or {}

        # Determine system prompt: use from config, or default for the phase
        # Fallback to a generic prompt if somehow the phase is not in self.agent_system_prompts
        default_prompt = self.agent_system_prompts.get(
            phase, f"You are an assistant for the {phase.value} phase of DMAIC."
        )
        system_prompt = current_openai_config.get("system_prompt", default_prompt)

        # Determine model: use from config, or a default model (e.g., the one used in _initialize_agents)
        model = current_openai_config.get("model", "gpt-3.5-turbo")

        # Re-create the agent for this phase with potentially new settings
        self.agents[phase] = create_agent(
            system_prompt=system_prompt, client=self.client, model=model
        )

        # Reset the specific phase data in project_data to ensure a fresh start
        # This effectively clears previous conversations, outputs, and completion status for the phase.
        self.project_data["phases"][phase.value] = {
            "started_at": datetime.now().isoformat(),  # Mark new start time for this "rerun"
            "conversation": [],
            "outputs": {},
            "completed": False,
        }

        # Set current phase and return initial guidance using the existing start_phase logic
        # start_phase will use the newly initialized phase data structure.
        return self.start_phase(phase)
