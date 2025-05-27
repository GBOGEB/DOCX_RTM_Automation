#!/usr/bin/env bash
set -e

# Determine script directory and project root
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." &>/dev/null && pwd)

echo "Current working directory: $(pwd)"
echo "Project root: $PROJECT_ROOT"
echo "Script directory: $SCRIPT_DIR"

# Configuration
CONFIG_DIR="$PROJECT_ROOT/config"
COMMON_PATHS_YAML="$CONFIG_DIR/common_paths.yaml" # Assuming common_paths.yaml is in project's config dir

INPUT_DIR_RELATIVE="input" # Relative to PROJECT_ROOT
OUTPUT_DIR_RELATIVE="output" # Relative to PROJECT_ROOT, can be changed to "output2" etc.

INPUT_DOCX_NAME="MASTER_1805_1144.docx"
OUTPUT_MD_NAME="MASTER_1805_1144.md"
OUTPUT_STRUCTURE_JSON_NAME="structure.json"

# --- Customizable section ---
# Set INPUT_BASE_DIR to allow inputs from sub-repositories or other locations
# For a sub-repository named 'my_sub_repo' containing its own 'input' folder:
# INPUT_BASE_DIR="$PROJECT_ROOT/my_sub_repo"
# INPUT_DOCX_PATH="$INPUT_BASE_DIR/$INPUT_DIR_RELATIVE/$INPUT_DOCX_NAME"

# Default: Input from project's input directory
INPUT_BASE_DIR="$PROJECT_ROOT"
INPUT_DOCX_PATH="$INPUT_BASE_DIR/$INPUT_DIR_RELATIVE/$INPUT_DOCX_NAME"

# Output directory (absolute path)
OUTPUT_DIR_ABSOLUTE="$PROJECT_ROOT/$OUTPUT_DIR_RELATIVE"
# --- End Customizable section ---


# Ensure output directory exists
mkdir -p "$OUTPUT_DIR_ABSOLUTE"
echo "Output directory: $OUTPUT_DIR_ABSOLUTE"


# Load Python executable from YAML
# This assumes common_paths.yaml exists and is structured correctly.
# A more robust solution might involve a small Python script to parse YAML if PYTHON_EXEC itself is complex.
if [ ! -f "$COMMON_PATHS_YAML" ]; then
    echo "Warning: $COMMON_PATHS_YAML not found. Using 'python3' as default."
    PYTHON_EXEC="python3"
else
    # Attempt to read python_executable. This requires 'yq' or similar, or a python helper.
    # Using python -c for simplicity, assuming basic YAML structure.
    PYTHON_EXEC=$(python3 -c "import yaml; print(yaml.safe_load(open('$COMMON_PATHS_YAML'))['python_executable'])" 2>/dev/null)
    if [ -z "$PYTHON_EXEC" ]; then
        echo "Warning: Could not read 'python_executable' from $COMMON_PATHS_YAML or it was empty. Using 'python3'."
        PYTHON_EXEC="python3"
    fi
fi

# Debug: Print the Python executable path
echo "Using Python executable: $PYTHON_EXEC"

# Install dependencies (from project root)
echo "Installing dependencies..."
cd "$PROJECT_ROOT" || exit 1
"$PYTHON_EXEC" -m pip install -r requirements.txt
cd "$SCRIPT_DIR" # Return to script directory or handle CWD as needed for subsequent commands

# Check if input DOCX exists
if [ ! -f "$INPUT_DOCX_PATH" ]; then
    echo "Error: Input DOCX file not found at $INPUT_DOCX_PATH"
    exit 1
fi
echo "Input DOCX: $INPUT_DOCX_PATH"

# Extract structure from DOCX using the main script (if it supports a direct structure dump)
# Assuming extract_structure.py is now part of docx_to_md_with_structure.py or similar
# If extract_structure.py is separate:
# echo "Extracting structure from DOCX..."
# "$PYTHON_EXEC" "$SCRIPT_DIR/extract_structure.py" "$INPUT_DOCX_PATH" > "$OUTPUT_DIR_ABSOLUTE/$OUTPUT_STRUCTURE_JSON_NAME"

# Convert DOCX to Markdown using the enhanced script
echo "Converting DOCX to Markdown and extracting structure..."
# Assuming docx_to_md_with_structure.py handles structure.txt output itself.
# The structure.json might be an intermediate from a lua filter, or a direct output.
# If structure.json is desired, the script needs an option for it.
# For now, focusing on the markdown and text structure output.
"$PYTHON_EXEC" "$SCRIPT_DIR/docx_to_md_with_structure.py" \
    "$INPUT_DOCX_PATH" \
    "$OUTPUT_DIR_ABSOLUTE/$OUTPUT_MD_NAME" \
    --structure "$OUTPUT_DIR_ABSOLUTE/document_structure.txt" \
    # Add --lua-filter if a specific one is needed and not default in the python script
    # --lua-filter "$CONFIG_DIR/structure_extraction.lua"

# If you still need a separate pandoc call for basic markdown:
# echo "Converting DOCX to Markdown (basic)..."
# pandoc -s "$INPUT_DOCX_PATH" -t markdown -o "$OUTPUT_DIR_ABSOLUTE/$OUTPUT_MD_NAME"

echo "Processing complete. Outputs are in $OUTPUT_DIR_ABSOLUTE"
