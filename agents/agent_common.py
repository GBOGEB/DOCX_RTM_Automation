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