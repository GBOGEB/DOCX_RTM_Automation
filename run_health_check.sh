#!/bin/bash
# shellcheck shell=bash

echo "================================================================"
echo "                    RTM QUICK HEALTH CHECK"
echo "================================================================"
echo ""
echo "This will quickly diagnose your RTM system status"
echo ""

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "ERROR: Python is not installed or not in PATH"
    echo "Please install Python and try again"
    exit 1
fi

# Check if the health check script exists
if [ ! -f "quick_health_check.py" ]; then
    echo "ERROR: quick_health_check.py not found"
    echo "Please ensure you're in the correct directory"
    exit 1
fi

echo "Starting health check..."
echo ""

# Run the health check
python quick_health_check.py

echo ""
echo "Health check complete. Check the logs folder for detailed report."
echo ""
read -p "Press Enter to continue..."
