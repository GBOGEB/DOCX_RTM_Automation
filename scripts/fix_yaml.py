#!/usr/bin/env python3
"""Fix common YAML syntax issues"""

import sys
from pathlib import Path
import re

def fix_yaml_file(file_path):
    """Fix common YAML syntax issues in a file"""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    print(f"Fixing YAML file: {file_path}")

    # Read the file
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    # Fix common issues
    fixed_lines = []
    in_multiline = False
    multiline_indent = 0

    for i, line in enumerate(lines):
        # Remove trailing whitespace
        line = line.rstrip() + '\n'

        # Fix tabs to spaces
        if '\t' in line:
            line = line.replace('\t', '  ')

        # Check for unclosed quotes
        single_quotes = line.count("'") % 2
        double_quotes = line.count('"') % 2

        if single_quotes:
            print(f"Line {i+1}: Unclosed single quote - {line.strip()}")
            line = line.rstrip() + "'\n"

        if double_quotes:
            print(f"Line {i+1}: Unclosed double quote - {line.strip()}")
            line = line.rstrip() + '"\n'

        # New: Check for key without colon (likely key missing colon)
        stripped = line.strip()
        indentation = len(line) - len(line.lstrip())

        # If line has content, isn't a comment, isn't a list item, doesn't have a colon
        # and doesn't appear to be a continuation of a multi-line value:
        if (stripped and
            not stripped.startswith('#') and
            not stripped.startswith('-') and
            ':' not in stripped and
            not stripped.startswith('>') and
            not stripped.startswith('|') and
            not in_multiline):
            print(f"Line {i+1}: Potential missing colon - {stripped}")
            # Only add colon if this looks like a key (no spaces, all printable chars)
            if re.match(r'^[\w\-_]+$', stripped):
                line = line.rstrip() + ":\n"
                print(f"  Fixed: Added missing colon -> {line.strip()}")

        # Detect multi-line strings
        if ' >' in line or ' |' in line:
            in_multiline = True
            multiline_indent = len(line) - len(line.lstrip())

        # Ensure proper indentation in multi-line strings
        if in_multiline and line.strip() and not line.strip().startswith('#'):
            if len(line) - len(line.lstrip()) <= multiline_indent:
                if i > 0 and lines[i-1].strip() and not lines[i-1].strip().startswith('#'):
                    in_multiline = False

        fixed_lines.append(line)

    # Write the fixed file
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    print(f"Fixed file written to: {file_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_yaml.py <yaml_file>")
        sys.exit(1)

    success = fix_yaml_file(sys.argv[1])
    sys.exit(0 if success else 1)
