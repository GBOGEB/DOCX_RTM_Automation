#!/bin/bash

# Script to check RTM workflow execution paths and status
# Usage: ./rtm_status_fixed.sh [--verbose] [--full-report]

# Get project root directory
PROJECT_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Source common utilities if available
if [ -f "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh" ]; then
    source "${PROJECT_ROOT_DIR}/shell_scripts/common_utils.sh"
else
    # Define minimal versions of logging functions if common_utils.sh isn't available
    log_message() {
        local level="$1"
        local message="$2"
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$timestamp] [$level] $message"
    }
    command_exists() {
        command -v "$1" >/dev/null 2>&1
    }
fi

# Process arguments
VERBOSE=false
WORKFLOW_NAME=""
FULL_REPORT=false

usage() {
    echo "Usage: $0 [--verbose] [--full-report] [workflow_name]"
    echo ""
    echo "Options:"
    echo "  --verbose       Display more detailed information"
    echo "  --full-report   Generate a comprehensive status report"
    echo "  workflow_name   Check a specific workflow by name (e.g., 'rtm', 'setup')"
    echo ""
    echo "Examples:"
    echo "  $0                    # Basic check of all workflows"
    echo "  $0 --verbose          # Detailed check of all workflows"
    echo "  $0 --full-report      # Generate a comprehensive status report"
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            usage
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --full-report|-f)
            FULL_REPORT=true
            shift
            ;;
        -*)
            log_message "ERROR" "Unknown option: $1"
            usage
            ;;
        *)
            if [ -z "$WORKFLOW_NAME" ]; then
                WORKFLOW_NAME="$1"
            else
                log_message "ERROR" "Too many arguments: $1"
                usage
            fi
            shift
            ;;
    esac
done

# Initialize variables
DOCX_COUNT=0
MD_COUNT=0
JSON_COUNT=0
OUT_MD_COUNT=0
OUT_JSON_COUNT=0
OUT_YAML_COUNT=0
RECENT_FILES=0
RTM_FILE_COUNT=0
ERROR_COUNT=0
WARNING_COUNT=0

log_message "INFO" "Checking RTM workflow status..."

# Check for input files
log_message "INFO" "Checking for input files..."
INPUT_DIR="${PROJECT_ROOT_DIR}/input"
if [ -d "$INPUT_DIR" ]; then
    DOCX_COUNT=$(find "$INPUT_DIR" -name "*.docx" | wc -l)
    MD_COUNT=$(find "$INPUT_DIR" -name "*.md" | wc -l)
    JSON_COUNT=$(find "$INPUT_DIR" -name "*.json" | wc -l)

    if [ "$DOCX_COUNT" -gt 0 ]; then
        log_message "SUCCESS" "Found $DOCX_COUNT DOCX files in input directory"
        if [ "$VERBOSE" = true ]; then
            echo "DOCX files:"
            find "$INPUT_DIR" -name "*.docx" -exec basename {} \; | sed 's/^/  - /'
        fi
    else
        log_message "WARNING" "No DOCX files found in input directory"
    fi

    if [ "$MD_COUNT" -gt 0 ]; then
        log_message "SUCCESS" "Found $MD_COUNT Markdown files in input directory"
        if [ "$VERBOSE" = true ]; then
            echo "Markdown files:"
            find "$INPUT_DIR" -name "*.md" -exec basename {} \; | sed 's/^/  - /'
        fi
    else
        log_message "INFO" "No Markdown files found in input directory"
    fi

    if [ "$JSON_COUNT" -gt 0 ]; then
        log_message "SUCCESS" "Found $JSON_COUNT JSON files in input directory"
        if [ "$VERBOSE" = true ]; then
            echo "JSON files:"
            find "$INPUT_DIR" -name "*.json" -exec basename {} \; | sed 's/^/  - /'
        fi
    else
        log_message "INFO" "No JSON files found in input directory"
    fi
else
    log_message "ERROR" "Input directory not found at $INPUT_DIR"
fi

