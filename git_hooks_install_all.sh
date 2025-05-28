#!/bin/bash
# Comprehensive Git hooks installer for Bash environments

echo "======================================"
echo " RTM Automation Git Hooks Installer"
echo "======================================"
echo

# Check if we're in a Git repository
if [ ! -d ".git" ]; then
    echo "Error: Not in a Git repository root directory"
    echo "Please run this script from the root of your project"
    exit 1
fi

# Ensure hooks directory exists
mkdir -p .git/hooks

# Define all available hooks
HOOKS=(
    "pre-commit"
    "post-commit"
    "pre-push"
    "post-merge"
)

# Install each available hook
for hook in "${HOOKS[@]}"; do
    if [ -f "$hook" ]; then
        echo "Installing $hook hook..."
        cp "$hook" ".git/hooks/$hook"
        chmod +x ".git/hooks/$hook"
        echo "✓ $hook installed"
    else
        echo "⚠ $hook file not found, skipping"
    fi
done

# Check for pre-commit framework
if command -v pre-commit &> /dev/null; then
    echo
    echo "pre-commit framework detected"
    if [ -f ".pre-commit-config.yaml" ]; then
        echo "Installing pre-commit framework hooks..."
        pre-commit install
        echo "✓ pre-commit framework hooks installed"
    else
        echo "⚠ .pre-commit-config.yaml not found, skipping framework install"
    fi
else
    echo
    echo "⚠ pre-commit framework not installed"
    echo "To install: pip install pre-commit"
fi

echo
echo "Installation complete!"
echo "Run './run_git_hook.sh pre-commit' to test the pre-commit hook"
echo
