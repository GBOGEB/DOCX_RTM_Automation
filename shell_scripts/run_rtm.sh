#!/bin/bash

# Script: run_rtm.sh
# Description: Main execution script for the RTM Automation process.
# It activates a virtual environment (if specified) and runs the main Python application.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
# Project root directory (assuming this script is in shell_scripts/ at the project root)
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_MAIN_SCRIPT="${PROJECT_ROOT_DIR}/code/main.py"
VENV_PATH="${PROJECT_ROOT_DIR}/.venv" # Path to your virtual environment

# --- Helper Functions ---
log_info() {
  echo "[INFO] $(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
  echo "[ERROR] $(date +'%Y-%m-%d %H:%M:%S') - $1" >&2
}

log_warning() {
  echo "[WARNING] $(date +'%Y-%m-%d %H:%M:%S') - $1"
}

# --- Main Logic ---
log_info "Starting RTM automation process from run_rtm.sh..."
cd "$PROJECT_ROOT_DIR" # Ensure we are in the project root

# Activate virtual environment if it exists
if [ -d "$VENV_PATH" ]; then
  log_info "Activating virtual environment at $VENV_PATH..."
  # shellcheck source=/dev/null
  if [ -f "$VENV_PATH/bin/activate" ]; then # Linux/macOS
    source "$VENV_PATH/bin/activate"
    log_info "Virtual environment activated (Unix style)."
  elif [ -f "$VENV_PATH/Scripts/activate" ]; then # Windows (Git Bash)
    source "$VENV_PATH/Scripts/activate"
    log_info "Virtual environment activated (Windows style)."
  else
    log_warning "Activation script not found in $VENV_PATH/bin/ or $VENV_PATH/Scripts/. Attempting to proceed without venv."
    # Optionally, exit if venv is critical
    # log_error "Critical: Could not activate virtual environment."
    # exit 1
  fi
else
  log_warning "Virtual environment directory not found at $VENV_PATH. Running with system Python."
  # Consider exiting if venv is mandatory:
  # log_error "Virtual environment is required. Please run setup_project.sh first."
  # exit 1
fi

# Check if the main Python script exists
if [ ! -f "$PYTHON_MAIN_SCRIPT" ]; then
    log_error "Main Python script not found at $PYTHON_MAIN_SCRIPT"
    exit 1
fi

log_info "Executing Python application: $PYTHON_MAIN_SCRIPT"
# Pass all arguments received by this shell script to the Python script
python "$PYTHON_MAIN_SCRIPT" "$@"

# Check the exit status of the Python script
exit_status=$?
if [ $exit_status -eq 0 ]; then
    log_info "RTM automation Python script completed successfully."
else
    log_error "RTM automation Python script failed with exit code $exit_status."
    exit $exit_status
fi

# Deactivate virtual environment (optional, script exit will handle it)
# if [ -d "$VENV_PATH" ] && type deactivate &>/dev/null; then
#   deactivate
#   log_info "Virtual environment deactivated."
# fi

log_info "run_rtm.sh finished."