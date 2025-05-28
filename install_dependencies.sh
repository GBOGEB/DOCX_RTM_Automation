#!/bin/bash

echo "Installing project dependencies..."

# Install base requirements
pip install pytest pyyaml docx2python markdown rich lxml

# Install additional development dependencies
pip install flake8 black isort mypy pytest-cov pylint

# Generate requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "Generating requirements.txt..."
    pip freeze > requirements.txt
    echo "requirements.txt created."
fi

echo "Dependencies installed successfully."

# Check if src directory exists, create if not
if [ ! -d "src" ]; then
    echo "Creating project structure..."
    mkdir -p src/core src/utils tests
    touch src/__init__.py src/core/__init__.py src/utils/__init__.py tests/__init__.py
    echo "Project structure created."
fi

echo "Setup completed."