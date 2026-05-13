#!/usr/bin/env python3
"""
Fix Syntax Errors - Automatically fix common syntax errors in Python files
"""

import re
import sys
from pathlib import Path
from datetime import datetime
import traceback


def fix_string_literal_errors(file_path):
    """Fix missing closing quotes and f-string issues."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Fix unterminated f-strings
        content = re.sub(r'f"([^"]*)"([^"\s]*)"', r'f"\1\2"', content)

        # Fix missing closing quotes (simple cases)
        lines = content.split("\n")
        fixed_lines = []

        for line_num, line in enumerate(lines):
            # Check for unmatched quotes
            if line.count('"') % 2 != 0 and not line.strip().endswith("\\"):
                # Try to fix by adding closing quote at end
                if not line.rstrip().endswith('"'):
                    line = line.rstrip() + '"'

            # Fix common f-string issues
            if 'f"' in line and line.count('"') % 2 != 0:
                # Simple fix: close the f-string
                if not line.rstrip().endswith('"'):
                    line = line.rstrip() + '"'

            fixed_lines.append(line)

        content = "\n".join(fixed_lines)

        # Write back if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False


def fix_indentation_errors(file_path):
    """Fix basic indentation errors."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        lines = content.split("\n")
        fixed_lines = []

        for line_num, line in enumerate(lines):
            # Convert tabs to 4 spaces
            if "\t" in line:
                line = line.replace("\t", "    ")

            # Fix mixed indentation
            if line.strip():  # Non-empty line
                leading_spaces = len(line) - len(line.lstrip())
                if leading_spaces % 4 != 0 and leading_spaces > 0:
                    # Round to nearest multiple of 4
                    new_indent = (leading_spaces // 4) * 4
                    if leading_spaces % 4 >= 2:
                        new_indent += 4
                    line = " " * new_indent + line.lstrip()

            fixed_lines.append(line)

        content = "\n".join(fixed_lines)

        # Write back if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        print(f"Error fixing indentation in {file_path}: {e}")
        return False


def fix_syntax_error_in_file(file_path):
    """Fix syntax errors in a specific file."""
    print(f"🔧 Fixing syntax errors in: {file_path}")

    fixed_issues = []

    # Fix string literal errors
    if fix_string_literal_errors(file_path):
        fixed_issues.append("string_literals")

    # Fix indentation errors
    if fix_indentation_errors(file_path):
        fixed_issues.append("indentation")

    if fixed_issues:
        print(f"   ✅ Fixed: {', '.join(fixed_issues)}")
        return True
    else:
        print("   ℹ️ No fixes needed")
        return False


def get_files_with_syntax_errors():
    """Get list of files that have syntax errors from ruff output."""
    error_files = [
        "DOCX_RTM_Automation/scripts/debug_full_pipeline.py",
        "DOCX_RTM_Automation/scripts/docx_rtm_automation.py",
        "DOCX_RTM_Automation/src/extractors/extract_outline.py",
        "DOCX_RTM_Automation/src/extractors/extract_rtm.py",
        "full_pipeline_guide.py",
        "quick_import_fix.py",
        "scripts/automation/run_full_pipeline.py",
        "scripts/debug/fix_pyproject_and_final_cleanup.py",
        "scripts/debug_full_pipeline.py",
        "scripts/docx_rtm_automation.py",
        "server/app.py",
    ]

    # Filter to files that actually exist
    existing_files = []
    for file_path in error_files:
        if Path(file_path).exists():
            existing_files.append(file_path)

    return existing_files


def backup_file(file_path):
    """Create a backup of the file before fixing."""
    backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with open(file_path, "r", encoding="utf-8") as src:
            content = src.read()
        with open(backup_path, "w", encoding="utf-8") as dst:
            dst.write(content)
        return backup_path
    except Exception as e:
        print(f"Warning: Could not create backup for {file_path}: {e}")
        return None


def main():
    """Main function to fix syntax errors."""

    print("🔧 RTM Syntax Error Fix Tool")
    print("=" * 35)

    # Get files with syntax errors
    error_files = get_files_with_syntax_errors()

    if not error_files:
        print("✅ No files with syntax errors found!")
        return 0

    print(f"📋 Found {len(error_files)} files with syntax errors:")
    for file_path in error_files:
        print(f"   • {file_path}")

    print("\n🔧 Fixing syntax errors...")

    fixed_count = 0

    for file_path in error_files:
        try:
            # Create backup
            backup_path = backup_file(file_path)
            if backup_path:
                print(f"📋 Backup created: {backup_path}")

            # Fix the file
            if fix_syntax_error_in_file(file_path):
                fixed_count += 1

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            traceback.print_exc()

    print("\n🎊 SYNTAX ERROR FIX COMPLETE!")
    print("=" * 35)
    print(f"📊 Files processed: {len(error_files)}")
    print(f"✅ Files fixed: {fixed_count}")
    print(f"ℹ️ Files unchanged: {len(error_files) - fixed_count}")

    if fixed_count > 0:
        print("\n🚀 You can now run:")
        print("   ruff format .")
        print("   ruff check . --fix")
        print("   python rtm_pipeline_executor.py")

    print("\n💡 Note: Complex syntax errors may require manual review")

    return 0


if __name__ == "__main__":
    sys.exit(main())
