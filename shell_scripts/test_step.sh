#!/bin/bash

# Script to test individual pipeline steps
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${PROJECT_ROOT}/shell_scripts/common_utils.sh"

# Check if virtual environment is active
if [ -d "${PROJECT_ROOT}/.venv" ]; then
  if [ -f "${PROJECT_ROOT}/.venv/Scripts/activate" ]; then
    source "${PROJECT_ROOT}/.venv/Scripts/activate"
    log_message "INFO" "Activated virtual environment (Windows)"
  elif [ -f "${PROJECT_ROOT}/.venv/bin/activate" ]; then
    source "${PROJECT_ROOT}/.venv/bin/activate"
    log_message "INFO" "Activated virtual environment (Unix)"
  fi
fi

# Function to display usage information
usage() {
  echo "Usage: $0 <step> [options]"
  echo ""
  echo "Test an individual pipeline step for RTM Automation."
  echo ""
  echo "Steps:"
  echo "  word_to_md         - Convert Word documents to Markdown"
  echo "  extract_outline    - Extract document outline from Markdown"
  echo "  extract_rtm        - Extract Requirements Traceability Matrix data"
  echo "  md_to_json_yaml    - Convert Markdown to JSON/YAML"
  echo "  sync_outline_files - Synchronize outline files across formats"
  echo ""
  echo "Options:"
  echo "  --input <path>    - Specify input file or directory"
  echo "  --output <path>   - Specify output file or directory"
  echo "  --config <path>   - Specify config file path"
  echo "  --verbose, -v     - Enable verbose output"
  echo "  --help, -h        - Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 word_to_md --input input/document.docx --output output/document.md"
  echo "  $0 extract_rtm --input output/document.md --verbose"
  echo ""
}

# Check if a step name was provided
if [ $# -eq 0 ]; then
  usage
  exit 1
fi

# Get the step name
STEP="$1"
shift

# Call the Python test script with all arguments
log_message "INFO" "Testing pipeline step: $STEP"
python "${PROJECT_ROOT}/test_step.py" "$STEP" "$@"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  log_message "SUCCESS" "Step '$STEP' completed successfully"
else
  log_message "ERROR" "Step '$STEP' failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE
