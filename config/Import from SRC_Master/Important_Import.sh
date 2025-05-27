#!/bin/bash
# File: scripts/setup_project.sh
# Make sure to run this script from the directory where you'd like to create "my_new_repo"

set -euo pipefail # Exit on error, undefined variable, or pipe failure

PROJECT_NAME="${1:-my_new_repo}" # Use first argument as project name, or default

# Define directories
SRC_DIR="$PROJECT_NAME/src"
DOCUMENT_PROCESSING_DIR="$SRC_DIR/document_processing"
UTILS_DIR="$SRC_DIR/utils"
TESTS_DIR="$PROJECT_NAME/tests"
SCRIPTS_DIR="$PROJECT_NAME/scripts"

echo "Creating project structure for '$PROJECT_NAME'..."

# Create directory structure
mkdir -p "$DOCUMENT_PROCESSING_DIR" "$UTILS_DIR" "$TESTS_DIR" "$SCRIPTS_DIR"

# Create __init__.py files to make directories Python packages
touch "$SRC_DIR/__init__.py"
touch "$DOCUMENT_PROCESSING_DIR/__init__.py"
touch "$UTILS_DIR/__init__.py"

# Create document_processing module files
echo "Creating document processing modules..."
cat > "$DOCUMENT_PROCESSING_DIR/extract.py" << 'EOF'
"""
Module: extract.py
Renamed from extract_take2.py
Handles extraction of requirements and other data from documents.
"""
def extract_data(document_path):
    """
    Extracts structured data from the given document.
    Placeholder for actual extraction logic.
    """
    print(f"Attempting to extract data from: {document_path}")
    # TODO: implement extraction logic (e.g., using python-docx)
    return {"data": "example"}
EOF

cat > "$DOCUMENT_PROCESSING_DIR/word_to_md.py" << 'EOF'
"""
Module: word_to_md.py
Fixed version: converts Word documents to Markdown.
Relies on Pandoc being installed on the system.
"""
import subprocess

