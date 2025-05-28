#!/bin/bash

# Update script files to fix issues with Git Bash on Windows
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common utilities if available
if [ -f "${PROJECT_ROOT}/shell_scripts/common_utils.sh" ]; then
  source "${PROJECT_ROOT}/shell_scripts/common_utils.sh"
else
  # Define simple logging function
  log_message() {
    local level="$1"
    local message="$2"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message"
  }
fi

log_message "INFO" "Starting script updates..."

# Backup and replace the rtm_status.sh script
if [ -f "${PROJECT_ROOT}/shell_scripts/rtm_status.sh" ]; then
  log_message "INFO" "Backing up rtm_status.sh..."
  cp "${PROJECT_ROOT}/shell_scripts/rtm_status.sh" "${PROJECT_ROOT}/shell_scripts/rtm_status.sh.bak"

  log_message "INFO" "Replacing rtm_status.sh with fixed version..."
  cp "${PROJECT_ROOT}/shell_scripts/rtm_status_fixed.sh" "${PROJECT_ROOT}/shell_scripts/rtm_status.sh"
  chmod +x "${PROJECT_ROOT}/shell_scripts/rtm_status.sh"
  log_message "SUCCESS" "Updated rtm_status.sh"
else
  log_message "WARNING" "rtm_status.sh not found. Will create from fixed version."
  cp "${PROJECT_ROOT}/shell_scripts/rtm_status_fixed.sh" "${PROJECT_ROOT}/shell_scripts/rtm_status.sh"
  chmod +x "${PROJECT_ROOT}/shell_scripts/rtm_status.sh"
  log_message "SUCCESS" "Created rtm_status.sh from fixed version"
fi

# Make sure the run_rtm.sh exists and is executable
if [ ! -f "${PROJECT_ROOT}/shell_scripts/run_rtm.sh" ]; then
  log_message "WARNING" "run_rtm.sh not found. Creating basic version..."

  # Create a basic run_rtm.sh script
  cat > "${PROJECT_ROOT}/shell_scripts/run_rtm.sh" << 'EOF'
#!/bin/bash

# Script to run the RTM automation pipeline
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${PROJECT_ROOT}/shell_scripts/common_utils.sh"

log_message "INFO" "Starting RTM automation pipeline..."

# Activate virtual environment if it exists
if [ -d "${PROJECT_ROOT}/.venv" ]; then
  if [ -f "${PROJECT_ROOT}/.venv/Scripts/activate" ]; then
    log_message "INFO" "Activating Windows-style virtual environment..."
    source "${PROJECT_ROOT}/.venv/Scripts/activate"
  elif [ -f "${PROJECT_ROOT}/.venv/bin/activate" ]; then
    log_message "INFO" "Activating Unix-style virtual environment..."
    source "${PROJECT_ROOT}/.venv/bin/activate"
  else
    log_message "WARNING" "Virtual environment found but no activation script located"
  fi
fi

# Run the main script
MAIN_PY="${PROJECT_ROOT}/code/main.py"
if [ -f "$MAIN_PY" ]; then
  log_message "INFO" "Running main.py..."
  python "$MAIN_PY" "$@"
  EXIT_CODE=$?

  if [ $EXIT_CODE -eq 0 ]; then
    log_message "SUCCESS" "RTM automation completed successfully"
  else
    log_message "ERROR" "RTM automation failed with exit code $EXIT_CODE"
  fi
else
  log_message "ERROR" "Main script not found at $MAIN_PY"
  exit 1
fi

log_message "INFO" "RTM automation pipeline complete"
EOF

  chmod +x "${PROJECT_ROOT}/shell_scripts/run_rtm.sh"
  log_message "SUCCESS" "Created basic run_rtm.sh"
fi

# Create sample configuration for secrets section in paths.yaml
log_message "INFO" "Updating paths.yaml with secrets section..."
CONFIG_FILE="${PROJECT_ROOT}/config/paths.yaml"
if [ -f "$CONFIG_FILE" ]; then
  # Check if secrets section already exists
  if ! grep -q "secrets:" "$CONFIG_FILE"; then
    log_message "INFO" "Adding secrets section to paths.yaml..."
    cat >> "$CONFIG_FILE" << 'EOF'

# Secrets configuration (for main.py compatibility)
secrets:
  openai_key_path: "config/openai_key.txt"  # Path to OpenAI API key file
EOF
    log_message "SUCCESS" "Added secrets section to paths.yaml"
  else
    log_message "INFO" "Secrets section already exists in paths.yaml"
  fi
else
  log_message "ERROR" "Configuration file not found at $CONFIG_FILE"
fi

# Make shell scripts executable
log_message "INFO" "Making all shell scripts executable..."
find "${PROJECT_ROOT}/shell_scripts" -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
chmod +x "${PROJECT_ROOT}"/*.sh 2>/dev/null || true
log_message "SUCCESS" "All shell scripts should now be executable"

# Create a test input file if none exists
if [ "$(find "${PROJECT_ROOT}/input" -name "*.md" | wc -l)" -eq 0 ]; then
  log_message "INFO" "Creating sample input Markdown file..."

  mkdir -p "${PROJECT_ROOT}/input"
  cat > "${PROJECT_ROOT}/input/sample_requirements.md" << 'EOF'
# Sample Requirements Document

## Introduction

This is a sample document containing requirements and test cases for demonstrating the RTM automation tool.

## Requirements

### REQ-001 - User Authentication
The system shall provide a secure authentication mechanism for users.

### REQ-002 - Data Storage
The system shall store user data securely in an encrypted database.

### REQ-003 - Password Rules
The system shall enforce password complexity rules (minimum 8 characters, at least one uppercase, one lowercase, one number).

## Test Cases

### TC-001 - Verify User Login
This test verifies that users can log in with valid credentials.

### TC-002 - Verify Password Validation
This test checks that password complexity rules are enforced.

### TC-003 - Verify Data Encryption
This test ensures that user data is properly encrypted in the database.

## Traceability Links

[REQ-001] -> [TC-001]
[REQ-003] -> [TC-002]
[REQ-002] -> [TC-003]
EOF

  log_message "SUCCESS" "Created sample input file at ${PROJECT_ROOT}/input/sample_requirements.md"
fi

log_message "SUCCESS" "Script updates completed"
log_message "INFO" "Next steps:"
log_message "INFO" "1. Run ./shell_scripts/rtm_status.sh --verbose"
log_message "INFO" "2. Verify that all is working correctly"
log_message "INFO" "3. Run ./shell_scripts/run_rtm.sh to test the full pipeline"
