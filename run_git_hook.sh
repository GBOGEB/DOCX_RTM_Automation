#!/bin/bash
# Helper script for running Git hooks in different environments

# Function to help run git hooks correctly
run_git_hook() {
    local hook_name="$1"

    # Check if .git directory exists
    if [ ! -d ".git" ]; then
        echo "Error: Not in git repository root directory"
        echo "Please run this script from the root of your git repository"
        return 1
    fi

    # Check if hook exists
    if [ -f ".git/hooks/$hook_name" ]; then
        echo "Running $hook_name hook..."

        # Make sure the hook is executable
        chmod +x ".git/hooks/$hook_name"

        # Run the hook
        ".git/hooks/$hook_name"
        return $?
    else
        echo "Error: $hook_name hook not found"
        echo "Hook should be located at: .git/hooks/$hook_name"
        return 1
    fi
}

# Display help if no arguments
if [ -z "$1" ]; then
    echo "Git Hook Runner - Run Git hooks manually"
    echo ""
    echo "Usage: ./run_git_hook.sh HOOK_NAME"
    echo ""
    echo "Available hooks:"
    if [ -d ".git/hooks" ]; then
        for hook in .git/hooks/*; do
            if [ -f "$hook" ] && [ -x "$hook" ] && [ ! -f "$hook.sample" ]; then
                echo "  - $(basename "$hook")"
            fi
        done
    else
        echo "  No hooks available (.git/hooks directory not found)"
    fi
    echo ""
    echo "Examples:"
    echo "  ./run_git_hook.sh pre-commit"
    echo "  ./run_git_hook.sh post-commit"
    exit 0
fi

# Run the specified hook
run_git_hook "$1"
exit $?
