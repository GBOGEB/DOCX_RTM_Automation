#!/bin/bash

echo "Running linters and code quality checks..."

# Check for required tools
for tool in flake8 black isort mypy pylint; do
    if ! command -v $tool &> /dev/null; then
        echo "Installing $tool..."
        pip install $tool
    fi
done

# Run Black formatter
echo "Running Black formatter..."
black src tests

# Run isort
echo "Running isort..."
isort src tests

# Run flake8
echo "Running flake8..."
flake8 src tests

# Run mypy type checking
echo "Running mypy type checking..."
mypy src

# Run pylint
echo "Running pylint..."
pylint --recursive=y src

echo "Code quality checks completed."

# Fix for md_to_json_yaml.py missing dependencies
if grep -q "import glob" /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/src/core/md_to_json_yaml.py; then
    echo "glob import exists in md_to_json_yaml.py"
else
    echo "Adding missing glob import to md_to_json_yaml.py"
    sed -i '1,10s/import os/import os\nimport glob/' /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/src/core/md_to_json_yaml.py
fi

# Fix output_path issue in md_to_json_yaml.py
if grep -q "output_path = " /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/src/core/md_to_json_yaml.py; then
    echo "output_path variable exists, not making changes"
else
    echo "Fixing the output_path issue in md_to_json_yaml.py"
    sed -i 's/    output_dir = md_path.parent if output_file is None else Path(output_file).parent\n        output_stem = output_path.stem\n        output_dir = output_path.parent/    output_dir = md_path.parent if output_file is None else Path(output_file).parent/' /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/src/core/md_to_json_yaml.py
fi
