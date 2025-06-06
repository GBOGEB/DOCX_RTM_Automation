"""
Agent module initialization.

This file initializes the agents package and imports key components for external use.
"""

import os
import sys
from pathlib import Path

# If this file is run directly, add the parent directory to path
if __name__ == "__main__":
    # Get the project root directory
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Now imports will work properly even when this file is run directly
    import agents.agent_common as agent_common
    import agents.agent_orchestrator as agent_orchestrator
    import agents.dmaic_cicd_agent as dmaic_cicd_agent
    import agents.git_agent as git_agent
    import agents.requirement_analyzer as requirement_analyzer
    import agents.copilot_agent as copilot_agent
    import agents.openai_service_stub as openai_service_stub

    # Expose to the module namespace
    from agents.agent_common import (
        BaseAgent,
        AgentRole,
        AgentCapability,
        AgentMessage,
        StandardAgentResponse,
        AgentPriority,
        PING_REQUEST,
        PONG_RESPONSE,
        AGENT_READY,
        AGENT_SHUTDOWN,
        AGENT_ERROR,
    )
    from agents.agent_orchestrator import AgentOrchestrator
    from agents.dmaic_cicd_agent import DMAICCICDAgent
    from agents.git_agent import GitAgent
    from agents.requirement_analyzer import (
        RequirementAnalysisAgent,
        TraceabilityAnalysisAgent,
    )
    from agents.copilot_agent import CopilotAgent
    from agents.openai_service_stub import OpenAIService
else:
    # Normal import mode - when the package is imported, not run directly
    from .agent_common import (
        BaseAgent,
        AgentRole,
        AgentCapability,
        AgentMessage,
        StandardAgentResponse,
        AgentPriority,
        PING_REQUEST,
        PONG_RESPONSE,
        AGENT_READY,
        AGENT_SHUTDOWN,
        AGENT_ERROR,
    )
    from .agent_orchestrator import AgentOrchestrator
    from .dmaic_cicd_agent import DMAICCICDAgent
    from .git_agent import GitAgent
    from .requirement_analyzer import (
        RequirementAnalysisAgent,
        TraceabilityAnalysisAgent,
    )
    from .copilot_agent import CopilotAgent
    from .openai_service_stub import OpenAIService

# List of agent modules to be made available for import
__all__ = [
    "AgentOrchestrator",
    "BaseAgent",
    "AgentRole",
    "AgentCapability",
    "AgentMessage",
    "StandardAgentResponse",
    "PING_REQUEST",
    "PONG_RESPONSE",
    "AGENT_READY",
    "AGENT_SHUTDOWN",
    "AGENT_ERROR",
    "AgentPriority",
    "DMAICCICDAgent",
    "GitAgent",
    "RequirementAnalysisAgent",
    "TraceabilityAnalysisAgent",
    "CopilotAgent",
    "OpenAIService",
]

# If run directly, execute a basic check
if __name__ == "__main__":
    print("Agent package initialized successfully with direct execution mode.")
    print("Available components:")
    for component in __all__:
        print(f"- {component}")
