#!/usr/bin/env bash
set -e

# Debug: Print current working directory
echo "Current working directory: $(pwd)"

# Load Python executable from YAML
PYTHON_EXEC=$(python -c "import yaml; print(yaml.safe_load(open('C:/Users/gbonthuy/Downloads/sor_digital_twin_starter/config/common_paths.yaml'))['python_executable'])")

# Debug: Print the Python executable path
echo "Using Python executable: $PYTHON_EXEC"

# Install dependencies
echo "Installing dependencies..."
"$PYTHON_EXEC" -m pip install -r requirements.txt

# Extract structure from DOCX
echo "Extracting structure from DOCX..."
"$PYTHON_EXEC" scripts/extract_structure.py input/MASTER_1805_1144.docx > output/structure.json

# Convert DOCX to Markdown
echo "Converting DOCX to Markdown..."
pandoc -s input/MASTER_1805_1144.docx -t markdown -o output/MASTER_1805_1144.md
