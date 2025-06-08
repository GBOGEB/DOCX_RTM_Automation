#!/bin/bash

echo "Fixing imports and dependencies in the agent system..."

# Define the directory to search for files
PROJECT_DIR="/c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0"

# Create an __init__.py for agents directory if it doesn't exist
if [ ! -f "agents/__init__.py" ]; then
    echo "Creating agents/__init__.py..."
    cat > "agents/__init__.py" << 'EOF'
"""
Agent system for DOCX RTM Automation.

This package contains all agents used within the system.
"""

# Import key agent classes for convenience
from .agent_common import AgentRole, AgentCapability, BaseAgent, AgentMessage

# Import agents individually to avoid circular imports
from .git_agent import GitAgent
EOF
    echo "Created agents/__init__.py"
fi

# Check for and fix common import issues in agent_common.py
if [ -f "agents/agent_common.py" ]; then
    echo "Checking agents/agent_common.py for issues..."

    # Check for missing imports
    if ! grep -q "import enum" "agents/agent_common.py"; then
        echo "Adding missing import 'enum' to agent_common.py"
        sed -i '1i import enum' "agents/agent_common.py"
    fi

    if ! grep -q "import time" "agents/agent_common.py"; then
        echo "Adding missing import 'time' to agent_common.py"
        sed -i '1i import time' "agents/agent_common.py"
    fi

    if ! grep -q "import uuid" "agents/agent_common.py"; then
        echo "Adding missing import 'uuid' to agent_common.py"
        sed -i '1i import uuid' "agents/agent_common.py"
    fi

    if ! grep -q "import queue" "agents/agent_common.py"; then
        echo "Adding missing import 'queue' to agent_common.py"
        sed -i '1i import queue' "agents/agent_common.py"
    fi

    echo "Fixed imports in agent_common.py"
fi

# Check dmaic related imports in agent_orchestrator.py
if [ -f "agents/agent_orchestrator.py" ]; then
    echo "Checking agents/agent_orchestrator.py for issues..."

    # Create minimal dmaic.py if it doesn't exist
    if [ ! -f "dmaic.py" ]; then
        echo "Creating minimal dmaic.py..."
        cat > "dmaic.py" << 'EOF'
"""
DMAIC (Define, Measure, Analyze, Improve, Control) handler module.
This is a placeholder implementation.
"""

class DMAICHandler:
    def __init__(self, project_name):
        self.project_name = project_name
        self.phase = "Define"

    def set_phase(self, phase):
        """Set the current DMAIC phase."""
        self.phase = phase

    def get_phase(self):
        """Get the current DMAIC phase."""
        return self.phase
EOF
        echo "Created minimal dmaic.py"
    fi

    # Create minimal utils modules if they don't exist
    if [ ! -d "utils" ]; then
        echo "Creating utils directory and minimal implementations..."
        mkdir -p utils

        # Create output_handler.py
        cat > "utils/output_handler.py" << 'EOF'
"""
Output handler for logging and reporting.
This is a placeholder implementation.
"""

import logging

class OutputHandler:
    def __init__(self):
        logging.basicConfig(level=logging.INFO,
                           format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("RTM_Automation")

    def log_info(self, message):
        self.logger.info(message)

    def log_error(self, message):
        self.logger.error(message)

    def log_warning(self, message):
        self.logger.warning(message)

    def log_debug(self, message):
        self.logger.debug(message)

    def log_critical(self, message, exc_info=False):
        self.logger.critical(message, exc_info=exc_info)
EOF

        # Create paths_manager.py
        cat > "utils/paths_manager.py" << 'EOF'
"""
Paths manager for handling paths in the project.
This is a placeholder implementation.
"""

import os
from pathlib import Path

class PathsManager:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.data_dir = os.path.join(self.project_root, "data")
        self.output_dir = os.path.join(self.project_root, "output")

        # Create directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def get_data_dir(self):
        """Get the data directory path."""
        return self.data_dir

    def get_output_dir(self):
        """Get the output directory path."""
        return self.output_dir
EOF

        # Create __init__.py
        cat > "utils/__init__.py" << 'EOF'
"""
Utilities package for DOCX RTM Automation.
"""
EOF

        echo "Created minimal utils modules"
    fi

    echo "Fixed imports for agent_orchestrator.py"
fi

# Try to run a basic check
echo "Verifying agent system setup..."
python -c "
try:
    from agents.agent_common import BaseAgent, AgentRole, AgentCapability
    from agents.git_agent import GitAgent
    print('Agent system imports working correctly!')
except ImportError as e:
    print(f'Error: {e}')
    print('Some imports are still not working correctly.')
except SyntaxError as e:
    print(f'Syntax Error: {e}')
    print('There are syntax errors in the code. Please check the files manually.')
except Exception as e:
    print(f'Unexpected error: {e}')
    print('Please check the files manually.')
"

echo "Import fixes complete."