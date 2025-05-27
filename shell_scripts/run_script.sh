#!/bin/bash
# This shell script ensures that the Python modules can be found correctly

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

# Add the project root to PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

# Run the specified Python script with any arguments
python "$@"
