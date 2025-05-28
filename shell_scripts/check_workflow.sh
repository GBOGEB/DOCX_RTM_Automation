#!/bin/bash

# Script to check RTM workflow execution paths and status
# Usage: ./check_workflow.sh [--verbose] [workflow_name]

# Get project root directory
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Source common utilities if available
if [ -f "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh" ]; then
    source "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh"
else
    # Define minimal versions of logging functions if common_utils.sh isn't available
    log_message() {
        local level="$1"
        local message="$2"
        echo "[$level] $message"
    }
    command_exists() {
        command -v "$1" >/dev/null 2>&1
    }
fi

# Process arguments
VERBOSE=false
WORKFLOW_NAME=""

usage() {
    echo "Usage: $0 [--verbose] [workflow_name]"
    echo ""
    echo "Options:"
    echo "  --verbose       Display more detailed information"
    echo "  workflow_name   Check a specific workflow by name (e.g., 'rtm', 'setup')"
    echo ""
    echo "Examples:"
    echo "  $0                    # Basic check of all workflows"
    echo "  $0 --verbose          # Detailed check of all workflows"
    echo "  $0 rtm                # Check only the RTM workflow"
    echo "  $0 --verbose setup    # Detailed check of the setup workflow"
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            usage
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        -*)
            log_message "ERROR" "Unknown option: $1"
            usage
            ;;
        *)
            if [ -z "$WORKFLOW_NAME" ]; then
                WORKFLOW_NAME="$1"
            else
                log_message "ERROR" "Too many arguments: $1"
                usage
            fi
            shift
            ;;
    esac
done

log_message "INFO" "Checking RTM workflow execution paths..."

if [ -n "$WORKFLOW_NAME" ]; then
    log_message "INFO" "Focusing on workflow: $WORKFLOW_NAME"
fi

# Check for critical files and directories
log_message "INFO" "Checking critical files and directories..."

CRITICAL_COMPONENTS=(
  "code/main.py"
  "shell_scripts/run_rtm.sh"
  "config/paths.yaml"
  "output"
  "logs"
)

ALL_COMPONENTS_FOUND=true
for component in "${CRITICAL_COMPONENTS[@]}"; do
    # Skip components that don't match the specified workflow
    if [ -n "$WORKFLOW_NAME" ]; then
        if [[ "$component" != *"$WORKFLOW_NAME"* ]] && [[ "$WORKFLOW_NAME" != "all" ]]; then
            continue
        fi
    fi

    if [ -e "${PROJECT_ROOT_DIR}/${component}" ]; then
        if [ -f "${PROJECT_ROOT_DIR}/${component}" ]; then
            log_message "SUCCESS" "Found file: ${component}"
            if [ "$VERBOSE" = true ]; then
                log_message "INFO" "File details: $(ls -la ${PROJECT_ROOT_DIR}/${component})"

                # For shell scripts, check if they're executable
                if [[ "$component" == *.sh ]]; then
                    if [ -x "${PROJECT_ROOT_DIR}/${component}" ]; then
                        log_message "SUCCESS" "File is executable: ${component}"
                    else
                        log_message "WARNING" "File is not executable: ${component}"
                        log_message "INFO" "Consider running: chmod +x ${PROJECT_ROOT_DIR}/${component}"
                    fi
                fi
            fi
        elif [ -d "${PROJECT_ROOT_DIR}/${component}" ]; then
            log_message "SUCCESS" "Found directory: ${component}"
            if [ "$VERBOSE" = true ]; then
                log_message "INFO" "Directory contents: $(ls -la ${PROJECT_ROOT_DIR}/${component} | head -5)"
                if [ "$(ls -1 ${PROJECT_ROOT_DIR}/${component} | wc -l)" -gt 5 ]; then
                    log_message "INFO" "... and $(expr $(ls -1 ${PROJECT_ROOT_DIR}/${component} | wc -l) - 5) more files"
                fi
            fi
        fi
    else
        log_message "ERROR" "Missing component: ${component}"
        ALL_COMPONENTS_FOUND=false
    fi
done

# Check Python virtual environment
if [ -d "${PROJECT_ROOT_DIR}/.venv" ]; then
    log_message "SUCCESS" "Python virtual environment found"
    if [ -f "${PROJECT_ROOT_DIR}/.venv/Scripts/activate" ]; then
        log_message "INFO" "Windows-style activation script present"

        # If verbose, check if environment is activated
        if [ "$VERBOSE" = true ]; then
            if [[ "$VIRTUAL_ENV" == *".venv"* ]]; then
                log_message "SUCCESS" "Virtual environment is currently activated"
            else
                log_message "INFO" "Virtual environment is not currently activated"
                log_message "INFO" "To activate: source ${PROJECT_ROOT_DIR}/.venv/Scripts/activate"
            fi
        fi
    elif [ -f "${PROJECT_ROOT_DIR}/.venv/bin/activate" ]; then
        log_message "INFO" "Unix-style activation script present"

        # If verbose, check if environment is activated
        if [ "$VERBOSE" = true ]; then
            if [[ "$VIRTUAL_ENV" == *".venv"* ]]; then
                log_message "SUCCESS" "Virtual environment is currently activated"
            else
                log_message "INFO" "Virtual environment is not currently activated"
                log_message "INFO" "To activate: source ${PROJECT_ROOT_DIR}/.venv/bin/activate"
            fi
        fi
    else
        log_message "WARNING" "Virtual environment exists but activation script not found"
    fi
