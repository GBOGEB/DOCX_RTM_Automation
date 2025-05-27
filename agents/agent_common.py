# agent_common.py

import uuid
import time
from enum import Enum, auto
from queue import Queue
from typing import Dict, Any, List, Optional, Callable, Set, TypedDict, Union

class AgentRole(Enum):
    """Defines the functional role of an agent in the system"""
    ORCHESTRATOR = auto()  # Manages other agents and workflows
    ANALYST = auto()       # Performs data analysis, generates insights
    REPOSITORY = auto()    # Interacts with code repositories (Git)
    CONTENT = auto()       # Generates or processes content (code, docs)
    AUTOMATION = auto()    # Executes automated tasks (CI/CD, scripts)
    DATA_SOURCE = auto()   # Provides access to data sources
    USER_INTERFACE = auto() # Interacts with users

class AgentPriority(Enum):
    """Defines the priority for message processing or agent tasks"""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class AgentCapability(Enum):
    """Standardized list of agent capabilities"""
    UNDEFINED = auto()
    # Git Agent Capabilities
    GIT_CLONE = auto()
    GIT_PULL = auto()
    GIT_PUSH = auto()
    GIT_COMMIT = auto()
    GIT_BRANCH_OPERATIONS = auto()
    GIT_PR_CREATE = auto()
    GIT_STATUS_CHECK = auto()
    # Copilot Agent Capabilities
    CODE_GENERATION = auto()
    CODE_ANALYSIS = auto()
    FILE_CONVERSION = auto()
    REQUIREMENT_EXTRACTION = auto()
    REPORT_GENERATION = auto()
    REPO_ANALYSIS = auto() # General repo analysis, distinct from Git ops
    BASH_SCRIPT_GENERATION = auto()
    BASH_SCRIPT_EXECUTION = auto()
    DEPLOYMENT_CONFIG_GENERATION = auto()
    GITHUB_ACTIONS_WORKFLOW_GENERATION = auto()
    # Requirement Analyzer Capabilities
    REQUIREMENT_CLARITY_ANALYSIS = auto()
    REQUIREMENT_TESTABILITY_ANALYSIS = auto()
    REQUIREMENT_COMPLETENESS_ANALYSIS = auto()
    REQUIREMENT_TRACEABILITY_ANALYSIS = auto()
    # CI/CD Agent Capabilities
    CICD_PIPELINE_ANALYSIS = auto()
    CICD_METRICS_COLLECTION = auto()
    CICD_IMPROVEMENT_PLANNING = auto()
    CICD_BUILD_FAILURE_ANALYSIS = auto()
    # General Capabilities
    TEXT_SUMMARIZATION = auto()
    DATA_QUERY = auto()
    NATURAL_LANGUAGE_PROCESSING = auto()
    # New Capabilities
    PULL_REQUEST_REVIEW = auto() # Broader than just analysis, could include automated comments
    IMPACT_ANALYSIS = auto() # Assessing impact of changes (code, reqs, etc.)
    DOCUMENT_PARSING = auto() # Specific to parsing various document formats
    CODE_PARSING = auto() # Potentially more detailed than general code_analysis
    DATA_RECOMBINATION = auto() # For merging/transforming structured data
    REQUIREMENT_VALIDATION = auto() # Check requirements against criteria
    TEST_CASE_GENERATION = auto() # Generate test cases from requirements or code
    CONFIGURATION_MANAGEMENT = auto() # Handling config files, deployment settings


class AgentMessage:
    def __init__(self,
                 source: str,
                 target: str,
                 message_type: str,
                 content: Dict[str, Any],
                 priority: AgentPriority = AgentPriority.MEDIUM,
                 requires_response: bool = False,
                 correlation_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None): # Added metadata
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.source = source  # ID of the sending agent
        self.target = target  # ID of the target agent or "broadcast"
        self.message_type = message_type  # e.g., "request_analysis", "git_clone"
        self.content = content  # Payload of the message
        self.priority = priority
        self.requires_response = requires_response
        self.correlation_id = correlation_id or self.id # For tracking request-response pairs
        self.metadata = metadata or {} # Optional metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "source": self.source,
            "target": self.target,
            "message_type": self.message_type,
            "content": self.content,
            "priority": self.priority.name,
            "requires_response": self.requires_response,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata
        }


class StandardAgentResponse(TypedDict):
    """Standardized response structure for agent message handlers."""
    status: str  # "success", "error", "pending", "partial"
    message: Optional[str] # Human-readable message
    data: Optional[Dict[str, Any]] # Payload of the response
    error_details: Optional[str] # Details if status is "error"
    markdown_content: Optional[str] # For responses that include markdown


# Common Message Types (examples, can be expanded)
# Git Operations
GIT_PULL_REQUEST_DETAILS_REQUEST = "get_pull_request_details_request"
GIT_PULL_REQUEST_DETAILS_RESPONSE = "get_pull_request_details_response"
GIT_FILE_CONTENT_REQUEST = "get_file_content_request" # Request content of a file at a specific commit/branch
GIT_FILE_CONTENT_RESPONSE = "get_file_content_response"

# Parsing & Analysis
PARSE_DOCUMENT_COMMAND = "parse_document_command"
PARSE_DOCUMENT_RESPONSE = "parse_document_response"
PARSE_CODE_COMMAND = "parse_code_command"
PARSE_CODE_RESPONSE = "parse_code_response"
IMPACT_ASSESSMENT_REQUEST = "impact_assessment_request"
IMPACT_ASSESSMENT_RESPONSE = "impact_assessment_response"
REQUIREMENT_ANALYSIS_REQUEST = "requirement_analysis_request" # Could be more specific
REQUIREMENT_ANALYSIS_RESPONSE = "requirement_analysis_response"

