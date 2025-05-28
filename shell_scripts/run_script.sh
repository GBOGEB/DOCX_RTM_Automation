#!/bin/bash

# Script: run_script.sh
# Description: A generic script to execute another specified script with arguments.
# Usage: ./run_script.sh <path_to_script_to_run> [arg1 arg2 ...]

# Exit on error, treat unset variables as an error
set -eu

log_info() {
  echo "[INFO] $(date +'%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
  echo "[ERROR] $(date +'%Y-%m-%d %H:%M:%S') - $1" >&2
}

if [ "$#" -lt 1 ]; then
  log_error "Usage: $0 <script_to_run> [arguments...]"
  log_error "Example: $0 ./shell_scripts/problem_helpers.sh some_arg"
  exit 1
fi

SCRIPT_TO_RUN="$1"
shift # Remove the first argument (script_to_run), remaining are args for that script

if [ ! -f "$SCRIPT_TO_RUN" ]; then
  log_error "Script to run '$SCRIPT_TO_RUN' not found."
  exit 1
fi

# Ensure the target script is executable
if [ ! -x "$SCRIPT_TO_RUN" ]; then
  log_info "Script '$SCRIPT_TO_RUN' is not executable. Attempting to set +x..."
  chmod +x "$SCRIPT_TO_RUN"
  if [ $? -ne 0 ]; then
    log_error "Failed to make '$SCRIPT_TO_RUN' executable. Please check permissions."
    exit 1
  fi
fi

log_info "Executing '$SCRIPT_TO_RUN' with arguments: $@"
# Execute the target script, passing along any remaining arguments
"$SCRIPT_TO_RUN" "$@"
exit_status=$?

if [ $exit_status -eq 0 ]; then
  log_info "Script '$SCRIPT_TO_RUN' completed successfully."
else
  log_error "Script '$SCRIPT_TO_RUN' failed with exit code $exit_status."
fi

exit $exit_status
