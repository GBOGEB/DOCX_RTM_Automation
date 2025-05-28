"""
Agent system for DOCX RTM Automation.

This package contains all agents used within the system to facilitate
automation tasks, including orchestrating workflows, managing Git operations,
and handling agent-specific roles and capabilities.
"""

# Import key agent classes for convenience - using relative imports
from .agent_common import AgentRole, AgentCapability, BaseAgent, AgentMessage

# Import all agents
# Note the cyclic import is mitigated by the if __name__ == "__main__" guard in agent_orchestrator.py
from .agent_orchestrator import AgentOrchestrator
from .git_agent import GitAgent