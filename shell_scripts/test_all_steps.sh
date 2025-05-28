#!/bin/bash

# Script to test all RTM pipeline steps in sequence
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${PROJECT_ROOT}/shell_scripts/common_utils.sh"

# Activate virtual environment if available
if [ -d "${PROJECT_ROOT}/.venv" ]; then
  if [ -f "${PROJECT_ROOT}/.venv/Scripts/activate" ]; then
    source "${PROJECT_ROOT}/.venv/Scripts/activate"
    log_message "INFO" "Activated virtual environment (Windows)"
  elif [ -f "${PROJECT_ROOT}/.venv/bin/activate" ]; then
    source "${PROJECT_ROOT}/.venv/bin/activate"
    log_message "INFO" "Activated virtual environment (Unix)"
  fi
fi

# Ensure output directories exist
ensure_dir_exists "${PROJECT_ROOT}/output"
ensure_dir_exists "${PROJECT_ROOT}/output/rtm"

# Make sure we have a DOCX file in the input directory
SAMPLE_DOCX="${PROJECT_ROOT}/input/sample_document.docx"
if [ ! -f "$SAMPLE_DOCX" ]; then
  log_message "INFO" "Creating a sample DOCX in the input directory..."

  # Check if we have any DOCX files
  EXISTING_DOCX=$(find "${PROJECT_ROOT}/input" -name "*.docx" | head -1)

  if [ -n "$EXISTING_DOCX" ] && [[ ! "$EXISTING_DOCX" == *"~$"* ]]; then
    # Use an existing DOCX file
    SAMPLE_DOCX="$EXISTING_DOCX"
    log_message "INFO" "Using existing DOCX file: $SAMPLE_DOCX"
  else
    # Create a simple text file as a placeholder
    log_message "WARNING" "No suitable DOCX file found in the input directory."
    log_message "INFO" "Creating a placeholder text file instead."
    echo "This is a placeholder for a Word document." > "${PROJECT_ROOT}/input/sample_document.txt"
    log_message "INFO" "Created placeholder file. Tests will use Markdown files instead."

    # Create a sample Markdown file if none exists
    EXISTING_MD=$(find "${PROJECT_ROOT}/input" -name "*.md" | head -1)
    if [ -z "$EXISTING_MD" ]; then
      cat > "${PROJECT_ROOT}/input/sample_requirements.md" << 'EOF'
# Sample Requirements Document

## Introduction

This is a sample document for testing the RTM automation tool.

## Requirements

### REQ-001 - User Authentication
The system shall provide a secure authentication mechanism.

### REQ-002 - Data Storage
The system shall store data securely.

## Test Cases

### TC-001 - Verify Login
This test verifies user authentication.

### TC-002 - Verify Data Security
This test verifies data storage security.

## Traceability Links

[REQ-001] -> [TC-001]
[REQ-002] -> [TC-002]
EOF
      log_message "INFO" "Created sample Markdown file for testing"
    fi
  fi
fi

# Test each pipeline step in sequence

# Step 1: Word to Markdown
log_message "INFO" "===== Testing: word_to_md ====="
"${PROJECT_ROOT}/shell_scripts/test_step.sh" word_to_md
if [ $? -eq 0 ]; then
  log_message "SUCCESS" "word_to_md step passed"
else
  log_message "ERROR" "word_to_md step failed"
fi
echo

# Step 2: Extract Outline
log_message "INFO" "===== Testing: extract_outline ====="
"${PROJECT_ROOT}/shell_scripts/test_step.sh" extract_outline
if [ $? -eq 0 ]; then
  log_message "SUCCESS" "extract_outline step passed"
else
  log_message "ERROR" "extract_outline step failed"
fi
echo

# Step 3: Extract RTM
log_message "INFO" "===== Testing: extract_rtm ====="
"${PROJECT_ROOT}/shell_scripts/test_step.sh" extract_rtm
if [ $? -eq 0 ]; then
  log_message "SUCCESS" "extract_rtm step passed"
else
  log_message "ERROR" "extract_rtm step failed"
fi
echo

# Step 4: Markdown to JSON/YAML
log_message "INFO" "===== Testing: md_to_json_yaml ====="
"${PROJECT_ROOT}/shell_scripts/test_step.sh" md_to_json_yaml
if [ $? -eq 0 ]; then
  log_message "SUCCESS" "md_to_json_yaml step passed"
else
  log_message "ERROR" "md_to_json_yaml step failed"
fi
echo

# Step 5: Sync Outline Files
log_message "INFO" "===== Testing: sync_outline_files ====="
"${PROJECT_ROOT}/shell_scripts/test_step.sh" sync_outline_files
if [ $? -eq 0 ]; then
  log_message "SUCCESS" "sync_outline_files step passed"
else
  log_message "ERROR" "sync_outline_files step failed"
fi
echo

log_message "INFO" "All pipeline steps have been tested."

# Generate RTM status report
log_message "INFO" "Generating RTM status report..."
"${PROJECT_ROOT}/shell_scripts/rtm_status.sh" --full-report
if [ $? -eq 0 ]; then
  log_message "SUCCESS" "Status report generated successfully"
else
  log_message "ERROR" "Status report generation failed"
fi
echo

log_message "INFO" "Test sequence completed."
