#!/usr/bin/env python3
"""
Syntax Checker - Validate Python files for syntax errors
"""

import ast
import os
import sys
from pathlib import Path

def check_python_syntax(file_path):
    """Check if a Python file has valid syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        # Attempt to parse the file
        ast.parse(source)
        return True, None

    except SyntaxError as e:
        return False, f"Syntax Error: {e.msg} at line {e.lineno}, column {e.offset}"

    except UnicodeDecodeError as e:
        return False, f"Encoding Error: {e}"

    except Exception as e:
        return False, f"Unexpected Error: {e}"

def check_all_python_files():
    """Check all Python files in the current directory"""
    print("🔍 Python Syntax Checker")
    print("=" * 50)

    python_files = list(Path(".").glob("*.py"))

    if not python_files:
        print("No Python files found in current directory")
        return

    print(f"Found {len(python_files)} Python files to check...\n")

    valid_files = []
    invalid_files = []

    for file_path in python_files:
        print(f"Checking {file_path.name}...", end=" ")

        is_valid, error_msg = check_python_syntax(file_path)

        if is_valid:
            print("✅ Valid")
            valid_files.append(file_path)
        else:
            print(f"❌ Invalid")
            print(f"   Error: {error_msg}")
            invalid_files.append((file_path, error_msg))

    # Summary
    print("\n" + "=" * 50)
    print("SYNTAX CHECK SUMMARY")
    print("=" * 50)
    print(f"✅ Valid files: {len(valid_files)}")
    print(f"❌ Invalid files: {len(invalid_files)}")

    if invalid_files:
        print("\nFiles with syntax errors:")
        for file_path, error in invalid_files:
            print(f"   • {file_path.name}: {error}")

        print("\n💡 Fix these syntax errors to ensure proper operation")
        return 1
    else:
        print("\n🎉 All Python files have valid syntax!")
        return 0

def check_shell_scripts():
    """Check shell scripts for basic issues"""
    print("\n🔍 Shell Script Checker")
    print("=" * 50)

    shell_files = list(Path(".").glob("*.sh"))

    if not shell_files:
        print("No shell scripts found")
        return

    for file_path in shell_files:
        print(f"Checking {file_path.name}...", end=" ")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for shebang
            lines = content.split('\n')
            if lines and lines[0].startswith('#!'):
                print("✅ Has shebang")
            else:
                print("⚠️  Missing shebang (add #!/bin/bash)")

        except Exception as e:
            print(f"❌ Error reading file: {e}")

def main():
    """Main function"""
    try:
        # Check Python files
        exit_code = check_all_python_files()

        # Check shell scripts
        check_shell_scripts()

        if exit_code == 0:
            print("\n🎯 All syntax checks passed!")
        else:
            print("\n⚠️  Some files have syntax issues - please fix them")

        return exit_code

    except Exception as e:
        print(f"❌ Syntax checker failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
