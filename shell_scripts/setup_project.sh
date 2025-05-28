#!/bin/bash

# Script: setup_project.sh
# Description: Sets up the project environment, including virtual environment and dependencies.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${PROJECT_ROOT_DIR}/.venv"
REQUIREMENTS_FILE="${PROJECT_ROOT_DIR}/requirements.txt" # Assuming you have one
PYTHON_CMD="python" # Change to "python3" if needed

# Source common utilities
source "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh"

log_message "INFO" "Starting project setup..."
cd "$PROJECT_ROOT_DIR"

# 1. Check for Python
if ! command_exists $PYTHON_CMD; then
    log_message "ERROR" "$PYTHON_CMD could not be found. Please install Python 3.x."
    exit 1
fi

log_message "INFO" "Python found: $($PYTHON_CMD --version)"

# 2. Create/Recreate Virtual Environment
if [ -d "$VENV_PATH" ]; then
    log_message "INFO" "Virtual environment already exists at $VENV_PATH."
    read -p "Recreate virtual environment? (y/N): " recreate_venv
    if [[ "$recreate_venv" =~ ^[Yy]$ ]]; then
        log_message "INFO" "Removing existing virtual environment..."
        rm -rf "$VENV_PATH"
        log_message "INFO" "Creating new virtual environment..."
        $PYTHON_CMD -m venv "$VENV_PATH"
    fi
else
    log_message "INFO" "Creating virtual environment at $VENV_PATH..."
    $PYTHON_CMD -m venv "$VENV_PATH"
fi

# 3. Activate Virtual Environment
log_message "INFO" "Activating virtual environment..."
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
    log_message "INFO" "Virtual environment activated (Unix style)."
elif [ -f "$VENV_PATH/Scripts/activate" ]; then
    source "$VENV_PATH/Scripts/activate"
    log_message "INFO" "Virtual environment activated (Windows style)."
else
    log_message "ERROR" "Cannot find activation script in $VENV_PATH/bin/ or $VENV_PATH/Scripts/."
    exit 1
fi

# 4. Install/Update Dependencies with platform-specific approach
if [ -f "$REQUIREMENTS_FILE" ]; then
    log_message "INFO" "Installing/updating dependencies from $REQUIREMENTS_FILE..."

    # Upgrade pip in a platform-specific way - using the venv's specific Python executable for safety
    log_message "INFO" "Upgrading pip..."

    # For Windows, we need to use the specific Python exe in the virtual env
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        if [ -f "$VENV_PATH/Scripts/python.exe" ]; then
            "$VENV_PATH/Scripts/python.exe" -m pip install --upgrade pip
        else
            log_message "WARNING" "Could not find python.exe in virtual environment. Using activated environment."
            python -m pip install --upgrade pip
        fi
    else
        # Unix-like platforms can use pip directly with activated environment
        pip install --upgrade pip
    fi

    # Wait a moment to ensure pip upgrade completes
    sleep 2

    # Install requirements with a retry mechanism
    log_message "INFO" "Installing requirements..."
    MAX_RETRIES=3
    RETRY_COUNT=0

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if python -m pip install -r "$REQUIREMENTS_FILE"; then
            log_message "SUCCESS" "Dependencies installed/updated."
            break
        else
            RETRY_COUNT=$((RETRY_COUNT+1))
            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                log_message "WARNING" "Dependency installation failed. Retrying ($RETRY_COUNT/$MAX_RETRIES)..."
                sleep 2
            else
                log_message "ERROR" "Failed to install dependencies after $MAX_RETRIES attempts."
                exit 1
            fi
        fi
    done
else
    log_message "WARNING" "requirements.txt not found at $REQUIREMENTS_FILE. Creating a minimal one..."
    echo "# Core dependencies for DOCX_RTM_Automation" > "$REQUIREMENTS_FILE"
    echo "pyyaml~=6.0" >> "$REQUIREMENTS_FILE"
    echo "pandas~=2.0.0" >> "$REQUIREMENTS_FILE"
    echo "markdown-it-py~=3.0.0" >> "$REQUIREMENTS_FILE"
    echo "openai~=1.6.0" >> "$REQUIREMENTS_FILE"
    echo "python-docx~=0.8.11" >> "$REQUIREMENTS_FILE"
    echo "black~=23.9.1" >> "$REQUIREMENTS_FILE"
    echo "flake8~=6.1.0" >> "$REQUIREMENTS_FILE"
    echo "pre-commit~=3.5.0" >> "$REQUIREMENTS_FILE"
    log_message "INFO" "Created a minimal requirements.txt. Installing..."

    # Upgrade pip in a platform-specific way
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
        python -m pip install --upgrade pip
    else
        pip install --upgrade pip
    fi

    pip install -r "$REQUIREMENTS_FILE"
    log_message "SUCCESS" "Minimal dependencies installed."
fi

# 5. Create necessary directories
log_message "INFO" "Ensuring standard directories exist..."
mkdir -p "${PROJECT_ROOT_DIR}/logs"
mkdir -p "${PROJECT_ROOT_DIR}/output/reports"
mkdir -p "${PROJECT_ROOT_DIR}/output/generated_code"
mkdir -p "${PROJECT_ROOT_DIR}/output/diagrams"
mkdir -p "${PROJECT_ROOT_DIR}/output/pipeline_analysis"
mkdir -p "${PROJECT_ROOT_DIR}/data/input_docs"

# 6. Install pre-commit hooks if .pre-commit-config.yaml exists
if [ -f "${PROJECT_ROOT_DIR}/.pre-commit-config.yaml" ]; then
    if command_exists pre-commit; then
        log_message "INFO" "Installing pre-commit hooks..."
        pre-commit install
        log_message "SUCCESS" "Pre-commit hooks installed."
    else
        log_message "WARNING" "pre-commit command not found. Installing pre-commit..."
        pip install pre-commit
        pre-commit install
        log_message "SUCCESS" "Installed pre-commit and set up hooks."
    fi
else
    log_message "WARNING" ".pre-commit-config.yaml not found. Pre-commit hooks not installed."
fi

# Make shell scripts executable
log_message "INFO" "Making shell scripts executable..."
find "${PROJECT_ROOT_DIR}/shell_scripts" -name "*.sh" -exec chmod +x {} \;
log_message "SUCCESS" "Shell scripts are now executable."

log_message "SUCCESS" "Project setup completed successfully."
echo ""
echo "To activate the virtual environment in your current shell, run:"
echo "source $VENV_PATH/bin/activate  (for Linux/macOS)"
echo "source $VENV_PATH/Scripts/activate (for Windows Git Bash)"
