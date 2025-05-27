#!/bin/bash

# Script: run_rtm.sh
# Description: This script is used to automate the RTM process on Unix-based systems.

echo "Starting RTM automation process..."

# Define variables
SCRIPT_DIR=$(dirname "$0")
RTM_TOOL="$SCRIPT_DIR/rtm_tool"

# Check if the RTM tool exists
if [ ! -f "$RTM_TOOL" ]; then
    echo "Error: RTM tool not found in $SCRIPT_DIR"
    exit 1
fi

# Run the RTM tool
chmod +x "$RTM_TOOL"
"$RTM_TOOL" "$@"

# Check the exit status
if [ $? -eq 0 ]; then
    echo "RTM automation completed successfully."
else
    echo "RTM automation failed."
    exit 1
fi