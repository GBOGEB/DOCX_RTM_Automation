#!/bin/bash

# Common shell utilities for RTM Automation processes

# Print a timestamped log message
log_message() {
  local level="$1"
  local message="$2"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  case "$level" in
    "INFO")
      # Blue text for info
      echo -e "[$timestamp] [INFO] $message"
      ;;
    "SUCCESS")
      # Green text for success
      echo -e "[$timestamp] [SUCCESS] $message"
      ;;
    "WARNING")
      # Yellow text for warnings
      echo -e "[$timestamp] [WARNING] $message"
      ;;
    "ERROR")
      # Red text for errors
      echo -e "[$timestamp] [ERROR] $message"
      ;;
    *)
      # Default for other levels
      echo "[$timestamp] [$level] $message"
      ;;
  esac
}

# Check if a command exists in path
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Get the absolute path to the project root directory
get_project_root() {
  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  echo "$(cd "$script_dir/.." && pwd)"
}

# Ensure a directory exists, creating it if necessary
ensure_dir_exists() {
  local dir="$1"
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    log_message "INFO" "Created directory: $dir"
  fi
}

# Display system information for debugging
show_system_info() {
  log_message "INFO" "System Information:"
  echo "OS: $(uname -a)"
  echo "Python: $(python --version 2>&1)"
  echo "Bash: $BASH_VERSION"
  echo "Current directory: $(pwd)"
  echo "Project root: $(get_project_root)"
}

# Run a command and log the result
run_command() {
  local cmd="$@"
  local start_time=$(date +%s.%N)

  log_message "INFO" "Running: $cmd"

  if "$@"; then
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    log_message "SUCCESS" "Command succeeded: $cmd in $duration seconds"
    return 0
  else
    local exit_code=$?
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    log_message "ERROR" "Command failed: $cmd with exit code $exit_code after $duration seconds"
    return $exit_code
  fi
}

# Clean up temporary files
cleanup_temp_files() {
  local temp_dir="${1:-/tmp}"
  local pattern="${2:-rtm_*.tmp}"

  find "$temp_dir" -name "$pattern" -type f -mtime +1 -delete
  log_message "INFO" "Cleaned up temporary files matching $pattern in $temp_dir"
}

# If running as main script, show usage
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  log_message "INFO" "RTM Automation Common Utilities"
  log_message "INFO" "This script provides utility functions for RTM automation scripts."
  log_message "INFO" "It should typically be sourced from other scripts rather than run directly."
  echo ""
  log_message "INFO" "Example usage:"
  echo "  source shell_scripts/common_utils.sh"
  echo "  log_message \"INFO\" \"Script starting...\""
  echo "  if command_exists python; then"
  echo "    run_command python --version"
  echo "  fi"
  echo ""
  show_system_info
fi
