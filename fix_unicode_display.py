#!/usr/bin/env python3
"""
Fix Unicode Display Issues - Replace problematic Unicode with safe alternatives
"""

import os
import sys
import re
from pathlib import Path

def detect_encoding_issues():
    """Detect if the terminal has Unicode encoding issues."""
    try:
        # Test if we can print emojis
        test_string = "🎉 ✅ 📁"
        print(test_string, end='')
        print('\r' + ' ' * len(test_string) + '\r', end='')  # Clear the line
        return False  # No issues if we got here
    except UnicodeEncodeError:
        return True  # Has encoding issues

def create_safe_replacements():
    """Create safe text replacements for problematic Unicode."""
    return {
        # Emojis to safe text
        '🎉': '[SUCCESS]',
        '✅': '[OK]',
        '❌': '[ERROR]',
        '⚠️': '[WARNING]',
        '🔧': '[FIX]',
        '📁': '[DIR]',
        '📄': '[FILE]',
        '🚀': '[LAUNCH]',
        '💡': '[TIP]',
        '🔍': '[SEARCH]',
        '📊': '[REPORT]',
        '🎯': '[TARGET]',

        # Special characters to safe alternatives
        '•': '*',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '═': '=',
        '─': '-',
        '│': '|',

        # Problematic Unicode sequences seen in your output
        'Ô£à': '[COMPLETE]',
        '­ƒôé': '[CHECK]',
        'ÔÇó': '*',
        '­ƒÜÇ': '[START]',
        '­ƒôï': '[INFO]',
        '­ƒöº': '[BEGIN]',
    }

def fix_file_encoding(file_path, replacements):
    """Fix encoding issues in a specific file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply replacements
        original_content = content
        for unicode_char, replacement in replacements.items():
            content = content.replace(unicode_char, replacement)

        # Only write back if changes were made
        if content != original_content:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.unicode_backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)

            # Write fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"[FIXED] {file_path} - backup saved as {backup_path}")
            return True
        else:
            print(f"[OK] {file_path} - no Unicode issues found")
            return False

    except Exception as e:
        print(f"[ERROR] Could not fix {file_path}: {e}")
        return False

def fix_batch_files():
    """Fix Unicode issues in batch files."""
    print("FIXING BATCH FILE UNICODE ISSUES")
    print("=" * 35)

    batch_files = [
        Path("run_pipeline.bat"),
        Path("setup_and_run_pipeline.bat"),
    ]

    replacements = create_safe_replacements()
    fixed_count = 0

    for batch_file in batch_files:
        if batch_file.exists():
            if fix_file_encoding(batch_file, replacements):
                fixed_count += 1
        else:
            print(f"[SKIP] {batch_file} - file not found")

    print(f"\n[SUMMARY] Fixed {fixed_count} batch files")
    return fixed_count

def fix_python_files():
    """Fix Unicode issues in Python files that generate output."""
    print("\nFIXING PYTHON FILE UNICODE ISSUES")
    print("=" * 35)

    python_files = [
        Path("setup_and_run_pipeline.py"),
        Path("simple_test_pipeline.py"),
        Path("word_markdown_pipeline_fixed.py"),
        Path("main_organized.py"),
    ]

    replacements = create_safe_replacements()
    fixed_count = 0

    for python_file in python_files:
        if python_file.exists():
            if fix_file_encoding(python_file, replacements):
                fixed_count += 1
        else:
            print(f"[SKIP] {python_file} - file not found")

    print(f"\n[SUMMARY] Fixed {fixed_count} Python files")
    return fixed_count

def create_unicode_safe_functions():
    """Create utility functions for Unicode-safe output."""
    utils_content = '''#!/usr/bin/env python3
"""
Unicode Safe Output Utilities
"""

import sys

def safe_print(text, **kwargs):
    """Print text with Unicode fallbacks."""
    replacements = {
        '🎉': '[SUCCESS]', '✅': '[OK]', '❌': '[ERROR]', '⚠️': '[WARNING]',
        '🔧': '[FIX]', '📁': '[DIR]', '📄': '[FILE]', '🚀': '[LAUNCH]',
        '💡': '[TIP]', '🔍': '[SEARCH]', '📊': '[REPORT]', '🎯': '[TARGET]',
        '•': '*', '→': '->', '←': '<-', '═': '=', '─': '-',
        'Ô£à': '[COMPLETE]', '­ƒôé': '[CHECK]', 'ÔÇó': '*'
    }

    # Apply replacements
    for unicode_char, replacement in replacements.items():
        text = text.replace(unicode_char, replacement)

    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        # Fallback to ASCII-only
        text = text.encode('ascii', 'replace').decode('ascii')
        print(text, **kwargs)

def safe_header(title, width=50):
    """Print a safe header."""
    safe_print("=" * width)
    safe_print(title.center(width))
    safe_print("=" * width)

def safe_success(message):
    """Print success message safely."""
    safe_print(f"[SUCCESS] {message}")

def safe_error(message):
    """Print error message safely."""
    safe_print(f"[ERROR] {message}")

def safe_info(message):
    """Print info message safely."""
    safe_print(f"[INFO] {message}")
'''

    utils_path = Path("unicode_safe_utils.py")
    with open(utils_path, 'w', encoding='utf-8') as f:
        f.write(utils_content)

    print(f"[CREATED] {utils_path} - Unicode-safe utility functions")

def test_terminal_output():
    """Test current terminal output capabilities."""
    print("\nTESTING TERMINAL OUTPUT")
    print("=" * 25)

    test_cases = [
        ("Basic ASCII", "Hello World"),
        ("Emojis", "🎉 ✅ 📁"),
        ("Special chars", "• → ← ═"),
        ("Problematic", "Ô£à ­ƒôé ÔÇó"),
    ]

    for name, test_text in test_cases:
        try:
            print(f"{name:15}: {test_text}")
        except UnicodeEncodeError:
            print(f"{name:15}: [ENCODING ERROR]")

    print()

def main():
    """Main function to fix Unicode display issues."""
    print("UNICODE DISPLAY ISSUE FIXER")
    print("=" * 30)
    print()

    # Test current terminal
    has_issues = detect_encoding_issues()

    if has_issues:
        print("[WARNING] Terminal has Unicode encoding issues")
    else:
        print("[INFO] Terminal appears to support Unicode")

    test_terminal_output()

    # Fix files
    batch_fixes = fix_batch_files()
    python_fixes = fix_python_files()

    # Create utilities
    create_unicode_safe_functions()

    print("\n" + "=" * 50)
    print("UNICODE FIX COMPLETE!")
    print()
    print(f"[SUMMARY] Fixed {batch_fixes + python_fixes} files")
    print()
    print("NEXT STEPS:")
    print("1. Use: ./run_pipeline_clean.bat")
    print("2. Or try: python setup_and_run_pipeline.py")
    print("3. Import unicode_safe_utils for safe printing")
    print()
    print("TERMINAL IMPROVEMENTS:")
    print("* Use Windows Terminal for better Unicode support")
    print("* Run: chcp 65001 (in Command Prompt)")
    print("* Export LANG=en_US.UTF-8 (in Git Bash)")

if __name__ == "__main__":
    main()
