#!/usr/bin/env python3
"""
Fix the 4 specific problematic JSON files identified in the RTM system
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

def fix_vscode_settings_json(file_path):
    """Fix VS Code settings.json files specifically."""
    print(f"\n🔧 Fixing VS Code settings: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create backup
        backup_path = backup_file(file_path)

        # Apply common VS Code settings fixes
        fixes_applied = []

        # Remove trailing commas before closing braces
        original = content
        content = re.sub(r',(\s*})', r'\1', content)
        if content != original:
            fixes_applied.append("Removed trailing commas")

        # Remove // comments (preserve strings)
        original = content
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            # Simple comment removal - avoid strings
            if '//' in line:
                # Check if // is in a string
                in_string = False
                quote_char = None
                for i, char in enumerate(line):
                    if char in ['"', "'"] and (i == 0 or line[i-1] != '\\'):
                        if not in_string:
                            in_string = True
                            quote_char = char
                        elif char == quote_char:
                            in_string = False
                            quote_char = None
                    elif char == '/' and i < len(line) - 1 and line[i+1] == '/' and not in_string:
                        line = line[:i].rstrip()
                        break
            cleaned_lines.append(line)

        content = '\n'.join(cleaned_lines)
        if content != original:
            fixes_applied.append("Removed comments")

        # Test if valid JSON now
        try:
            json.loads(content)
            print(f"   ✅ Fixed successfully!")
            print(f"   🛠️ Applied: {', '.join(fixes_applied)}")

            # Save fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except json.JSONDecodeError as e:
            print(f"   ❌ Still invalid: {e}")
            # Restore from backup
            shutil.copy2(backup_path, file_path)
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def fix_launch_json(file_path):
    """Fix launch.json files with unquoted property names."""
    print(f"\n🔧 Fixing launch.json: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create backup
        backup_path = backup_file(file_path)

        # Fix unquoted property names
        fixes_applied = []

        # Add quotes around unquoted keys
        original = content
        # Pattern to match unquoted keys (word followed by colon)
        content = re.sub(r'(\n\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', content)
        if content != original:
            fixes_applied.append("Added quotes around property names")

        # Remove trailing commas
        original = content
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        if content != original:
            fixes_applied.append("Removed trailing commas")

        # Test if valid JSON now
        try:
            json.loads(content)
            print(f"   ✅ Fixed successfully!")
            print(f"   🛠️ Applied: {', '.join(fixes_applied)}")

            # Save fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True

        except json.JSONDecodeError as e:
            print(f"   ❌ Still invalid: {e}")
            # Restore from backup
            shutil.copy2(backup_path, file_path)
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Fix the 4 specific problematic JSON files."""
    print("🛠️ RTM Specific JSON File Fixer")
    print("=" * 40)
    print("Fixing the 4 identified problematic JSON files...")

    # The 4 problematic files identified
    problematic_files = [
        (".vscode/settings.json", "settings"),
        (".ariana/.vscode/settings.json", "settings"),
        (".ariana/DOCX_RTM_Automation/.vscode/launch.json", "launch"),
        ("DOCX_RTM_Automation/.vscode/launch.json", "launch")
    ]

    fixed_count = 0
    failed_count = 0

    for file_path, file_type in problematic_files:
        path_obj = Path(file_path)

        if path_obj.exists():
            if file_type == "settings":
                success = fix_vscode_settings_json(file_path)
            elif file_type == "launch":
                success = fix_launch_json(file_path)
            else:
                print(f"\n⚠️ Unknown file type: {file_path}")
                success = False

            if success:
                fixed_count += 1
            else:
                failed_count += 1
        else:
            print(f"\n📄 File not found: {file_path}")

    # Summary
    print(f"\n📊 Fix Summary:")
    print(f"   ✅ Files fixed: {fixed_count}")
    print(f"   ❌ Files still problematic: {failed_count}")
    print(f"   📁 Files processed: {len(problematic_files)}")

    if failed_count == 0:
        print(f"\n🎉 All problematic JSON files have been fixed!")
        print(f"🚀 Your RTM system now has 100% JSON health!")
        print(f"\n💡 Next steps:")
        print(f"   • Run: python json_file_analyzer.py")
        print(f"   • Verify all JSON files are now valid")
        print(f"   • Commit your fixes: git add . && git commit -m 'Fixed JSON syntax issues'")
    else:
        print(f"\n⚠️ Some files still need manual attention")
        print(f"💡 Check the backup files to see original content")

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit(main())
