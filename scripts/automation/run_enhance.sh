#!/bin/bash

# This script provides easy access to the enhance_document_parsing.py options

echo "DOCX RTM Automation - Document Enhancement Tool"
echo "=============================================="
echo ""

if [ "$1" == "--list" ]; then
    python enhance_document_parsing.py --list
elif [ "$1" == "--sample" ]; then
    python enhance_document_parsing.py --sample
elif [ "$1" == "--interactive" ]; then
    python enhance_document_parsing.py --interactive
elif [ -n "$1" ]; then
    # If an argument is provided, assume it's a file path
    python enhance_document_parsing.py "$1"
else
    # Display help if no arguments provided
    echo "Usage:"
    echo "  ./run_enhance.sh [OPTION] [FILE]"
    echo ""
    echo "Options:"
    echo "  --list         List available input files"
    echo "  --sample       Use the sample document"
    echo "  --interactive  Choose from available files interactively"
    echo ""
    echo "Examples:"
    echo "  ./run_enhance.sh input/my_document.docx"
    echo "  ./run_enhance.sh --sample"
    echo "  ./run_enhance.sh --list"
    echo ""
fi
