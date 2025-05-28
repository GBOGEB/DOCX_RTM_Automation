#!/bin/bash

# Set up environment variables
export PYTHONPATH=$(pwd)

echo "DOCX RTM Automation Tool"
echo "========================="

# Check if specific modules exist and fix issues if needed
if [ -f "src/core/md_to_json_yaml.py" ]; then
    # Fix the missing import and output_path issues if needed
    if ! grep -q "import glob" src/core/md_to_json_yaml.py; then
        echo "Adding missing glob import to md_to_json_yaml.py"
        sed -i '1,10s/import os/import os\nimport glob/' src/core/md_to_json_yaml.py
    fi

    # Fix the output_stem/output_path issue if found
    if grep -q "output_stem = output_path.stem" src/core/md_to_json_yaml.py; then
        echo "Fixing output_path issue in md_to_json_yaml.py"
        sed -i 's/    output_dir = md_path.parent if output_file is None else Path(output_file).parent\n        output_stem = output_path.stem\n        output_dir = output_path.parent/    output_dir = md_path.parent if output_file is None else Path(output_file).parent/' src/core/md_to_json_yaml.py
    fi
fi

# Process input arguments
if [ "$1" == "word-to-md" ] && [ -n "$2" ]; then
    echo "Converting Word document to Markdown: $2"
    python -m src.core.word_to_md --input "$2" --verbose
    exit $?
elif [ "$1" == "word-to-md-dir" ]; then
    echo "Converting all Word documents in input directory to Markdown"
    python -m src.core.word_to_md --verbose
    exit $?
elif [ "$1" == "md-to-json" ] && [ -n "$2" ]; then
    echo "Converting Markdown to JSON/YAML: $2"
    python -m src.core.md_to_json_yaml --input "$2" --verbose
    exit $?
elif [ "$1" == "extract-rtm" ] && [ -n "$2" ]; then
    echo "Extracting RTM data from: $2"
    python -m src.extractors.extract_rtm --input "$2" --verbose
    exit $?
elif [ "$1" == "extract-rtm-dir" ] && [ -n "$2" ]; then
    echo "Extracting RTM data from directory: $2"
    python -m src.extractors.extract_rtm --input-dir "$2" --verbose
    exit $?
elif [ "$1" == "visualize-rtm" ] && [ -n "$2" ]; then
    echo "Visualizing RTM data from: $2"
    python -m src.visualizers.rtm_visualizer --input "$2"
    exit $?
elif [ "$1" == "rtm-pipeline" ]; then
    echo "Running full RTM pipeline: DOCX → MD → RTM → Visualization"
    echo "Step 1: Converting Word documents to Markdown"
    python -m src.core.word_to_md --verbose

    echo "Step 2: Extracting RTM data from all Markdown files"
    python -m src.extractors.extract_rtm --input-dir "output" --verbose

    echo "Step 3: Visualizing RTM data"
    python -m src.visualizers.rtm_visualizer --input-dir "output/rtm"
    exit $?
elif [ "$1" == "help" ] || [ -z "$1" ]; then
    echo "Usage:"
    echo "  ./run.sh word-to-md <input-file>    - Convert Word document to Markdown"
    echo "  ./run.sh word-to-md-dir             - Convert all Word documents in input directory to Markdown"
    echo "  ./run.sh md-to-json <input-file>    - Convert Markdown to JSON/YAML"
    echo "  ./run.sh extract-rtm <input-file>   - Extract RTM data from a Markdown file"
    echo "  ./run.sh extract-rtm-dir <input-dir> - Extract RTM data from all Markdown files in a directory"
    echo "  ./run.sh visualize-rtm <json-file>  - Visualize RTM data from a JSON file"
    echo "  ./run.sh rtm-pipeline               - Run the full RTM pipeline (DOCX → MD → RTM → Viz)"
    echo "  ./run.sh help                       - Show this help message"
    exit 0
else
    echo "Unknown command: $1"
    echo "Run './run.sh help' for usage information"
    exit 1
fi
