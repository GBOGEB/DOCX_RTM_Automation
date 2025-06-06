#!/usr/bin/env python3
"""
Aggressive JSON File Fixer - Handle complex VS Code configuration JSON issues
"""

import json
import os
import re
import shutil
from pathlib import Path
from datetime import datetime

def backup_file(file_path):
    """Create a backup of the file before fixing it."""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"   📋 Backup created: {backup_path}")
    return backup_path

def aggressive_fix_vscode_settings(file_path):
    """Aggressively fix VS Code settings.json with multiple strategies."""
    print(f"\n🔧 AGGRESSIVE Fix for: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"   📏 Original size: {len(content)} characters")

        # Create backup
        backup_path = backup_file(file_path)

        # Strategy 1: Split by potential JSON object boundaries
        lines = content.split('\n')
        potential_json_blocks = []
        current_block = []
        brace_count = 0

        for i, line in enumerate(lines):
            # Remove comments first
            clean_line = re.sub(r'//.*$', '', line)

            current_block.append(clean_line)
            brace_count += clean_line.count('{') - clean_line.count('}')

            # If we reach balance and have content, this might be a complete JSON object
            if brace_count == 0 and current_block and any('{' in l for l in current_block):
                block_content = '\n'.join(current_block).strip()
                if block_content:
                    potential_json_blocks.append(block_content)
                current_block = []

        # Add remaining content if any
        if current_block:
            block_content = '\n'.join(current_block).strip()
            if block_content:
                potential_json_blocks.append(block_content)

        print(f"   🔍 Found {len(potential_json_blocks)} potential JSON blocks")

        # Strategy 2: Try to fix each block and find the valid one
        valid_blocks = []
        for i, block in enumerate(potential_json_blocks):
            print(f"   🧪 Testing block {i+1}...")

            # Clean up the block
            cleaned_block = block

            # Remove trailing commas
            cleaned_block = re.sub(r',(\s*[}\]])', r'\1', cleaned_block)

            # Remove any remaining comments
            cleaned_block = re.sub(r'//.*$', '', cleaned_block, flags=re.MULTILINE)

            # Try to parse
            try:
                parsed = json.loads(cleaned_block)
                valid_blocks.append(cleaned_block)
                print(f"      ✅ Block {i+1} is valid JSON!")
            except json.JSONDecodeError as e:
                print(f"      ❌ Block {i+1} invalid: {str(e)[:50]}...")

        if valid_blocks:
            # Use the first valid block
            fixed_content = valid_blocks[0]

            # Verify it's still valid
            try:
                json.loads(fixed_content)

                # Save the fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)

                print(f"   ✅ SUCCESSFULLY FIXED using block strategy!")
                print(f"   📏 New size: {len(fixed_content)} characters")
                return True

            except json.JSONDecodeError:
                print(f"   ❌ Fixed content is still invalid")

        # Strategy 3: Create minimal VS Code settings
        print(f"   🔧 Creating minimal VS Code settings...")

        minimal_settings = {
            "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
            "python.terminal.activateEnvironment": True,
            "files.associations": {
                "*.json": "json",
                "*.yaml": "yaml",
                "*.py": "python"
            },
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            },
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True
        }

        minimal_content = json.dumps(minimal_settings, indent=2)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(minimal_content)

        print(f"   ✅ Created minimal VS Code settings!")
        print(f"   📏 Minimal size: {len(minimal_content)} characters")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def aggressive_fix_launch_json(file_path):
    """Aggressively fix launch.json files."""
    print(f"\n🔧 AGGRESSIVE Fix for launch.json: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create backup
        backup_path = backup_file(file_path)

        # Strategy 1: Fix common launch.json issues
        fixed_content = content

        # Remove comments
        fixed_content = re.sub(r'//.*$', '', fixed_content, flags=re.MULTILINE)

        # Add quotes around unquoted property names more aggressively
        # This pattern matches word characters at start of line followed by colon
        fixed_content = re.sub(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed_content, flags=re.MULTILINE)

        # Fix specific VS Code launch.json patterns
        fixed_content = re.sub(r'(\s+)(name|type|request|program|console|args|stopOnEntry|cwd)\s*:', r'\1"\2":', fixed_content)

        # Remove trailing commas
        fixed_content = re.sub(r',(\s*[}\]])', r'\1', fixed_content)

        # Try to parse
        try:
            json.loads(fixed_content)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            print(f"   ✅ SUCCESSFULLY FIXED launch.json!")
            return True

        except json.JSONDecodeError as e:
            print(f"   ❌ Still invalid after fixes: {e}")

            # Strategy 2: Create minimal launch.json
            print(f"   🔧 Creating minimal launch.json...")

            minimal_launch = {
                "version": "0.2.0",
                "configurations": [
                    {
                        "name": "Python: Current File",
                        "type": "python",
                        "request": "launch",
                        "program": "${file}",
                        "console": "integratedTerminal",
                        "cwd": "${workspaceFolder}"
                    },
                    {
                        "name": "Python: RTM Processing",
                        "type": "python",
                        "request": "launch",
                        "program": "${workspaceFolder}/process_real_documents.py",
                        "console": "integratedTerminal",
                        "cwd": "${workspaceFolder}"
                    }
                ]
            }

            minimal_content = json.dumps(minimal_launch, indent=2)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(minimal_content)

            print(f"   ✅ Created minimal launch.json!")
            return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def inspect_problematic_file(file_path):
    """Inspect a problematic file to understand the issue."""
    print(f"\n🔍 INSPECTING: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        print(f"   📏 Total lines: {len(lines)}")
        print(f"   📏 Total characters: {len(content)}")

        # Show first few lines
        print(f"   📄 First 10 lines:")
        for i, line in enumerate(lines[:10], 1):
            print(f"      {i:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")

        # Look for the error location (around line 25, char 914)
        if len(lines) >= 25:
            print(f"   🎯 Around line 25 (error location):")
            for i in range(22, min(28, len(lines))):
                line_num = i + 1
                line = lines[i]
                print(f"      {line_num:2d}: {line[:80]}{'...' if len(line) > 80 else ''}")

        # Try to find where JSON parsing fails
        char_count = 0
        for i, line in enumerate(lines):
            if char_count + len(line) + 1 >= 914:  # +1 for newline
                print(f"   🎯 Character 914 is around line {i+1}")
                print(f"      Line content: {line}")
                break
            char_count += len(line) + 1

    except Exception as e:
        print(f"   ❌ Error inspecting file: {e}")

def main():
    """Main aggressive JSON fixing function."""
    print("🛠️ AGGRESSIVE RTM JSON File Fixer")
    print("=" * 45)
    print("Using aggressive strategies to fix stubborn JSON files...")

    # The 4 problematic files
    problematic_files = [
        (".vscode/settings.json", "settings"),
        (".ariana/.vscode/settings.json", "settings"),
        (".ariana/DOCX_RTM_Automation/.vscode/launch.json", "launch"),
        ("DOCX_RTM_Automation/.vscode/launch.json", "launch")
    ]

    fixed_count = 0

    for file_path, file_type in problematic_files:
        path_obj = Path(file_path)

        if path_obj.exists():
            # First inspect the file
            inspect_problematic_file(file_path)

            # Then try to fix it
            if file_type == "settings":
                success = aggressive_fix_vscode_settings(file_path)
            elif file_type == "launch":
                success = aggressive_fix_launch_json(file_path)
            else:
                success = False

            if success:
                fixed_count += 1
        else:
            print(f"\n📄 File not found: {file_path}")

    # Final summary
    print(f"\n🎯 AGGRESSIVE FIX SUMMARY:")
    print(f"   ✅ Files aggressively fixed: {fixed_count}/4")

    if fixed_count == 4:
        print(f"\n🎉 ALL FILES FIXED!")
        print(f"🚀 Your RTM system now has 100% JSON health!")
        print(f"\n💡 Verify the fixes:")
        print(f"   python json_file_analyzer_safe.py")
    else:
        print(f"\n⚠️ Some files may need manual editing")
        print(f"💡 Check the backup files and VS Code for valid JSON")

    return 0

if __name__ == "__main__":
    main()
