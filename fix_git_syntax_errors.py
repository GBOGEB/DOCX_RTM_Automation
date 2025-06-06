#!/usr/bin/env python3
"""
Fix syntax errors that are blocking git commits
"""

import os
import sys
import ast
from pathlib import Path

def check_and_fix_syntax_errors():
    """Check and fix syntax errors in Python files."""
    print("🔧 Fixing Git Commit Syntax Errors")
    print("=" * 40)

    # Files that commonly have syntax errors
    files_to_check = [
        "agents/agent_common.py",
        "agents/__init__.py",
        "Project Requirements.py",
        "enhance_document_parsing.py",
        "digital_twin_parser.py"
    ]

    fixed_files = []

    for file_path in files_to_check:
        if not Path(file_path).exists():
            print(f"   ℹ️ File not found: {file_path}")
            continue

        print(f"   🔍 Checking {file_path}...")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to parse the file
            try:
                ast.parse(content)
                print(f"      ✅ Syntax OK")
            except SyntaxError as e:
                print(f"      ❌ Syntax error: {e}")

                # Try to fix common issues
                if "class Agent" in content and "class Agent:" not
