#!/bin/bash
# Helper script to run ASCII diagram commands from Git Bash

# Change to project directory
cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0 || {
    echo "Failed to change to project directory"
    exit 1
}

echo "ASCII Diagram Generator"
echo "======================"
echo ""

# Function to generate all diagram types
generate_all_diagrams() {
    echo "Generating workflow diagram..."
    python code/ascii_diagram.py --workflow

    echo "Generating DMAIC diagram..."
    python code/ascii_diagram.py --dmaic data/rtm_dmaic.md

    echo "Generating process flow diagram..."
    python code/ascii_diagram.py --process-flow data/rtm_workflow.json

    echo "Generating requirements structure diagram..."
    python code/ascii_diagram.py input/requirements.md

    echo "Generating step plan diagram..."
    python code/ascii_diagram.py --process-flow Step_Plan_AB.txt

    echo "All diagrams generated successfully!"
    echo "Check the output/diagrams directory for results."
}

# Show menu
echo "Select an option:"
echo "1. Generate RTM workflow diagram"
echo "2. Generate DMAIC diagram"
echo "3. Generate process flow from JSON"
echo "4. Generate document structure diagram"
echo "5. Generate step plan diagram"
echo "6. Generate all diagrams"
echo "q. Quit"
echo ""

read -p "Enter your choice: " choice

case $choice in
    1)
        python code/ascii_diagram.py --workflow
        ;;
    2)
        python code/ascii_diagram.py --dmaic data/rtm_dmaic.md
        ;;
    3)
        python code/ascii_diagram.py --process-flow data/rtm_workflow.json
        ;;
    4)
        python code/ascii_diagram.py input/requirements.md
        ;;
    5)
        python code/ascii_diagram.py --process-flow Step_Plan_AB.txt
        ;;
    6)
        generate_all_diagrams
        ;;
    q|Q)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        ;;
esac

echo ""
echo "Done!"
