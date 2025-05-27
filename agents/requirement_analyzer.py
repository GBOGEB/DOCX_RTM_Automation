from typing import Dict, Any, List, Optional

from config.openai_integration import initialize_openai, create_agent as create_openai_llm_agent
from agents.agent_common import BaseAgent, AgentRole, AgentMessage, StandardAgentResponse, AgentCapability, validate_input

# Initialize OpenAI client once at module level if shared, or per instance
# For simplicity here, we assume it might be passed or initialized in __init__
# client = initialize_openai() # This might be better handled by passing client to agents

class RequirementAnalysisAgent(BaseAgent):
    """
    Agent specialized in analyzing software requirements for clarity, testability, and completeness.
    """
    def __init__(self, agent_id: str, output_handler: Optional[Any] = None, client: Optional[Any] = None, model: str = "gpt-4"):
        super().__init__(agent_id, AgentRole.ANALYST, output_handler)
        self.client = client or initialize_openai() # Ensure client is initialized
        self.model = model
        self.llm_agent = create_openai_llm_agent(
            system_prompt="""You are a requirements engineering expert specialized in analyzing software requirements.
Your task is to evaluate requirements for clarity, testability, and completeness.""",
            client=self.client,
            model=self.model
        )
        self.register_capability(AgentCapability.REQUIREMENT_CLARITY_ANALYSIS)
        self.register_capability(AgentCapability.REQUIREMENT_TESTABILITY_ANALYSIS)
        self.register_capability(AgentCapability.REQUIREMENT_COMPLETENESS_ANALYSIS)
        self.register_message_handler("analyze_single_requirement", self.handle_analyze_single_requirement)

    def handle_analyze_single_requirement(self, message: AgentMessage) -> StandardAgentResponse:
        """Handles a request to analyze a single requirement."""
        if not validate_input(message.content, ["requirement_text"]):
            return {
                "status": "error",
                "message": "Missing 'requirement_text' in message content.",
                "data": None, "error_details": "Invalid input", "markdown_content": None
            }

        requirement_text = message.content["requirement_text"]
        prompt = f"Analyze this requirement for clarity, testability, and completeness:\n\n{requirement_text}"

        try:
            result, _ = self.llm_agent(prompt)
            # Attempt to structure the result or provide it as markdown
            markdown_report = f"### Requirement Analysis Report for:\n\n```\n{requirement_text}\n```\n\n**Analysis:**\n{result}"
            return {
                "status": "success",
                "message": "Requirement analyzed successfully.",
                "data": {"analysis_text": result, "original_requirement": requirement_text},
                "error_details": None,
                "markdown_content": markdown_report
            }
        except Exception as e:
            if self.output_handler:
                self.output_handler.log_error(f"Error during requirement analysis for agent {self.agent_id}: {e}")
            return {
                "status": "error",
                "message": "Failed to analyze requirement.",
                "data": {"original_requirement": requirement_text},
                "error_details": str(e),
                "markdown_content": None
            }

class TraceabilityAnalysisAgent(BaseAgent):
    """
    Agent specialized in requirement traceability analysis.
    """
    def __init__(self, agent_id: str, output_handler: Optional[Any] = None, client: Optional[Any] = None, model: str = "gpt-3.5-turbo"):
        super().__init__(agent_id, AgentRole.ANALYST, output_handler)
        self.client = client or initialize_openai() # Ensure client is initialized
        self.model = model
        self.llm_agent = create_openai_llm_agent(
            system_prompt="""You are specialized in requirement traceability.
Your task is to identify relationships between requirements and suggest improvements for traceability.""",
            client=self.client,
            model=self.model # Default model, can be overridden
        )
        self.register_capability(AgentCapability.REQUIREMENT_TRACEABILITY_ANALYSIS)
        self.register_message_handler("check_traceability", self.handle_check_traceability)

    def handle_check_traceability(self, message: AgentMessage) -> StandardAgentResponse:
        """Handles a request to check traceability between requirements."""
        if not validate_input(message.content, ["requirements_list"]):
            return {
                "status": "error",
                "message": "Missing 'requirements_list' in message content.",
                "data": None, "error_details": "Invalid input", "markdown_content": None
            }

        requirements_list = message.content["requirements_list"]
        if not isinstance(requirements_list, list) or not all(isinstance(req, str) for req in requirements_list):
            return {
                "status": "error",
                "message": "'requirements_list' must be a list of strings.",
                "data": None, "error_details": "Invalid input type", "markdown_content": None
            }

        prompt = "Analyze traceability between these requirements:\n\n" + "\n".join(requirements_list)

        try:
            result, _ = self.llm_agent(prompt)
            markdown_report = f"### Traceability Analysis Report for:\n\n"
            for i, req in enumerate(requirements_list):
                markdown_report += f"{i+1}. ```\n{req}\n```\n"
            markdown_report += f"\n**Analysis:**\n{result}"

            return {
                "status": "success",
                "message": "Traceability analyzed successfully.",
                "data": {"traceability_analysis": result, "original_requirements": requirements_list},
                "error_details": None,
                "markdown_content": markdown_report
            }
        except Exception as e:
            if self.output_handler:
                self.output_handler.log_error(f"Error during traceability analysis for agent {self.agent_id}: {e}")
            return {
                "status": "error",
                "message": "Failed to analyze traceability.",
                "data": {"original_requirements": requirements_list},
                "error_details": str(e),
                "markdown_content": None
            }

# Example usage (for testing, actual instantiation would be by orchestrator)
if __name__ == '__main__':
    class MockOutputHandler:
        def log_info(self, msg): print(f"INFO: {msg}")
        def log_error(self, msg): print(f"ERROR: {msg}")
        def log_debug(self, msg): print(f"DEBUG: {msg}")

    mock_output = MockOutputHandler()

    # Assuming OpenAI API key is set in environment
    req_agent = RequirementAnalysisAgent("req_analyzer_01", output_handler=mock_output)
    trace_agent = TraceabilityAnalysisAgent("trace_analyzer_01", output_handler=mock_output)

    # Test RequirementAnalysisAgent
    req_msg_content = {"requirement_text": "The system shall allow users to log in."}
    req_message = AgentMessage("test_suite", req_agent.agent_id, "analyze_single_requirement", req_msg_content)
    req_response = req_agent.handle_analyze_single_requirement(req_message)
    mock_output.log_info(f"Requirement Analysis Response: {req_response}")

    # Test TraceabilityAnalysisAgent
    trace_msg_content = {"requirements_list": ["REQ1: User login", "REQ2: Password encryption", "REQ3: Session management"]}
    trace_message = AgentMessage("test_suite", trace_agent.agent_id, "check_traceability", trace_msg_content)
    trace_response = trace_agent.handle_check_traceability(trace_message)
    mock_output.log_info(f"Traceability Analysis Response: {trace_response}")