def convert_word_to_md(word_file_path, output_md_path):
    """
    Converts a Word document (.docx) to Markdown (.md) using Pandoc.
    """
    try:
        subprocess.run(
            ["pandoc", word_file_path, "-o", output_md_path, "--from=docx", "--to=markdown-strict"],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"Successfully converted '{word_file_path}' to '{output_md_path}'")
    except FileNotFoundError:
        print("Error: Pandoc not found. Please ensure Pandoc is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Pandoc conversion: {e}")
        print(f"Pandoc stdout: {e.stdout}")
        print(f"Pandoc stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
EOF

# Create utils module files
echo "Creating utility modules..."
cat > "$UTILS_DIR/pandoc_integration.py" << 'EOF'
"""
Module: pandoc_integration.py
Integrates with Pandoc for document conversions using various filters.
"""
import subprocess

def convert_with_pandoc(input_file, output_file, lua_filter=None):
    """
    Converts a document using Pandoc, optionally applying a Lua filter.
    """
    command = ["pandoc", input_file, "-o", output_file]
    if lua_filter:
        command.extend(["--lua-filter", lua_filter])

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully converted '{input_file}' to '{output_file}' using Pandoc.")
    except FileNotFoundError:
        print("Error: Pandoc not found. Please ensure Pandoc is installed and in your system's PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Pandoc conversion: {e}")
        print(f"Pandoc stdout: {e.stdout}")
        print(f"Pandoc stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
EOF

cat > "$UTILS_DIR/markdown_lint.py" << 'EOF'
"""
Module: markdown_lint.py
Lints Markdown files using Ruff (if configured for Markdown).
Alternatively, can integrate with other Markdown linters.
"""
import subprocess

def lint_markdown_file(md_file_path):
    """
    Lints the specified Markdown file using Ruff.
    Note: Ruff's Markdown linting capabilities might be limited.
    Consider dedicated Markdown linters for more comprehensive checks.
    """
    try:
        # Ruff can be configured to check Markdown files, but it's primarily a Python linter.
        # For this example, we'll assume ruff is configured or we're just checking for general issues.
        result = subprocess.run(
            ["ruff", "check", md_file_path],
            check=False,  # Don't exit on linting errors, just report them
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Linting issues found in '{md_file_path}':\n{result.stdout}\n{result.stderr}")
        else:
            print(f"No linting issues found in '{md_file_path}' by Ruff.")
    except FileNotFoundError:
        print("Error: Ruff not found. Please ensure Ruff is installed and in your system's PATH.")
    except Exception as e:
        print(f"An unexpected error occurred during linting: {e}")
EOF

cat > "$UTILS_DIR/ascii_diagram.py" << 'EOF'
"""
Module: ascii_diagram.py
Generates ASCII diagrams from structured data.
"""
def generate_ascii_diagram(data, style="tree"):
    """
    Generates an ASCII diagram.
    Placeholder for actual diagram generation logic (e.g., using asciitree or similar).
    """
    print(f"Generating ASCII diagram for data with style: {style}")
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"+--{key}")
            if isinstance(value, (dict, list)):
                # Basic recursive print for demonstration
                # TODO: Implement proper ASCII tree generation
                print(f"|  +-- {value}")
    # TODO: create an ASCII diagram based on input data
    return "ASCII Diagram Placeholder"
EOF

# Create requirements.txt with dependencies
echo "Creating requirements.txt..."
cat > "$PROJECT_NAME/requirements.txt" << 'EOF'
# Core dependencies
python-docx
pyyaml
openai

# Linting
ruff

# Optional: if using pypandoc Python wrapper
# pypandoc
EOF

# Create a basic README.md
echo "Creating README.md..."
cat > "$PROJECT_NAME/README.md" << 'EOF'
# my_new_repo

This repository contains document processing utilities and integrations.

## Setup

1.  **Install Pandoc**: This project relies on Pandoc for some document conversions. Please install it from [pandoc.org](https://pandoc.org/installing.html).
2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    # .venv\Scripts\activate    # On Windows
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

(Add usage instructions here)

## Scripts

-   `scripts/github_push.sh`: Helper script to commit and push changes.
EOF

# Create a GitHub push helper script
echo "Creating helper scripts..."
cat > "$SCRIPTS_DIR/github_push.sh" << 'EOF'
#!/bin/bash
# Script: github_push.sh
# Commits and pushes changes to the GitHub repository.

# Check if inside a Git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "Error: Not inside a Git repository."
    exit 1
fi

# Check for uncommitted changes
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
    # Optionally, still push if there are unpushed commits
    # git push
    exit 0
fi

# Prompt for commit message
read -p "Enter commit message: " COMMIT_MESSAGE

if [ -z "$COMMIT_MESSAGE" ]; then
    COMMIT_MESSAGE="Automated commit: $(date)"
fi

git add .
git commit -m "$COMMIT_MESSAGE"

# Get current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Pushing to branch '$CURRENT_BRANCH'..."
git push origin "$CURRENT_BRANCH"

if [ $? -eq 0 ]; then
    echo "Successfully pushed to GitHub."
else
    echo "Error pushing to GitHub."
fi
EOF
chmod +x "$SCRIPTS_DIR/github_push.sh"

echo "Project structure for '$PROJECT_NAME' has been created successfully."
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
else
echo "2. Initialize Git repository: git init"
echo "3. Create a virtual environment and install requirements (see README.md)."
echo "4. Start developing!"
    echo "Error pushing to GitHub."
fi
EOF
chmod +x "$SCRIPTS_DIR/github_push.sh"

echo "Project structure for '$PROJECT_NAME' has been created successfully."
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
echo "2. Initialize Git repository: git init"
echo "3. Create a virtual environment and install requirements (see README.md)."
echo "4. Start developing!"