else
    log_message "WARNING" "Python virtual environment not found"
    log_message "INFO" "Consider running: ${PROJECT_ROOT_DIR}/shell_scripts/setup_project.sh"
fi

# Check for recent logs
if [ -d "${PROJECT_ROOT_DIR}/logs" ]; then
    # Use a wildcard to be more inclusive of different log file extensions
    RECENT_LOGS=$(find "${PROJECT_ROOT_DIR}/logs" -type f -name "*.*" -mtime -1 2>/dev/null | wc -l)

    if [ "$RECENT_LOGS" -gt 0 ]; then
        log_message "INFO" "Found ${RECENT_LOGS} log files from the last 24 hours"

        # Try to find the latest log file regardless of extension
        LATEST_LOG=$(find "${PROJECT_ROOT_DIR}/logs" -type f -name "*.*" -printf "%T@ %p\n" 2>/dev/null | sort -n | tail -1 | cut -f2- -d" ")

        if [ -n "$LATEST_LOG" ]; then  # Check if LATEST_LOG is not empty
            log_message "INFO" "Latest log file: $(basename "$LATEST_LOG")"

            if [ "$VERBOSE" = true ] && [ -f "$LATEST_LOG" ]; then
                log_message "INFO" "Last 5 lines of the latest log:"
                tail -5 "$LATEST_LOG" | while read -r line; do
                    echo "    $line"
                done
            fi
        else
            log_message "WARNING" "Could not determine latest log file"
        fi
    else
        log_message "WARNING" "No recent log files found"
    fi
else
    log_message "WARNING" "Logs directory not found"
fi

# Check for recent output files
if [ -d "${PROJECT_ROOT_DIR}/output" ]; then
    RECENT_OUTPUT=$(find "${PROJECT_ROOT_DIR}/output" -type f -mtime -1 2>/dev/null | wc -l)
    if [ "$RECENT_OUTPUT" -gt 0 ]; then
        log_message "INFO" "Found ${RECENT_OUTPUT} output files from the last 24 hours"
        LATEST_OUTPUT=$(find "${PROJECT_ROOT_DIR}/output" -type f -printf "%T@ %p\n" 2>/dev/null | sort -n | tail -1 | cut -f2- -d" ")
        if [ -n "$LATEST_OUTPUT" ]; then  # Check if LATEST_OUTPUT is not empty
            log_message "INFO" "Latest output file: $(basename "$LATEST_OUTPUT")"

            # If verbose and the file isn't too large, show a preview
            if [ "$VERBOSE" = true ] && [ -f "$LATEST_OUTPUT" ]; then
                FILE_SIZE=$(du -k "$LATEST_OUTPUT" | cut -f1)
                if [ "$FILE_SIZE" -lt 10 ]; then  # Only preview files smaller than 10KB
                    log_message "INFO" "Preview of latest output file:"
                    echo "----------------------------------------"
                    head -10 "$LATEST_OUTPUT"  # Show first 10 lines
                    echo "----------------------------------------"
                else
                    log_message "INFO" "Output file is too large to preview (${FILE_SIZE}KB)"
                fi
            fi
        else
            log_message "WARNING" "Could not determine latest output file"
        fi
    else
        log_message "WARNING" "No recent output files found"
    fi
else
    log_message "WARNING" "Output directory not found"
fi

# Summary
log_message "INFO" "Workflow environment check complete"
if [ "$ALL_COMPONENTS_FOUND" = true ]; then
    log_message "SUCCESS" "All critical components are present"
    log_message "INFO" "You can run the RTM workflow using:"
    log_message "INFO" "  ./shell_scripts/run_rtm.sh"
else
    log_message "WARNING" "Some critical components are missing"
    log_message "INFO" "Review the errors above and reinstall or fix the missing components"
fi

# Show execution commands
log_message "INFO" "Available command options:"
echo ""
echo "  Run main RTM workflow:"
echo "    ./shell_scripts/run_rtm.sh"
echo ""
echo "  Run diagnostics:"
echo "    ./shell_scripts/run_diagnostics.sh"
echo ""
echo "  Run main Python script directly:"
echo "    python code/main.py"
echo ""
echo "  Run with VS Code debugger:"
echo "    1. Open VS Code"
echo "    2. Press F5"
echo "    3. Select 'Python: Main Script'"
echo ""

if [ -f "${PROJECT_ROOT_DIR}/docs/workflow_execution_guide.md" ]; then
    log_message "INFO" "For more detailed instructions, see:"
    log_message "INFO" "  ${PROJECT_ROOT_DIR}/docs/workflow_execution_guide.md"
fi