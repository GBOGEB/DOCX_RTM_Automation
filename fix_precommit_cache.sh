#!/bin/bash
# Fix pre-commit cache issues for bash environments

echo "===================================="
echo "Pre-commit Cache Fix Tool"
echo "===================================="
echo

# Define the problematic cache directories
USER_CACHE_DIR="$HOME/new-pre-commit-cache"
PROJECT_CACHE_DIR="$(pwd)/.pre-commit-cache"

echo "Current pre-commit cache directories:"
echo "- User cache: $USER_CACHE_DIR"
echo "- Project cache: $PROJECT_CACHE_DIR"
echo

echo "Step 1: Cleaning up existing cache directories..."

# Check if the user cache directory exists
if [ -d "$USER_CACHE_DIR" ]; then
    echo "Found user cache directory, removing..."
    rm -rf "$USER_CACHE_DIR" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "WARNING: Unable to remove $USER_CACHE_DIR"
        echo "You may need to delete it manually."
    else
        echo "User cache directory removed successfully."
    fi
else
    echo "User cache directory not found."
fi

# Check if the project cache directory exists
if [ -d "$PROJECT_CACHE_DIR" ]; then
    echo "Found project cache directory, removing..."
    rm -rf "$PROJECT_CACHE_DIR" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "WARNING: Unable to remove $PROJECT_CACHE_DIR"
        echo "You may need to delete it manually."
    else
        echo "Project cache directory removed successfully."
    fi
else
    echo "Project cache directory not found."
fi

echo
echo "Step 2: Configuring pre-commit to use project-local cache..."

# Create .pre-commit-config.yaml if it doesn't exist
if [ ! -f ".pre-commit-config.yaml" ]; then
    echo ".pre-commit-config.yaml not found, creating basic configuration..."
    cat > .pre-commit-config.yaml << EOL
# Pre-commit Git hooks configuration
# See https://pre-commit.com for more information

repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
EOL
fi

# Create a pre-commit environment file to use local cache
echo "PRE_COMMIT_HOME=$(pwd)/.pre-commit-cache" > .env
echo "Created .env file with local cache configuration."

echo
echo "Step 3: Testing pre-commit setup..."

# Check if Python is available
if command -v python &> /dev/null; then
    echo "Python found, checking pre-commit installation..."

    # Check if pre-commit is installed
    if python -m pip show pre-commit &> /dev/null; then
        echo "Pre-commit is installed, running pre-commit clean..."
        python -m pre-commit clean

        echo
        echo "Installing pre-commit hooks..."
        python -m pre-commit install

        echo
        echo "Testing pre-commit autoupdate..."
        python -m pre-commit autoupdate
    else
        echo "Pre-commit not installed. Installing..."
        python -m pip install pre-commit

        echo
        echo "Installing pre-commit hooks..."
        python -m pre-commit install
    fi
else
    echo "Python not found. Please install Python and pre-commit manually."
fi

echo
echo "Fix completed. You can now try running pre-commit again with:"
echo "  ./run_git_hook.sh pre-commit"
echo "  or"
echo "  ./.git/hooks/pre-commit"
echo
echo "If issues persist, try:"
echo "1. Setting environment variable: export PRE_COMMIT_HOME=$(pwd)/.pre-commit-cache"
echo "2. Using 'pre-commit run --all-files' directly"
echo "3. Checking the log at $HOME/new-pre-commit-cache/pre-commit.log"
echo