# Data Handling
DATA_RECOMBINATION_COMMAND = "data_recombination_command"
DATA_RECOMBINATION_RESPONSE = "data_recombination_response"

# General
STATUS_UPDATE = "status_update"
ERROR_NOTIFICATION = "error_notification"


class BaseAgent:
    """Base class for all agents in the system"""

    def __init__(self, agent_id: str, role: AgentRole, output_handler: Optional[Any] = None):
        self.agent_id = agent_id
        self.role = role
        self.status = "idle"
        self.inbox: Queue[AgentMessage] = Queue()
        self.last_activity = time.time()
        self.orchestrator = None  # Will be set by the orchestrator
        self.output_handler = output_handler # For logging and output

        # Agent capabilities and message handlers
        self.capabilities: Set[Union[str, AgentCapability]] = set()
        self.message_handlers: Dict[str, Callable[[AgentMessage], Optional[StandardAgentResponse]]] = {}


    def register_capability(self, capability: Union[str, AgentCapability]):
        """Register a capability for this agent"""
        self.capabilities.add(capability)
        if self.output_handler:
            cap_name = capability.name if isinstance(capability, AgentCapability) else capability
            self.output_handler.log_debug(f"Agent {self.agent_id} registered capability: {cap_name}")

    def register_message_handler(self, message_type: str, handler: Callable[[AgentMessage], Optional[StandardAgentResponse]]):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
        if self.output_handler:
            self.output_handler.log_debug(f"Agent {self.agent_id} registered handler for message type: {message_type}")

    def register_with_orchestrator(self, orchestrator):
        self.orchestrator = orchestrator
        if self.output_handler:
            self.output_handler.log_info(f"Agent {self.agent_id} registered with orchestrator.")

    def send_message(self, message: AgentMessage) -> Optional[str]:
        """Send a message via the orchestrator"""
        if self.orchestrator:
            return self.orchestrator.route_message(message)
        else:
            if self.output_handler:
                self.output_handler.log_error(f"Agent {self.agent_id} cannot send message: Not registered with orchestrator.")
            return None

    def receive_message(self, message: AgentMessage):
        self.inbox.put(message)
        if self.output_handler:
            self.output_handler.log_info(f"Agent {self.agent_id} received message: {message.to_dict()}")

    def process_inbox(self):
        """Process all messages currently in the agent's inbox"""
        while not self.inbox.empty():
            message = self.inbox.get()
            self.last_activity = time.time()
            response: Optional[StandardAgentResponse] = None

            if message.message_type in self.message_handlers:
                try:
                    response = self.message_handlers[message.message_type](message)
                except Exception as e:
                    if self.output_handler:
                        self.output_handler.log_error(f"Error handling message {message.message_type} in {self.agent_id}: {e}")
                    response = {
                        "status": "error",
                        "message": f"Agent {self.agent_id} failed to process message.",
                        "error_details": str(e),
                        "data": None,
                        "markdown_content": None
                    }
            else:
                # Fallback to generic process_message if no specific handler
                response_data = self.process_message(message) # This might return Dict or StandardAgentResponse
                if isinstance(response_data, dict) and "status" in response_data: # Check if it's already StandardAgentResponse like
                    response = response_data # type: ignore
                else: # Adapt to StandardAgentResponse
                    response = {
                        "status": "processed" if response_data is not None else "unhandled",
                        "message": f"Message type {message.message_type} processed by generic handler." if response_data is not None else f"Message type {message.message_type} unhandled.",
                        "data": response_data if isinstance(response_data, dict) else {"result": response_data},
                        "error_details": None,
                        "markdown_content": None
                    }


            if message.requires_response and response and self.orchestrator:
                response_message = AgentMessage(
                    source=self.agent_id,
                    target=message.source,
                    message_type=f"{message.message_type}_response",
                    content=response, # type: ignore
                    priority=message.priority,
                    correlation_id=message.correlation_id
                )
                self.send_message(response_message)
            self.inbox.task_done()

    def process_message(self, message: AgentMessage) -> Optional[Dict[str, Any]]:
        """
        Generic message processing logic if no specific handler is found.
        Subclasses should override this for custom default behavior.
        This method is kept for backward compatibility or simple agents,
        but specific handlers returning StandardAgentResponse are preferred.
        """
        if self.output_handler:
            self.output_handler.log_info(
                f"Agent {self.agent_id} received message from {message.source} "
                f"of type {message.message_type} (no specific handler)."
            )
        # Default: acknowledge receipt
        return {"status": "received", "acknowledged_by": self.agent_id, "original_message_id": message.id}

    def update(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "role": self.role.name,
            "status": self.status,
            "last_activity": self.last_activity,
            "capabilities": [cap.name if isinstance(cap, AgentCapability) else cap for cap in self.capabilities]
        }


# Utility functions (can be kept here or moved to a utils.py if they grow)
def log_message(message: str) -> None:
    """
    Logs a message to the console with a standardized format.

    Args:
        message (str): The message to log.
    """
    print(f"[LOG]: {message}")


def validate_input(data: dict, required_keys: list) -> bool:
    """
    Validates that the required keys are present in the input data.
    Returns True if valid, False otherwise.
    Logs an error if a key is missing.
    """
    for key in required_keys:
        if key not in data:
            log_message(f"Error: Missing required key '{key}' in input data.")
            return False
    return True