#!/bin/bash
# Helper script for file operations in Bash environments

# Function to rename files (like Windows' 'ren' command)
bash_rename() {
    if [ $# -ne 2 ]; then
        echo "Usage: bash_rename SOURCE_FILE TARGET_FILE"
        return 1
    fi

    source_file="$1"
    target_file="$2"

    if [ ! -e "$source_file" ]; then
        echo "Error: Source file '$source_file' not found."
        return 1
    fi

    mv -v "$source_file" "$target_file"
    return $?
}

# Function to copy files (like Windows' 'copy' command)
bash_copy() {
    if [ $# -lt 2 ]; then
        echo "Usage: bash_copy SOURCE_FILE TARGET_FILE_OR_DIR"
        return 1
    fi

    source_file="$1"
    target="$2"

    if [ ! -e "$source_file" ]; then
        echo "Error: Source file '$source_file' not found."
        return 1
    fi

    cp -v "$source_file" "$target"
    return $?
}

# Function to list files with Windows-like syntax
bash_dir() {
    directory="${1:-.}"

    if [ ! -d "$directory" ]; then
        echo "Error: Directory '$directory' not found."
        return 1
    fi

    echo "Directory of $(realpath "$directory")"
    echo ""

    ls -la "$directory"
    return $?
}

# Show usage information
echo "File operation helpers for Bash environments"
echo ""
echo "Available commands:"
echo "  bash_rename SOURCE TARGET  - Rename a file (like Windows 'ren')"
echo "  bash_copy SOURCE TARGET    - Copy a file (like Windows 'copy')"
echo "  bash_dir [DIRECTORY]       - List files in directory (like Windows 'dir')"
echo ""
echo "Example usage:"
echo "  bash_rename \"@echo off.bat\" \"run_git_hook.bat\""
echo ""
