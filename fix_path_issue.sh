#!/bin/bash

# This script helps fix path issues in Git Bash when changing directories

# Display the current directory
echo "Current directory: $(pwd)"

# The error you're seeing is due to Git Bash having issues with Windows paths
# The proper way to reference Windows paths in Git Bash is with / instead of \
# and with /c/ instead of C:

echo "To navigate to the project directory in Git Bash, use:"
echo "cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0"
echo ""

# Attempt to change to the correct directory
cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0 2>/dev/null

if [ $? -eq 0 ]; then
    echo "Successfully changed to the project directory."
    echo "New current directory: $(pwd)"
else
    echo "Failed to change directory. Please check if the path exists."
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Verify that the folder exists at C:\\Users\\gbonthuy\\Downloads\\DOCX_RTM_Automation_v1.0"
    echo "2. Check for any spaces or special characters in the path"
    echo "3. Try navigating step by step:"
    echo "   cd /c"
    echo "   cd Users"
    echo "   cd gbonthuy"
    echo "   cd Downloads"
    echo "   cd DOCX_RTM_Automation_v1.0"
fi

echo ""
echo "Alternative approach:"
echo "You can also run Python commands from your current location by specifying the full path:"
echo "python /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/code/ascii_diagram.py --workflow"
