#!/usr/bin/env python3

import os
import re
import sys


def extract_python_code(md_file):
    """Extract Python code from terminal.md"""
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Find Python code blocks
    python_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)

    if not python_blocks:
        print("Error: No Python code found in terminal.md")
        sys.exit(1)

    # Return the largest Python code block (main script)
    return max(python_blocks, key=len)


def main():
    """Run the terminal script from terminal.md"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    terminal_md = os.path.join(script_dir, "terminal.md")

    if not os.path.exists(terminal_md):
        print(f"Error: terminal.md not found in {script_dir}")
        sys.exit(1)

    # Extract Python code
    code = extract_python_code(terminal_md)

    # Execute the code
    exec(code)


if __name__ == "__main__":
    main()
