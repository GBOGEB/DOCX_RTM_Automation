#!/bin/bash
# Navigation helper for Bash environments (Git Bash, WSL, etc.)

# Check if this script is being run or sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "This script needs to be sourced, not executed."
    echo "Use: source bash_nav.sh"
    exit 1
fi

# Define project path
PROJECT_PATH="/c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0"

# Function to navigate to project directory
goto_project() {
    cd "$PROJECT_PATH" || return
    echo "Current directory: $(pwd)"
    echo "Available files and directories:"
    ls -la
}

# Function to show help
show_nav_help() {
    echo "==============================================="
    echo "DOCX RTM Automation Navigation Helper for Bash"
    echo "==============================================="
    echo ""
    echo "Available commands:"
    echo "  goto_project    - Navigate to project directory"
    echo "  show_nav_help   - Show this help information"
    echo ""
    echo "Example usage:"
    echo "  $ source bash_nav.sh"
    echo "  $ goto_project"
    echo ""
    echo "Project path: $PROJECT_PATH"
}

# Display initial help
show_nav_help
echo ""
echo "Type 'goto_project' to navigate to the project directory."
