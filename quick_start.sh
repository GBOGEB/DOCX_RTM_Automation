#!/bin/bash
# shellcheck shell=bash
# RTM Pipeline Quick Start Script - Enhanced Edition
# shellcheck shell=bash

# Color codes for better visibility
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

print_success() {
    echo -e "${PURPLE}🎉${NC} $1"
}

print_highlight() {
    echo -e "${CYAN}🚀${NC} $1"
}

# Check for Python
check_python() {
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        print_error "Python not found. Please install Python to continue."
        exit 1
    fi
    print_status "Using $PYTHON_CMD"
}

# Get system status
get_system_status() {
    local current_dir
    current_dir=$(pwd | sed 's|.*/||')  # Get just the directory name
    local python_version
    python_version=$($PYTHON_CMD --version 2>&1)
    local input_files=0
    local output_files=0

    if [ -d "input" ]; then
        input_files=$(find input -type f 2>/dev/null | wc -l)
    fi

    if [ -d "output" ]; then
        output_files=$(find output -type f 2>/dev/null | wc -l)
    fi

    echo "📊 Quick System Status:"
    echo "   Working Directory: $current_dir"
    echo "   Python Version: $python_version"
    echo "   Input Files: $input_files"
    echo "   Output Files: $output_files"
}

# Show menu
show_menu() {
    echo ""
    echo "🎯 What would you like to do?"
    echo "================================"
    echo "1. 🏥 Quick Health Check"
    echo "2. 🚀 Run RTM Pipeline (Interactive)"
    echo "3. 🔧 Debug Console"
    echo "4. 📊 Full Diagnostics Export"
    echo "5. 🌟 Ariana Extension Report"
    echo "6. 📝 Process Specific File Type"
    echo "7. 🧹 Clean Temporary Files"
    echo "8. 📋 Show Recent Activity"
    echo "9. 🔄 Auto-Process All Compatible Files"
    echo ""
}

# Execute choice
execute_choice() {
    case $1 in
        1)
            print_info "Running Quick Health Check..."
            if [ -f "quick_health_check.py" ]; then
                $PYTHON_CMD quick_health_check.py
            else
                print_warning "Health check script not found, running basic check..."
                check_basic_system
            fi
            ;;
        2)
            print_info "Starting Interactive RTM Pipeline..."
            if [ -f "setup_and_run_pipeline.py" ]; then
                $PYTHON_CMD setup_and_run_pipeline.py
            else
                print_error "Pipeline script not found: setup_and_run_pipeline.py"
            fi
            ;;
        3)
            print_info "Opening Debug Console..."
            if [ -f "debug_console.py" ]; then
                $PYTHON_CMD debug_console.py
            else
                print_error "Debug console not found: debug_console.py"
            fi
            ;;
        4)
            print_info "Exporting Full Diagnostics..."
            $PYTHON_CMD -c "
try:
    from debug_console import RTMDebugConsole
    console = RTMDebugConsole()
    console.export_all_diagnostics()
    print('✅ Diagnostics exported to logs directory')
except ImportError:
    print('❌ Debug console not available')
except Exception as e:
    print(f'❌ Error: {e}')
" 2>/dev/null || print_error "Could not export diagnostics"
            ;;
        5)
            print_info "Generating Ariana Extension Report..."
            $PYTHON_CMD -c "
try:
    from debug_console import RTMDebugConsole
    console = RTMDebugConsole()
    console.generate_ariana_report()
    print('✅ Ariana report generated')
except ImportError:
    print('❌ Debug console not available')
except Exception as e:
    print(f'❌ Error: {e}')
" 2>/dev/null || print_warning "Could not generate Ariana report"
            ;;
        6)
            print_info "Processing specific file types..."
            echo "Available file types: .docx, .md, .txt, .pdf, .rtf"
            read -r -p "Enter file extension (e.g., .docx): " ext
            if [ -n "$ext" ]; then
                $PYTHON_CMD -c "
