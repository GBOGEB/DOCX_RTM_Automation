#!/bin/bash
# This script creates the necessary project structure

# Create directories
mkdir -p input output logs
mkdir -p agents/models pipelines/processors
mkdir -p scripts/modules

# Create necessary __init__.py files (if not already created)
touch __init__.py
touch config/__init__.py
touch utils/__init__.py
touch agents/__init__.py
touch agents/models/__init__.py
touch pipelines/__init__.py
touch pipelines/processors/__init__.py
touch scripts/__init__.py
touch scripts/modules/__init__.py

# Ensure output directory exists for examples to work
mkdir -p output
