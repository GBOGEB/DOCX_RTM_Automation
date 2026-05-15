#!/usr/bin/env python3
"""
Complete Syntax Fix V2 - Fixed encoding issues
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def safe_read_file(file_path):
    """Safely read a file with proper encoding detection"""
    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']

    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"   ⚠️  Error reading with {encoding}: {e}")
            continue

    # If all else fails, read as binary and decode with errors='replace'
    try:
        with open(file_path, 'rb') as f:
            content = f.read().decode('utf-8', errors='replace')
        return content, 'utf-8-with-replacements'
    except Exception as e:
        print(f"   ❌ Could not read file {file_path}: {e}")
        return None, None

def safe_write_file(file_path, content):
    """Safely write a file with UTF-8 encoding"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"   ❌ Error writing file {file_path}: {e}")
        return False

def create_clean_find_output_files():
    """Create a clean version of find_output_files.py"""
    clean_content = '''#!/usr/bin/env python3
"""
Find Output Files - Clean version with proper syntax
"""

import os
from pathlib import Path
from datetime import datetime

def find_output_files():
    """Find all output files in the output directory"""
    output_dir = Path("output")

    if not output_dir.exists():
        print("Output directory not found")
        return []

    print(f"Scanning output directory: {output_dir}")

    files = []
    for file_path in output_dir.rglob("*"):
        if file_path.is_file():
            try:
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "extension": file_path.suffix.lower()
                }
                files.append(file_info)
            except (OSError, PermissionError) as e:
                print(f"Could not access {file_path}: {e}")
                continue

    return files

def categorize_files(files):
    """Categorize files by type"""
    categories = {
        "documents": [".docx", ".pdf", ".rtf"],
        "data": [".json", ".yaml", ".yml"],
        "text": [".md", ".txt"],
        "images": [".png", ".jpg", ".jpeg", ".gif"],
        "logs": [".log"],
        "other": []
    }

    categorized = {category: [] for category in categories}

    for file_info in files:
        ext = file_info["extension"]
        categorized_file = False

        for category, extensions in categories.items():
            if category != "other" and ext in extensions:
                categorized[category].append(file_info)
                categorized_file = True
                break

        if not categorized_file:
            categorized["other"].append(file_info)

    return categorized

def display_results(categorized_files):
    """Display the results in a nice format"""
    print("\\n" + "="*60)
    print("OUTPUT FILES SUMMARY")
    print("="*60)

    total_files = sum(len(files) for files in categorized_files.values())
    total_size = sum(file["size"] for files in categorized_files.values() for file in files)

    print(f"Total Files: {total_files}")
    print(f"Total Size: {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")

    for category, files in categorized_files.items():
        if files:
            print(f"\\n{category.upper()} ({len(files)} files):")
            sorted_files = sorted(files, key=lambda x: x["modified"], reverse=True)

            for file_info in sorted_files[:10]:
                size_mb = file_info["size"] / 1024 / 1024
                if size_mb >= 1:
                    size_str = f"{size_mb:.1f} MB"
                else:
                    size_str = f"{file_info['size']:,} bytes"

                mod_time = file_info["modified"].strftime("%Y-%m-%d %H:%M")
                print(f"   • {file_info['name']} - {size_str} ({mod_time})")

            if len(files) > 10:
                print(f"   ... and {len(files) - 10} more files")

def main():
    """Main function"""
    print("RTM Output File Finder")
    print("=" * 60)
    print("Analyzing output directory for RTM pipeline results...")

    files = find_output_files()

    if not files:
        print("\\nNo output files found")
        print("\\nSuggestions:")
        print("   • Run the RTM pipeline to generate output files")
        print("   • Check if the 'output' directory exists")
        print("   • Verify file permissions")
        return

    print(f"\\nFound {len(files)} files to analyze")

    categorized = categorize_files(files)
    display_results(categorized)

    print(f"\\nAnalysis complete!")
    print("Check the 'output' directory for all generated files")

if __name__ == "__main__":
    main()
'''
    return clean_content

def create_clean_shell_script():
    """Create a clean shell script"""
    clean_content = '''#!/bin/bash
# shellcheck shell=bash
# RTM Pipeline Quick Start Script

# Check for Python
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "Python not found. Please install Python to continue."
    exit 1
fi

echo "RTM Pipeline Quick Start"
echo "========================"
echo "Using $PYTHON_CMD"
echo ""

# Simple menu
echo "What would you like to do?"
echo "1. Run RTM Pipeline"
echo "2. Check System Health"
echo "3. Debug Console"
echo "4. Exit"
echo ""

read -r -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "Starting RTM Pipeline..."
        $PYTHON_CMD setup_and_run_pipeline.py
        ;;
    2)
        echo "Running Health Check..."
        if [ -f "quick_health_check.py" ]; then
            $PYTHON_CMD quick_health_check.py
        else
            echo "Health check script not found"
        fi
        ;;
    3)
        echo "Opening Debug Console..."
        if [ -f "debug_console.py" ]; then
            $PYTHON_CMD debug_console.py
        else
            echo "Debug console not found"
        fi
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Running pipeline..."
        $PYTHON_CMD setup_and_run_pipeline.py
        ;;
esac

echo ""
echo "Operation completed!"
echo "Check the 'output' directory for results"
'''
    return clean_content

