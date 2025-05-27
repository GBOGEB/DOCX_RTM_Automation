#!/bin/bash

# This script provides functions to capture and format problems/errors

# Capture the last error and format it as a comment
function capture_last_error() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "# Error (code $exit_code): $BASH_COMMAND"
    fi
}

# Set this as a trap to automatically capture errors
trap 'capture_last_error' ERR

# Run a command and capture its output and errors
function run_and_capture() {
    local output_file="$(mktemp)"

    echo "# Running: $@"
    "$@" > "$output_file" 2>&1
    local exit_code=$?

    if [ $exit_code -ne 0 ]; then
        echo "# Command failed with exit code $exit_code:"
        cat "$output_file" | sed 's/^/# /'
    else
        echo "# Command succeeded"
    fi

    rm -f "$output_file"
    return $exit_code
}

# Copy last command output to clipboard with proper formatting
function copy_last_output() {
    local last_command=$(history | tail -n 2 | head -n 1 | sed 's/^[ ]*[0-9]\+[ ]*//')
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "cygwin"* ]] || [[ "$OSTYPE" == "msys"* ]]; then
        # Check if WSL and use clip.exe if possible, otherwise xclip
        if grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null && command -v clip.exe &> /dev/null; then
            echo "$last_command" | clip.exe
            echo "Last command copied to Windows clipboard via clip.exe"
        elif command -v xclip &> /dev/null; then
            echo "$last_command" | xclip -selection clipboard
            echo "Last command copied to clipboard via xclip"
        else
            echo "Clipboard utility (xclip or clip.exe) not found."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "$last_command" | pbcopy
        echo "Last command copied to clipboard via pbcopy"
    else
        echo "Unsupported OS for clipboard operation in this script."
    fi
}

# Example usage:
# run_and_capture python scripts/SRC_Master.py pipeline