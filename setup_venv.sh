#!/bin/bash

echo "Setting up virtual environment for DOCX RTM Automation..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Determine correct activation command based on OS
case "$(uname -s)" in
    CYGWIN*|MINGW*|MSYS*)
        # Windows
        ACTIVATE_CMD=".venv\\Scripts\\activate"
        ;;
    *)
        # Unix-like
        ACTIVATE_CMD=".venv/bin/activate"
        ;;
esac

echo "To activate the virtual environment, run:"
echo "source $ACTIVATE_CMD"

# Offer to activate if running interactively
if [ -t 0 ]; then
    read -p "Activate virtual environment now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Activating virtual environment..."
        source "$ACTIVATE_CMD"

        # Install dependencies
        echo "Installing dependencies..."
        pip install --upgrade pip

        # Check if requirements.txt exists
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        else
            # Install core dependencies
            pip install pytest pyyaml docx2python markdown rich lxml
            pip install flake8 black isort mypy pytest-cov pylint

            # Generate requirements.txt
            echo "Generating requirements.txt..."
            pip freeze > requirements.txt
        fi

        echo "Setup complete. Virtual environment is active."
        echo "You can now run: ./run.sh help"
    fi
fi

# Create basic package structure if it doesn't exist
if [ ! -d "src" ] || [ ! -d "agents" ]; then
    echo "Creating basic package structure..."
    mkdir -p src/core src/utils src/extractors src/visualizers agents tests

    # Create __init__.py files
    for dir in src src/core src/utils src/extractors src/visualizers agents tests; do
        touch "$dir/__init__.py"
    done

    echo "Basic package structure created."
fi

# Check if the agent files exist and are importable
echo "Checking agent system files..."
if [ -f "agents/agent_common.py" ] && [ -f "agents/git_agent.py" ]; then
    echo "Agent system files found. Verifying imports..."

    # Try to import agent modules
    PYTHON_CMD="
import sys
import os
sys.path.insert(0, os.getcwd())
try:
    from agents.agent_common import BaseAgent, AgentRole, AgentCapability
    from agents.git_agent import GitAgent
    print('Agent imports successful!')
except Exception as e:
    print(f'Error importing agent modules: {e}')
    sys.exit(1)
"

    python -c "$PYTHON_CMD" || {
        echo "Error importing agent modules. Please check the files for syntax errors."
        echo "You may need to fix imports or class definitions."
    }
else
    echo "Some agent system files are missing. Run the lint.sh script to create them."
fi

echo "Environment setup check complete."
