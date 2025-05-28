#!/bin/bash
# Shell helpers for bash environments (Git Bash, WSL, etc.)

# Function to convert Windows path to bash-compatible format
win_to_bash_path() {
    # Get path from argument or use pwd if none provided
    local path="${1:-$(pwd)}"

    # Convert backslashes to forward slashes
    path="${path//\\//}"

    # For absolute paths starting with drive letter
    if [[ $path =~ ^[A-Za-z]: ]]; then
        # Convert C: to /c
        drive_letter=$(echo "${path:0:1}" | tr '[:upper:]' '[:lower:]')
        path="/${drive_letter}${path:2}"
    fi

    echo "$path"
}

# Function to check project structure
check_project() {
    echo "Checking project structure..."

    # Check core directories
    for dir in "src" "agents" "config" "tests" "input" "output"; do
        if [ -d "$dir" ]; then
            echo "✓ Found $dir directory"
        else
            echo "✗ Missing $dir directory"
        fi
    done

    # Check core files
    for file in "run.sh" "setup_venv.sh" "pyproject.toml"; do
        if [ -f "$file" ]; then
            echo "✓ Found $file"
        else
            echo "✗ Missing $file"
        fi
    done
}

# Function to activate virtual environment
activate_venv() {
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate
        echo "Virtual environment activated."
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
        echo "Virtual environment activated."
    else
        echo "Virtual environment not found. Run setup_venv.sh first."
        return 1
    fi
}

# Function to print help
print_help() {
    echo "RTM Automation Shell Helpers"
    echo "============================"
    echo ""
    echo "Available functions:"
    echo "  win_to_bash_path [path]  - Convert Windows path to bash format"
    echo "  check_project            - Check project structure"
    echo "  activate_venv            - Activate virtual environment"
    echo ""
    echo "Usage:"
    echo "  source shell_helpers.sh"
    echo "  win_to_bash_path \"C:\\path\\to\\dir\""
}

# Print help message if sourced directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "This script should be sourced, not executed directly."
    echo "Try: source shell_helpers.sh"
    exit 1
fi

echo "Shell helpers loaded. Type 'print_help' for available commands."
