#!/bin/bash

# Script to fix pipeline script issues

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source common utilities if available
if [ -f "${PROJECT_ROOT}/shell_scripts/common_utils.sh" ]; then
  source "${PROJECT_ROOT}/shell_scripts/common_utils.sh"
else
  # Define minimal logging function
  log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message"
  }
fi

log_message "INFO" "Starting pipeline scripts fix..."

# Create necessary directories
log_message "INFO" "Ensuring all necessary directories exist..."
mkdir -p "${PROJECT_ROOT}/src/core"
mkdir -p "${PROJECT_ROOT}/src/extractors"
mkdir -p "${PROJECT_ROOT}/src/utils"
mkdir -p "${PROJECT_ROOT}/src/modules"
mkdir -p "${PROJECT_ROOT}/input"
mkdir -p "${PROJECT_ROOT}/output/rtm"
mkdir -p "${PROJECT_ROOT}/output/outlines"
mkdir -p "${PROJECT_ROOT}/output/structured"
mkdir -p "${PROJECT_ROOT}/logs"

# Make sure files are executable
chmod +x "${PROJECT_ROOT}/shell_scripts/"*.sh
chmod +x "${PROJECT_ROOT}/"*.sh

# Create the special pipeline adapter module for accessing scripts
log_message "INFO" "Creating pipeline adapter module..."
mkdir -p "${PROJECT_ROOT}/src/modules"
cat > "${PROJECT_ROOT}/src/modules/pipeline_adapter.py" << 'EOF'
#!/usr/bin/env python3
"""
Pipeline Adapter for RTM Automation

This module adapts the pipeline scripts to handle common command line patterns
and provides utilities for managing pipeline steps.
"""
import os
import sys
import importlib.util
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_pipeline_script(script_path):
    """
    Dynamically load a pipeline script module.

    Args:
        script_path: Path to the Python script

    Returns:
        Loaded module or None if loading failed
    """
    try:
        script_path = Path(script_path)
        if not script_path.exists():
            logger.error(f"Script not found: {script_path}")
            return None

        module_name = script_path.stem
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Error loading script {script_path}: {e}")
        return None

def execute_script(script_path, input_dir=None, output_dir=None, **kwargs):
    """
    Execute a pipeline script.

    Args:
        script_path: Path to the Python script
        input_dir: Input directory
        output_dir: Output directory
        **kwargs: Additional arguments to pass to the script

    Returns:
        True if execution was successful, False otherwise
    """
    module = load_pipeline_script(script_path)
    if not module:
        return False

    # Build args list
    args_list = [script_path]

    if input_dir:
        if hasattr(module, 'process_all_md_files') or 'input_dir' in str(module.main.__code__.co_varnames):
            args_list.extend(["--input-dir", input_dir])
        elif hasattr(module, 'main'):
            args_list.extend(["--input", input_dir])

    if output_dir:
        if hasattr(module, 'process_all_md_files') or 'output_dir' in str(module.main.__code__.co_varnames):
            args_list.extend(["--output-dir", output_dir])
        elif hasattr(module, 'main'):
            args_list.extend(["--output", output_dir])

    # Add any additional kwargs as command line args
    for key, value in kwargs.items():
        args_list.extend([f"--{key.replace('_', '-')}", str(value)])

    # Execute the script
    old_argv = sys.argv.copy()
    sys.argv = args_list

    try:
        result = module.main()
        return result == 0 if isinstance(result, int) else True
    except Exception as e:
        logger.error(f"Error executing script {script_path}: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        sys.argv = old_argv
EOF

log_message "SUCCESS" "Pipeline scripts fixed successfully"
log_message "INFO" "You can now test the pipeline with:"
log_message "INFO" "  ./shell_scripts/test_all_steps.sh"
