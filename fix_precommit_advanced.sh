#!/bin/bash
# shellcheck shell=bash
# Advanced pre-commit hook fixer

echo "Fixing pre-commit hooks and shell script issues..."

# Fix line endings
if command -v dos2unix >/dev/null 2>&1; then
    echo "Using dos2unix to fix line endings..."
    find . -name "*.sh" -exec dos2unix {} \;
    find .git/hooks -type f -exec dos2unix {} \; 2>/dev/null || true
else
    echo "dos2unix not found, using sed..."
    find . -name "*.sh" -exec sed -i 's/\r$//' {} \;
    find .git/hooks -type f -exec sed -i 's/\r$//' {} \; 2>/dev/null || true
fi

# Make scripts executable
chmod +x *.sh 2>/dev/null || true
chmod +x .git/hooks/* 2>/dev/null || true

# Fix Git configuration
git config core.autocrlf input
git config core.eol lf

echo "Pre-commit fixes completed."
