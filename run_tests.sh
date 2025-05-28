#!/bin/bash

# Set up environment variables
export PYTHONPATH=$(pwd)
echo "Setting up test environment..."

# Check for pytest installation
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest is not installed. Installing..."
    pip install pytest
fi

# Install project dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing project dependencies..."
    pip install -r requirements.txt
fi

# Create test directory if it doesn't exist
if [ ! -d "tests" ]; then
    echo "Creating tests directory..."
    mkdir -p tests
    touch tests/__init__.py
fi

# Discover and run all tests
echo "Running tests..."
python -m pytest tests/ -v

# Optional: Run specific test modules if needed
# python -m pytest tests/test_docx_parser.py -v
# python -m pytest tests/test_md_converter.py -v

# Report results
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "Tests completed successfully."
else
    echo "Tests failed with exit code $exit_code."
fi

exit $exit_code
