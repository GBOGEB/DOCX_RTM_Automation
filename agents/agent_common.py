"""
Common components for the agent system.

This module contains shared definitions, enums, and base classes used by all agents.
"""

import enum
import time
import uuid
import queue
import logging
from typing import Dict, Any, List, Optional, Union, Callable, TypeVar
from dataclasses import dataclass, field, asdict

# Common message types
PING_REQUEST = "ping"
PING_RESPONSE = "pong"
ERROR_RESPONSE = "error"
INFO_MESSAGE = "info"

class AgentRole(enum.Enum):
    """Roles that agents can fulfill in the system."""
    ORCHESTRATOR = "orchestrator"  # Coordinates other agents
    ANALYSER = "analyzer"  # Analyzes content
    ANALYST = "analyst"    # Alternative spelling for analyzer
    GENERATOR = "generator"  # Generates content
    TOOL = "tool"  # Provides specific functionality
    ASSISTANT = "assistant"  # Provides assistance to users
    WORKER = "worker"  # Performs tasks


class AgentCapability(enum.Enum):
    """Capabilities that agents can have."""
    DOCUMENT_PARSING = "document_parsing"
    DOCUMENT_GENERATION = "document_generation"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    IMPACT_ANALYSIS = "impact_analysis"
    GIT_OPERATIONS = "git_operations"
    VERSION_CONTROL = "version_control"
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    TEST_PLAN_GENERATION = "test_plan_generation"
    TRACEABILITY_ANALYSIS = "traceability_analysis"
    CICD_PIPELINE_ANALYSIS = "cicd_pipeline_analysis"
    CICD_METRICS_COLLECTION = "cicd_metrics_collection"
    CICD_IMPROVEMENT_PLANNING = "cicd_improvement_planning"
    CICD_BUILD_FAILURE_ANALYSIS = "cicd_build_failure_analysis"


class AgentPriority(enum.Enum):
    """Priority levels for agent tasks and messages."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


# Define type variables for generic validation
T = TypeVar('T')

def validate_input(value: Any, expected_type: Union[type, List[type]],
                  field_name: str, allow_none: bool = False,
                  custom_validator: Optional[Callable[[Any], bool]] = None,
                  error_message: Optional[str] = None) -> T:
    """
    Validate that an input value meets expected criteria.

    Args:
        value: The value to validate
        expected_type: Type or list of types the value should be
        field_name: Name of the field (for error messages)
        allow_none: Whether None is an acceptable value
        custom_validator: Optional function for additional validation
        error_message: Optional custom error message

    Returns:
        The validated value (potentially transformed)

    Raises:
        ValueError: If validation fails
        TypeError: If type check fails
    """
    # Handle None values
    if value is None:
        if allow_none:
            return None
        raise ValueError(f"{field_name} cannot be None")

    # Type checking
    expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
    if not any(isinstance(value, t) for t in expected_types):
        type_names = " or ".join(t.__name__ for t in expected_types)
        raise TypeError(
            error_message or f"{field_name} must be of type {type_names}, got {type(value).__name__}"
        )

    # Custom validation
    if custom_validator and not custom_validator(value):
        raise ValueError(
            error_message or f"{field_name} failed custom validation"
        )

    return value


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: AgentPriority = AgentPriority.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return asdict(self)


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    agent_id: str
    name: str
    role: AgentRole
    capabilities: List[AgentCapability]
    max_tasks: int = 10
    timeout: float = 30.0
    retry_count: int = 3
    debug_mode: bool = False

    def __post_init__(self):
        """Validate configuration after initialization."""
        validate_input(self.agent_id, str, "agent_id")
        validate_input(self.name, str, "name")
        validate_input(self.role, AgentRole, "role")
        validate_input(self.capabilities, list, "capabilities")
        validate_input(self.max_tasks, int, "max_tasks",
                      custom_validator=lambda x: x > 0)
        validate_input(self.timeout, [int, float], "timeout",
                      custom_validator=lambda x: x > 0)


@dataclass
class AgentStatus:
    """Status information for an agent."""
    agent_id: str
    is_active: bool = True
    current_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    last_heartbeat: float = field(default_factory=time.time)
    status_message: str = "Ready"

    def update_heartbeat(self):
        """Update the last heartbeat timestamp."""
        self.last_heartbeat = time.time()


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, config: AgentConfig):
        """Initialize the agent with configuration."""
        self.config = config
        self.status = AgentStatus(agent_id=config.agent_id)
        self.task_queue = queue.Queue(maxsize=config.max_tasks)
        self.logger = logging.getLogger(f"Agent.{config.name}")
        self._running = False

    def start(self) -> bool:
        """Start the agent."""
        try:
            self._running = True
            self.status.is_active = True
            self.status.status_message = "Running"
            self.logger.info(f"Agent {self.config.name} started")
            return True
        except Exception as e:
            self.logger.error(f"Failed to start agent: {e}")
            return False

    def stop(self) -> bool:
        """Stop the agent."""
        try:
            self._running = False
            self.status.is_active = False
            self.status.status_message = "Stopped"
            self.logger.info(f"Agent {self.config.name} stopped")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop agent: {e}")
            return False

    def is_running(self) -> bool:
        """Check if the agent is running."""
        return self._running and self.status.is_active

    def get_status(self) -> AgentStatus:
        """Get current agent status."""
        self.status.update_heartbeat()
        return self.status

    def can_handle_capability(self, capability: AgentCapability) -> bool:
        """Check if agent can handle a specific capability."""
        return capability in self.config.capabilities

    def add_task(self, task: Dict[str, Any]) -> bool:
        """Add a task to the agent's queue."""
        try:
            if self.task_queue.full():
                self.logger.warning("Task queue is full, cannot add new task")
                return False

            self.task_queue.put(task, block=False)
            self.status.current_tasks = self.task_queue.qsize()
            return True
        except Exception as e:
            self.logger.error(f"Failed to add task: {e}")
            return False

    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process an incoming message."""
        self.logger.debug(f"Processing message: {message.message_type}")

        # Handle common message types
        if message.message_type == PING_REQUEST:
            return AgentMessage(
                sender_id=self.config.agent_id,
                recipient_id=message.sender_id,
                message_type=PING_RESPONSE,
                content={"status": "ok", "timestamp": time.time()}
            )

        # Override in subclasses for specific message handling
        return self._handle_custom_message(message)

    def _handle_custom_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle custom message types. Override in subclasses."""
        self.logger.warning(f"Unhandled message type: {message.message_type}")
        return None
