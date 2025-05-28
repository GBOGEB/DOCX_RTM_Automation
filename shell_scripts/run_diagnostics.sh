#!/bin/bash

# Script: run_diagnostics.sh
# Description: Runs diagnostic tests to check your system setup

# --- Configuration ---
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="${PROJECT_ROOT_DIR}/.venv"

# Source common utilities
source "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh"

log_message "INFO" "Starting diagnostic tests..."

# Check project structure
log_message "INFO" "Checking project structure..."

# Important directories
directories=(
    "config"
    "code"
    "agents"
    "utils"
    "shell_scripts"
    "pipelines"
    "dmaic"
    "docs"
    "logs"
    "output"
    "data"
)

for dir in "${directories[@]}"; do
    if [ -d "${PROJECT_ROOT_DIR}/$dir" ]; then
        log_message "SUCCESS" "Directory '$dir' exists."
    else
        log_message "WARNING" "Directory '$dir' not found. Some features may not work."
    fi
done

# Check for critical files
log_message "INFO" "Checking for critical files..."

critical_files=(
    "code/main.py"
    "config/paths.yaml"
    "shell_scripts/run_rtm.sh"
    "shell_scripts/common_utils.sh"
)

for file in "${critical_files[@]}"; do
    if [ -f "${PROJECT_ROOT_DIR}/$file" ]; then
        log_message "SUCCESS" "File '$file' exists."
    else
        log_message "ERROR" "Critical file '$file' not found."
    fi
done

# Check Python and virtual environment
log_message "INFO" "Checking Python and virtual environment..."

if command_exists python; then
    PYTHON_VERSION=$(python --version 2>&1)
    log_message "SUCCESS" "Python is installed: $PYTHON_VERSION"
else
    log_message "ERROR" "Python is not installed or not in PATH."
fi

if [ -d "$VENV_PATH" ]; then
    if [ -f "$VENV_PATH/bin/activate" ] || [ -f "$VENV_PATH/Scripts/activate" ]; then
        log_message "SUCCESS" "Virtual environment exists at $VENV_PATH"
    else
        log_message "ERROR" "Virtual environment directory exists but no activation script found."
    fi
else
    log_message "ERROR" "Virtual environment not found at $VENV_PATH. Run setup_project.sh first."
fi

# Check for external dependencies
log_message "INFO" "Checking for external dependencies..."

# Check for Pandoc (required by CopilotAgent for document conversion)
if command_exists pandoc; then
    PANDOC_VERSION=$(pandoc --version | grep -oP 'pandoc\s+\K\d+\.\d+(\.\d+)?')
    log_message "SUCCESS" "Pandoc is installed: version $PANDOC_VERSION"
else
    log_message "WARNING" "Pandoc not found. Document conversion features will be limited."
    log_message "INFO" "Install Pandoc from: https://pandoc.org/installing.html"
fi

# Check for Git
if command_exists git; then
    GIT_VERSION=$(git --version | grep -oP 'git version\s+\K\d+\.\d+(\.\d+)?')
    log_message "SUCCESS" "Git is installed: version $GIT_VERSION"
else
    log_message "ERROR" "Git not found. Git operations will fail."
fi

# Check for Python dependencies (activate venv first)
log_message "INFO" "Checking Python dependencies..."
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
elif [ -f "$VENV_PATH/Scripts/activate" ]; then
    source "$VENV_PATH/Scripts/activate"
else
    log_message "ERROR" "Cannot activate virtual environment. Skipping dependency checks."
    exit 1
fi

# Check critical Python packages
python_packages=(
    "openai"
    "pandas"
    "markdown_it"
    "yaml"
    "flake8"
    "black"
    "pre_commit"
)

for package in "${python_packages[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        # Get version if possible
        VERSION=$(python -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
        log_message "SUCCESS" "Python package '$package' is installed: version $VERSION"
    else
        log_message "ERROR" "Python package '$package' is not installed."
    fi
done

# Check Git submodules
log_message "INFO" "Checking Git submodules..."
if [ -f "${PROJECT_ROOT_DIR}/.gitmodules" ]; then
    log_message "SUCCESS" ".gitmodules file exists."

    # Count submodules
    SUBMODULE_COUNT=$(grep -c "\[submodule" "${PROJECT_ROOT_DIR}/.gitmodules" 2>/dev/null || echo "0")
    if [ "$SUBMODULE_COUNT" -gt 0 ]; then
        log_message "INFO" "Found $SUBMODULE_COUNT submodule(s) in .gitmodules file."
    else
        log_message "WARNING" "No submodules defined in .gitmodules file."
    fi
else
    log_message "INFO" "No .gitmodules file found. If you're using submodules, this is a problem."
fi

# Check pre-commit setup
log_message "INFO" "Checking pre-commit setup..."
if [ -f "${PROJECT_ROOT_DIR}/.pre-commit-config.yaml" ]; then
    log_message "SUCCESS" ".pre-commit-config.yaml file exists."

    if command_exists pre-commit; then
        log_message "INFO" "Running pre-commit hook status check..."
        cd "${PROJECT_ROOT_DIR}" && pre-commit hook-impl --hook-type pre-commit --config .pre-commit-config.yaml > /dev/null
        PRECOMMIT_STATUS=$?
        if [ $PRECOMMIT_STATUS -eq 0 ]; then
            log_message "SUCCESS" "Pre-commit hooks are configured correctly."
        else
            log_message "WARNING" "Pre-commit hooks may not be installed or properly configured."
        fi
    else
        log_message "ERROR" "pre-commit is not installed or not in PATH."
    fi
else
    log_message "WARNING" "No .pre-commit-config.yaml file found. Version control checks are not configured."
fi

# Overall summary
log_message "INFO" "Diagnostic tests completed. Review the messages above for issues."

# Deactivate virtual environment if it was activated during this script
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
    log_message "INFO" "Virtual environment deactivated."
fi

# Simple recommendations based on diagnostics
echo ""
echo "-----------------------------------------------------------"
echo "Diagnostic Summary and Recommendations:"

# Check for serious issues - if any ERROR messages were found
if grep -q "\[ERROR\]" "${PROJECT_ROOT_DIR}/logs/diagnostics_$(date +"%Y%m%d_%H%M%S").log" 2>/dev/null; then
    log_message "WARNING" "Serious issues found. Address errors first."
    echo "1. Run: ./shell_scripts/setup_project.sh to fix environment issues"
    echo "2. Check for missing critical files and dependencies"
else
    log_message "SUCCESS" "No serious issues found. You're ready to proceed."
    echo "1. Run: ./shell_scripts/run_rtm.sh to test the main pipeline"
    echo "2. Consider installing any optional dependencies marked as warnings"
fi

echo "-----------------------------------------------------------"