# Check for output files
log_message "INFO" "Checking for output files..."
OUTPUT_DIR="${PROJECT_ROOT_DIR}/output"
if [ -d "$OUTPUT_DIR" ]; then
    OUT_MD_COUNT=$(find "$OUTPUT_DIR" -name "*.md" | wc -l)
    OUT_JSON_COUNT=$(find "$OUTPUT_DIR" -name "*.json" | wc -l)
    OUT_YAML_COUNT=$(find "$OUTPUT_DIR" -name "*.yaml" -o -name "*.yml" | wc -l)

    if [ "$OUT_MD_COUNT" -gt 0 ]; then
        log_message "SUCCESS" "Found $OUT_MD_COUNT Markdown files in output directory"
    else
        log_message "INFO" "No Markdown files found in output directory"
    fi

    if [ "$OUT_JSON_COUNT" -gt 0 ]; then
        log_message "SUCCESS" "Found $OUT_JSON_COUNT JSON files in output directory"
    else
        log_message "INFO" "No JSON files found in output directory"
    fi

    if [ "$OUT_YAML_COUNT" -gt 0 ]; then
        log_message "SUCCESS" "Found $OUT_YAML_COUNT YAML files in output directory"
    else
        log_message "INFO" "No YAML files found in output directory"
    fi

    # Check for RTM-specific output
    RTM_DIR="${OUTPUT_DIR}/rtm"
    if [ -d "$RTM_DIR" ]; then
        RTM_FILE_COUNT=$(find "$RTM_DIR" -type f | wc -l)
        log_message "SUCCESS" "Found RTM output directory with $RTM_FILE_COUNT files"
        if [ "$VERBOSE" = true ] && [ "$RTM_FILE_COUNT" -gt 0 ]; then
            echo "RTM output files:"
            find "$RTM_DIR" -type f -exec basename {} \; | sed 's/^/  - /'
        fi
    else
        log_message "WARNING" "No RTM output directory found at $RTM_DIR"
    fi

    # Check recent activity
    RECENT_FILES=$(find "$OUTPUT_DIR" -type f -mtime -1 2>/dev/null | wc -l)
    if [ "$RECENT_FILES" -gt 0 ]; then
        log_message "INFO" "Found $RECENT_FILES files modified in the last 24 hours"
        if [ "$VERBOSE" = true ]; then
            echo "Recently modified files:"
            find "$OUTPUT_DIR" -type f -mtime -1 | xargs -I{} basename {} | head -5 | sed 's/^/  - /'
            if [ "$(find "$OUTPUT_DIR" -type f -mtime -1 | wc -l)" -gt 5 ]; then
                echo "  - ... and $((RECENT_FILES - 5)) more files"
            fi
        fi
    else
        log_message "INFO" "No recent file activity in output directory"
    fi
else
    log_message "ERROR" "Output directory not found at $OUTPUT_DIR"
fi

# Check RTM pipeline configuration
log_message "INFO" "Checking RTM pipeline configuration..."
CONFIG_FILE="${PROJECT_ROOT_DIR}/config/paths.yaml"
if [ -f "$CONFIG_FILE" ]; then
    log_message "SUCCESS" "Found configuration file at $CONFIG_FILE"

    # Check for pipeline configuration in the YAML file
    if grep -q "pipeline:" "$CONFIG_FILE"; then
        log_message "SUCCESS" "Pipeline configuration found"

        if [ "$VERBOSE" = true ]; then
            echo "Pipeline steps from configuration:"
            grep -A 20 "pipeline:" "$CONFIG_FILE" | grep -E "name:|script:|enabled:" | head -15 | sed 's/^/  /'
        fi
    else
        log_message "WARNING" "No pipeline configuration found in $CONFIG_FILE"
    fi
else
    log_message "ERROR" "Configuration file not found at $CONFIG_FILE"
fi

# Check for active processes
log_message "INFO" "Checking for RTM-related processes..."
RTM_PROCESSES=$(ps aux | grep -i "rtm\|docx.*automation" | grep -v grep | wc -l)
if [ "$RTM_PROCESSES" -gt 0 ]; then
    log_message "INFO" "Found $RTM_PROCESSES RTM-related processes running"
    if [ "$VERBOSE" = true ]; then
        echo "RTM processes:"
        ps aux | grep -i "rtm\|docx.*automation" | grep -v grep | sed 's/^/  /'
    fi
else
    log_message "INFO" "No RTM-related processes currently running"
fi

