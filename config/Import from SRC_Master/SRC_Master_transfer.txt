#!/usr/bin/env python3
"""
Master script for the project.
This script integrates pandoc conversion, ASCII diagram generation, and markdown linting.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Add the directory containing all modules to the Python path
modules_path = os.path.join(os.path.dirname(__file__), "modules")
if not os.path.exists(modules_path):
    print(f"Error: 'modules' directory not found at {modules_path}. Ensure it exists and contains the required files.")
    sys.exit(1)
sys.path.insert(0, modules_path)

try:
    from pandoc_integration import convert_document
except ModuleNotFoundError as e:
    print(f"Error: {e}. Ensure 'pandoc_integration.py' is present in the 'modules' directory.")
    sys.exit(1)

try:
    from ascii_diagram import generate_ascii_diagram  # type: ignore
    from markdown_lint import lint_markdown
except ModuleNotFoundError as e:
    print(f"Error: {e}. Ensure 'ascii_diagram.py' and 'markdown_lint.py' are present in the 'modules' directory.")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: master.py <command> [arguments]")
        
        sys.exit(1)

    command = sys.argv[1]
    if command == "convert":
        if len(sys.argv) < 3:
            print("Usage: master.py convert <input_file>")
            sys.exit(1)
        input_file = sys.argv[2]
        convert_document(input_file)
    elif command == "diagram":
        diagram = generate_ascii_diagram()
        print(diagram)
    elif command == "lint":
        if len(sys.argv) < 3:
            print("Usage: master.py lint <markdown_file>")
            sys.exit(1)
        markdown_file = sys.argv[2]
        lint_markdown(markdown_file)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