import os
from pathlib import Path
try:
    files = list(Path('input').glob('*$ext'))
    print(f'Found {len(files)} files with extension $ext')
    for file in files[:5]:
        print(f'  • {file.name}')
    if len(files) > 5:
        print(f'  ... and {len(files) - 5} more files')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || print_warning "Could not scan for files"
            else
                print_warning "No extension provided"
            fi
            ;;
        7)
            print_info "Cleaning temporary files..."
            cleaned=0
            if [ -d "temp_processing" ]; then
                if [ "$(ls -A temp_processing 2>/dev/null)" ]; then
                    rm -rf temp_processing/* 2>/dev/null && cleaned=1
                    print_status "Temporary processing files cleaned"
                fi
            fi
            if [ -d "__pycache__" ]; then
                rm -rf __pycache__ 2>/dev/null && cleaned=1
                print_status "Python cache cleaned"
            fi
            # Clean .pyc files
            if find . -name "*.pyc" -delete 2>/dev/null; then
                cleaned=1
                print_status "Python compiled files cleaned"
            fi

            if [ $cleaned -eq 0 ]; then
                print_info "No temporary files found to clean"
            fi
            ;;
        8)
            print_info "Showing recent activity..."
            echo "📁 Recent files in output directory:"
            if [ -d "output" ]; then
                if command -v ls >/dev/null 2>&1; then
                    # Use ls with time sorting if available
                    ls -lt output 2>/dev/null | head -10 || print_warning "Could not list files"
                else
                    # Fallback to find
                    find output -type f -printf "%T@ %Tc %p\n" 2>/dev/null | sort -nr | head -10 || print_warning "Could not list files"
                fi
            else
                print_warning "Output directory not found"
            fi

            echo ""
            echo "📋 Recent log files:"
            if [ -d "logs" ]; then
                if command -v ls >/dev/null 2>&1; then
                    ls -lt logs 2>/dev/null | head -5 || print_warning "Could not list log files"
                fi
            else
                print_info "No logs directory found"
            fi
            ;;
        9)
            print_info "Auto-processing all compatible files..."
            $PYTHON_CMD -c "
import sys
import os
sys.path.append('.')

try:
    if os.path.exists('setup_and_run_pipeline.py'):
        from setup_and_run_pipeline import check_for_input_files
        files = check_for_input_files()
        if files:
            print(f'Found {len(files)} files to process')
            for file in files:
                print(f'  • {file.name if hasattr(file, \"name\") else file}')
            print('Run \"python setup_and_run_pipeline.py\" to process these files')
        else:
            print('No compatible files found in input directory')
    else:
        print('Pipeline script not found')
except Exception as e:
    print(f'Error: {e}')
" 2>/dev/null || print_warning "Could not scan for files to process"
            ;;
        *)
            print_warning "Invalid choice. Running health check by default..."
            if [ -f "quick_health_check.py" ]; then
                $PYTHON_CMD quick_health_check.py
            else
                check_basic_system
            fi
            ;;
    esac
}

# Basic system check fallback
check_basic_system() {
    print_info "Running basic system check..."

    echo "📁 Directory structure:"
    for dir in input output temp_processing logs; do
        if [ -d "$dir" ]; then
            file_count=$(find "$dir" -type f 2>/dev/null | wc -l)
            print_status "$dir: exists ($file_count files)"
        else
            print_warning "$dir: missing"
        fi
    done

    echo ""
    echo "🐍 Python files:"
    for file in setup_and_run_pipeline.py debug_console.py quick_health_check.py; do
        if [ -f "$file" ]; then
            print_status "$file: exists"
        else
            print_warning "$file: missing"
        fi
    done
}

# Main execution
main() {
    print_highlight "RTM Pipeline Quick Start - Enhanced Edition"
    echo "==============================================="
    echo ""

    # Check Python availability
    check_python

    # Show system status
    get_system_status

    # Show menu
    show_menu

    # Get user choice with validation
    while true; do
        read -r -p "Enter your choice (1-9): " choice

        if [[ "$choice" =~ ^[1-9]$ ]]; then
            break
        else
            print_error "Invalid choice. Please enter a number between 1-9."
        fi
    done

    # Execute choice
    execute_choice "$choice"

    # Show completion status
    echo ""
    print_success "Operation completed!"
    echo "======================="
    echo ""
    echo "📈 Current Status:"
    if [ -d "output" ]; then
        output_count=$(find output -type f 2>/dev/null | wc -l)
        echo "   📁 Output files: $output_count"
    fi

    if [ -d "logs" ]; then
        log_count=$(find logs -name "*.json" 2>/dev/null | wc -l)
        echo "   📋 Report files: $log_count"
    fi

    echo ""
    echo "💡 Pro Tips:"
    echo "   • Run './quick_start.sh' anytime for this menu"
    echo "   • Use 'python debug_console.py' for detailed debugging"
    echo "   • Check 'logs/' directory for detailed reports"
    echo "   • Your system processed files successfully! 🎉"

    echo ""
    read -r -p "Press Enter to exit..."
}

# Run main function
main "$@"
