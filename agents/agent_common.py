"""
Common components for the agent system.

This module contains shared definitions, enums, and base classes used by all agents.
"""

import enum
import time
import uuid
import queue
import logging
from typing import Dict, Any, List, Optional, Set, Union, Callable, TypeVar
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
    """Message that can be passed between agents."""
    source: str
    target: str
    message_type: str
    content: Dict[str, Any]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)
    priority: AgentPriority = field(default=AgentPriority.MEDIUM)
    requires_response: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary representation."""
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "message_type": self.message_type,
            "content": self.content,
            "timestamp": self.timestamp,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "requires_response": self.requires_response
        }


@dataclass
class Agent:
    """
    Represents an agent in the system with its role, capabilities, and priority.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: AgentRole = field(default=AgentRole.WORKER)
    capabilities: Set[AgentCapability] = field(default_factory=set)
    priority: AgentPriority = field(default=AgentPriority.LOW)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent instance to a dictionary representation.
        """
        return asdict(self)


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, agent_id: str = None, role: AgentRole = AgentRole.WORKER):
        """
        Initialize a base agent.

        Args:
            agent_id: Unique identifier for this agent
            role: The role this agent fulfills in the system
        """
        self.agent_id = agent_id or f"{role.name}_{str(uuid.uuid4())[:8]}"
        self.role = role
        self.capabilities: Set[AgentCapability] = set()
        self.status = "initialized"
        self.last_activity = time.time()
        self.inbox = queue.Queue()
        self.output_handler = None  # Will be set by orchestrator

    def receive_message(self, message: AgentMessage) -> bool:
        """
        Receive a message and add it to the agent's inbox.

        Args:
            message: The message to receive

        Returns:
            True if the message was successfully queued, False otherwise
        """
        try:
            self.inbox.put(message)
            self.last_activity = time.time()
            return True
        except Exception as e:
            if self.output_handler:
                self.output_handler.log_error(f"Error queueing message: {e}")
            return False

    def process_inbox(self) -> int:
        """
        Process messages in the agent's inbox.

        Returns:
            Number of messages processed
        """
        processed = 0

        try:
            while not self.inbox.empty():
                message = self.inbox.get_nowait()
                self.process_message(message)
                processed += 1
                self.last_activity = time.time()
        except queue.Empty:
            pass  # Inbox is empty
        except Exception as e:
            if self.output_handler:
                self.output_handler.log_error(f"Error processing inbox: {e}")

        return processed

    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Process a single message.

        Args:
            message: The message to process

        Returns:
            Response message if applicable, None otherwise
        """
        # Handle system messages like ping
        if message.message_type == PING_REQUEST:
            # Create a response
            return self._handle_ping(message)

        # Log that we received a message but don't know how to handle it
        if self.output_handler:
            self.output_handler.log_warning(
                f"Agent {self.agent_id} doesn't know how to handle message type: {message.message_type}"
            )
        return None

    def _handle_ping(self, message: AgentMessage) -> AgentMessage:
        """Handle a ping request."""
        response = AgentMessage(
            source=self.agent_id,
            target=message.source,
            message_type=f"{PING_REQUEST}_response",
            content={"status": "ok", "time": time.time()},
            correlation_id=message.correlation_id,
        )

        # Optionally log the ping
        if self.output_handler:
            self.output_handler.log_debug(f"Agent {self.agent_id} received ping, responding with pong")

        return response

    def update(self) -> Dict[str, Any]:
        """
        Update the agent state (called periodically).

        Returns:
            Dictionary with status information
        """
        # Process any pending messages
        processed = self.process_inbox()

        # Perform any agent-specific update logic
        # This is meant to be overridden by subclasses

        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "last_activity": self.last_activity,
            "messages_processed": processed,
            "inbox_size": self.inbox.qsize(),
        }