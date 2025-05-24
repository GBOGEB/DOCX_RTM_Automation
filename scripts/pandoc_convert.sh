#!/bin/bash
# Enhanced Pandoc conversion script for RTM extraction

# Default settings
LUA_FILTER="config/extend_headings.lua"
TOC_DEPTH=6
NUMBER_SECTIONS=true
EXTRACT_RTM=true

# Function to display usage
function show_help {
    echo "Usage: $0 [options] <input_file> <output_file>"
    echo ""
    echo "Options:"
    echo "  --no-toc           Disable table of contents"
    echo "  --toc-depth N      Set TOC depth (default: 6)"
    echo "  --no-numbers       Disable section numbering"
    echo "  --filter FILE      Use custom Lua filter"
    echo "  --no-rtm           Disable RTM extraction"
    echo "  --rtm-output FILE  Specify RTM output file"
    echo "  --help             Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 input/doc.docx output/doc.md"
    echo "  $0 --no-toc --filter my_filter.lua input/doc.docx output/doc.md"
}

# Parse arguments
TOC="--toc"
OPTS=()

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --help)
            show_help
            exit 0
            ;;
        --no-toc)
            TOC=""
            shift
            ;;
        --toc-depth)
            TOC_DEPTH="$2"
            shift 2
            ;;
        --no-numbers)
            NUMBER_SECTIONS=false
            shift
            ;;
        --filter)
            LUA_FILTER="$2"
            shift 2
            ;;
        --no-rtm)
            EXTRACT_RTM=false
            shift
            ;;
        --rtm-output)
            RTM_OUTPUT="$2"
            shift 2
            ;;
        *)
            # Assume this is input/output file
            if [[ -z "$INPUT_FILE" ]]; then
                INPUT_FILE="$1"
            elif [[ -z "$OUTPUT_FILE" ]]; then
                OUTPUT_FILE="$1"
            else
                echo "Error: Too many arguments."
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Check required arguments
if [[ -z "$INPUT_FILE" ]] || [[ -z "$OUTPUT_FILE" ]]; then
    echo "Error: Input and output files are required."
    show_help
    exit 1
fi

# Check if input file exists
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: Input file not found: $INPUT_FILE"
    exit 1
fi

# Prepare output directory
OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
mkdir -p "$OUTPUT_DIR"

# Build Pandoc command
PANDOC_CMD="pandoc \"$INPUT_FILE\" -o \"$OUTPUT_FILE\" --wrap=none"

if [[ -n "$TOC" ]]; then
    PANDOC_CMD="$PANDOC_CMD $TOC --toc-depth $TOC_DEPTH"
fi

if [[ "$NUMBER_SECTIONS" == true ]]; then
    PANDOC_CMD="$PANDOC_CMD --number-sections"
fi

if [[ -f "$LUA_FILTER" ]]; then
    PANDOC_CMD="$PANDOC_CMD --lua-filter \"$LUA_FILTER\""
else
    echo "Warning: Lua filter not found: $LUA_FILTER"
fi

# Extract media (images) from document
PANDOC_CMD="$PANDOC_CMD --extract-media=\"$OUTPUT_DIR/media\""

echo "Converting: $INPUT_FILE -> $OUTPUT_FILE"
echo "Command: $PANDOC_CMD"

# Execute the command
eval $PANDOC_CMD
RESULT=$?

if [[ $RESULT -eq 0 ]]; then
    echo "✅ Conversion successful"
    
    # Extract RTM data if requested
    if [[ "$EXTRACT_RTM" == true ]]; then
        if [[ -z "$RTM_OUTPUT" ]]; then
            # Default RTM output file
            OUTPUT_BASE="${OUTPUT_FILE%.*}"
            RTM_OUTPUT="$OUTPUT_BASE.rtm.json"
        fi
        
        echo "Extracting RTM data to: $RTM_OUTPUT"
        
        # Use Pandoc with RTM extraction filter
        RTM_FILTER="config/extract_rtm.lua"
        
        if [[ -f "$RTM_FILTER" ]]; then
            pandoc "$OUTPUT_FILE" -o /dev/null --lua-filter "$RTM_FILTER"
            
            # Check if extraction produced RTM data
            RTM_TMP="output/extracted_rtm.json"
            if [[ -f "$RTM_TMP" ]]; then
                mkdir -p "$(dirname "$RTM_OUTPUT")"
                mv "$RTM_TMP" "$RTM_OUTPUT"
                echo "✅ RTM data extracted successfully"
            else
                echo "❌ No RTM data was extracted"
            fi
        else
            echo "❌ RTM extraction filter not found: $RTM_FILTER"
        fi
    fi
    
    exit 0
else
    echo "❌ Conversion failed with error code: $RESULT"
    exit $RESULT
fi

# Example usage of the script
scripts\run_conversion.bat input\MASTER_1805_1144.docx output\MASTER_1805_1144.md