def fix_python_file():
    """Fix the Python file with encoding issues"""
    print("🔧 Fixing find_output_files.py...")

    target_file = Path("find_output_files.py")

    # Create backup of existing file if it exists
    if target_file.exists():
        backup_file = target_file.with_suffix(".py.backup.v2")
        try:
            shutil.copy2(target_file, backup_file)
            print(f"   📋 Created backup: {backup_file}")
        except Exception as e:
            print(f"   ⚠️  Could not create backup: {e}")

    # Write clean version
    clean_content = create_clean_find_output_files()
    if safe_write_file(target_file, clean_content):
        print("   ✅ Fixed find_output_files.py")
        return True
    else:
        print("   ❌ Failed to fix find_output_files.py")
        return False

def fix_shell_script():
    """Fix the shell script"""
    print("🔧 Fixing quick_start.sh...")

    script_file = Path("quick_start.sh")

    # Try to read existing content first
    existing_content, encoding = safe_read_file(script_file)

    if existing_content is None:
        print("   ⚠️  Could not read existing shell script, creating new one")
        existing_content = ""

    # Check if it needs fixing
    needs_fix = True
    if existing_content:
        lines = existing_content.split('\n')
        if lines and lines[0].startswith('#!/bin/bash'):
            if len(lines) > 1 and 'shellcheck' in lines[1]:
                needs_fix = False

    if needs_fix or not existing_content:
        # Create backup
        if script_file.exists():
            backup_file = script_file.with_suffix(".sh.backup.v2")
            try:
                shutil.copy2(script_file, backup_file)
                print(f"   📋 Created backup: {backup_file}")
            except Exception as e:
                print(f"   ⚠️  Could not create backup: {e}")

        # Write clean version
        clean_content = create_clean_shell_script()
        if safe_write_file(script_file, clean_content):
            print("   ✅ Fixed quick_start.sh")
            return True
        else:
            print("   ❌ Failed to fix quick_start.sh")
            return False
    else:
        print("   ✅ Shell script already correct")
        return True

def verify_fixes():
    """Verify that fixes worked with proper encoding"""
    print("\n🔍 Verifying fixes...")

    success = True

    # Test Python syntax
    try:
        import ast
        content, encoding = safe_read_file("find_output_files.py")
        if content is not None:
            ast.parse(content)
            print(f"   ✅ find_output_files.py syntax valid (encoding: {encoding})")
        else:
            print("   ❌ Could not read find_output_files.py")
            success = False
    except Exception as e:
        print(f"   ❌ find_output_files.py still has issues: {e}")
        success = False

    # Test shell script
    shell_file = Path("quick_start.sh")
    if shell_file.exists():
        content, encoding = safe_read_file(shell_file)
        if content is not None:
            lines = content.split('\n')
            if lines and lines[0].strip() == '#!/bin/bash':
                print(f"   ✅ quick_start.sh format correct (encoding: {encoding})")
            else:
                print(f"   ⚠️  quick_start.sh format issue: {lines[0] if lines else 'empty'}")
                # Don't fail for shell script issues
        else:
            print("   ❌ Could not read quick_start.sh")
            success = False
    else:
        print("   ⚠️  quick_start.sh not found")

    return success

def main():
    """Main function"""
    print("🔧 Complete Syntax Fix Tool V2")
    print("=" * 50)
    print("Fixing syntax and encoding issues in RTM system files\n")

    fixes_applied = 0

    # Fix Python file
    if fix_python_file():
        fixes_applied += 1

    # Fix shell script
    if fix_shell_script():
        fixes_applied += 1

    # Verify fixes
    print("\n" + "=" * 50)
    if verify_fixes():
        print("🎉 All syntax and encoding issues resolved!")
        print(f"✅ Applied {fixes_applied} fixes successfully")

        print("\n📁 Backup files created:")
        for backup in Path(".").glob("*.backup*"):
            print(f"   • {backup}")

        print("\n💡 You can now run:")
        print("   python find_output_files.py")
        print("   python syntax_checker.py")
        print("   ./quick_start.sh  (on Unix/Linux)")

        return 0
    else:
        print("⚠️  Some issues may still remain")
        print("Files have been created with clean content")
        return 1

if __name__ == "__main__":
    exit(main())