# Check log files for errors
log_message "INFO" "Checking log files for errors..."
LOGS_DIR="${PROJECT_ROOT_DIR}/logs"
if [ -d "$LOGS_DIR" ]; then
    ERROR_COUNT=$(grep -i "error" "$LOGS_DIR"/* 2>/dev/null | wc -l)
    WARNING_COUNT=$(grep -i "warning" "$LOGS_DIR"/* 2>/dev/null | wc -l)

    if [ "$ERROR_COUNT" -gt 0 ]; then
        log_message "WARNING" "Found $ERROR_COUNT error messages in log files"
        if [ "$VERBOSE" = true ]; then
            echo "Recent error messages:"
            grep -i "error" "$LOGS_DIR"/* 2>/dev/null | tail -5 | sed 's/^/  /'
        fi
    else
        log_message "SUCCESS" "No error messages found in log files"
    fi

    if [ "$WARNING_COUNT" -gt 0 ]; then
        log_message "INFO" "Found $WARNING_COUNT warning messages in log files"
    fi

    # Get the most recent log file
    LATEST_LOG=$(find "$LOGS_DIR" -type f -name "*.log" -printf "%T@ %p\n" 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
    if [ -n "$LATEST_LOG" ]; then
        log_message "INFO" "Latest log file: $(basename "$LATEST_LOG")"
        if [ "$VERBOSE" = true ]; then
            echo "Last 10 lines from the latest log:"
            tail -10 "$LATEST_LOG" | sed 's/^/  /'
        fi
    fi
else
    log_message "WARNING" "Logs directory not found at $LOGS_DIR"
fi

# Generate full report if requested
if [ "$FULL_REPORT" = true ]; then
    REPORT_FILE="${OUTPUT_DIR}/rtm_status_report_$(date +%Y%m%d_%H%M%S).md"

    log_message "INFO" "Generating full status report at $REPORT_FILE..."

    # Ensure output directory exists
    mkdir -p "$OUTPUT_DIR"

    # Create the report
    {
        echo "# RTM Workflow Status Report"
        echo ""
        echo "Generated: $(date)"
        echo ""
        echo "## System Information"
        echo ""
        echo "- OS: $(uname -a)"
        echo "- Python: $(python --version 2>&1)"
        echo "- Project Root: $PROJECT_ROOT_DIR"
        echo ""
        echo "## Input Files"
        echo ""
        echo "- DOCX Files: $DOCX_COUNT"
        echo "- Markdown Files: $MD_COUNT"
        echo "- JSON Files: $JSON_COUNT"
        echo ""
        echo "## Output Files"
        echo ""
        echo "- Markdown Files: $OUT_MD_COUNT"
        echo "- JSON Files: $OUT_JSON_COUNT"
        echo "- YAML Files: $OUT_YAML_COUNT"
        echo "- Recent Files (last 24h): $RECENT_FILES"
        echo ""
        echo "## RTM Output"
        echo ""

        if [ -d "$RTM_DIR" ]; then
            echo "- RTM Files: $RTM_FILE_COUNT"
            echo ""
            echo "### RTM File Listing"
            echo ""
            echo "```"
            # Use find with no -printf option for compatibility
            find "$RTM_DIR" -type f -exec basename {} \; 2>/dev/null | sort
            echo "```"
        else
            echo "- RTM Directory not found"
        fi

        echo ""
        echo "## Log Summary"
        echo ""
        echo "- Errors: $ERROR_COUNT"
        echo "- Warnings: $WARNING_COUNT"
        echo ""

        if [ -n "$LATEST_LOG" ]; then
            echo "### Latest Log File: $(basename "$LATEST_LOG")"
            echo ""
            echo "```"
            if [ -f "$LATEST_LOG" ]; then
                tail -20 "$LATEST_LOG" 2>/dev/null
            else
                echo "Log file not found or not accessible"
            fi
            echo "```"
        fi

        echo ""
        echo "## Recommendations"
        echo ""

        if [ "$ERROR_COUNT" -gt 0 ] || [ ! -d "$RTM_DIR" ] || [ ! -f "$CONFIG_FILE" ]; then
            echo "Issues were found with the RTM workflow. Please:"
            echo ""
            echo "1. Check the configuration file"
            echo "2. Verify input files"
            echo "3. Review log files for errors"
            echo "4. Run RTM pipeline to generate output"
        else
            echo "RTM workflow appears to be functioning normally. Next steps:"
            echo ""
            echo "1. Add more input files for processing"
            echo "2. Run './shell_scripts/run_rtm.sh' for new content"
            echo "3. Check output files for results"
        fi
    } > "$REPORT_FILE"

    log_message "SUCCESS" "Full status report generated at $REPORT_FILE"
fi

# Summary
log_message "INFO" "RTM workflow status check completed"

# Show recommendations
echo ""
echo "-------------------------------------------------"
if [ "$ERROR_COUNT" -gt 0 ] || [ ! -d "$RTM_DIR" ] || [ ! -f "$CONFIG_FILE" ]; then
    log_message "WARNING" "Issues were found with the RTM workflow"
    echo "Recommendations:"
    echo "  1. Check the configuration file"
    echo "  2. Verify input files"
    echo "  3. Review log files for errors"
    echo "  4. Run RTM pipeline to generate output"
else
    log_message "SUCCESS" "RTM workflow appears to be functioning normally"
    echo "Next steps:"
    echo "  1. Add more input files for processing"
    echo "  2. Run './shell_scripts/run_rtm.sh' for new content"
    echo "  3. Check output files for results"
fi
echo "-------------------------------------------------"
