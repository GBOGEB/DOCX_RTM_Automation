#!/usr/bin/env python3
"""
Fix specific syntax errors in Python files that are preventing Black formatting from working.
This script targets known issues in specific files and applies targeted fixes.
"""

import os
import re
import sys


def fix_debug_full_pipeline(file_path):
    """Fix incorrect string literals in debug_full_pipeline.py files."""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix specific issue with unclosed string literals
    modified_content = content

    # Fix for logging statements with unclosed quotes
    pattern = r'logging\.debug\("Pipeline execution[^"]*$'
    if re.search(pattern, modified_content, re.MULTILINE):
        modified_content = re.sub(
            pattern,
            'logging.debug("Pipeline execution completed successfully")',
            modified_content,
            flags=re.MULTILINE,
        )
        changes_made = True
    else:
        changes_made = False

    # Write back to file if changes were made
    if changes_made:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True, "Fixed incorrect string literal"

    return False, "No issues found to fix"


def fix_docx_rtm_automation(file_path):
    """Fix incorrect f-strings in docx_rtm_automation.py files."""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix specific issues with f-strings
    modified_content = content
    changes_made = False

    # Fix for f-strings with unbalanced braces
    pattern = r'f"([^"]*){([^{}]*)([^}"]*)}"'
    matches = re.finditer(pattern, modified_content)

    for match in matches:
        full_match = match.group(0)
        prefix = match.group(1)
        var_content = match.group(2)
        suffix = match.group(3)

        # Check if there's an unbalanced brace issue
        if "{" in suffix or "}" in prefix:
            fixed_string = f'f"{prefix}{{{var_content}}}{suffix}"'
            modified_content = modified_content.replace(full_match, fixed_string)
            changes_made = True

    # Write back to file if changes were made
    if changes_made:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True, "Fixed incorrect f-string"

    return False, "No issues found to fix"


def fix_any_file(file_path):
    """Generic function to fix common syntax errors in any Python file."""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Try to fix multiple common issues
    modified_content = content
    changes_made = False

    # 1. Fix missing closing parentheses at end of file
    if re.search(r"def [^(]+\([^)]*$", modified_content, re.MULTILINE):
        modified_content += "\n)"
        changes_made = True

    # 2. Fix missing closing quotes
    for quote_char in ['"', "'"]:
        pattern = f"{quote_char}([^{quote_char}]*)$"
        if re.search(pattern, modified_content, re.MULTILINE):
            modified_content += quote_char
            changes_made = True

    # Write back to file if changes were made
    if changes_made:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        return True, "Fixed generic syntax error"

    return False, "No issues found to fix"


def main():
    """Main function to fix specific errors in known problematic files."""
    print("Fixing specific syntax errors in files that failed Black formatting...")

    # List of files to check and their corresponding fix functions
    files_to_check = [
        # Path and function pairs
        ("DOCX_RTM_Automation/src/extractors/extract_rtm.py", fix_any_file),
        ("DOCX_RTM_Automation/scripts/debug_full_pipeline.py", fix_debug_full_pipeline),
        ("scripts/debug_full_pipeline.py", fix_debug_full_pipeline),
        ("DOCX_RTM_Automation/scripts/docx_rtm_automation.py", fix_docx_rtm_automation),
        ("scripts/docx_rtm_automation.py", fix_docx_rtm_automation),
        ("DOCX_RTM_Automation/src/extractors/extract_outline.py", fix_any_file),
        ("server/app.py", fix_any_file),
    ]

    for file_path, fix_function in files_to_check:
        print(f"Fixing syntax in {file_path}...")
        success, message = fix_function(file_path)

        if success:
            print(f"  {message} in {file_path}")
        else:
            if "File not found" in message:
                print(f"  {message}")
            else:
                print(f"  {message} in {file_path}")

    print(
        "\nAttempted to fix specific syntax errors. Please run black again to verify:"
    )
    print("  black .")
    print("\nTo execute the script, run:")
    print("  python fix_specific_errors.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
