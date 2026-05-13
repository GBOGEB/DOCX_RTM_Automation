#!/usr/bin/env python3
"""
JSON File Fixer - Fix common JSON parsing errors in RTM system files
"""

import json
from pathlib import Path
import re
import shutil
from datetime import datetime


def backup_file(file_path):
    """Create a backup of the file before fixing it."""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"   📋 Backup created: {backup_path}")
    return backup_path


def fix_json_syntax_errors(content):
    """Fix common JSON syntax errors."""
    fixes_applied = []

    # Remove trailing commas before closing brackets/braces
    original_content = content
    content = re.sub(r",(\s*[}\]])", r"\1", content)
    if content != original_content:
        fixes_applied.append("Removed trailing commas")

    # Fix missing quotes around keys (basic cases)
    original_content = content
    content = re.sub(r"(\w+)(\s*:\s*)", r'"\1"\2', content)
    if content != original_content:
        fixes_applied.append("Added quotes around unquoted keys")

    # Remove comments (// and /* */)
    original_content = content
    content = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    if content != original_content:
        fixes_applied.append("Removed comments")

    # Fix multiple JSON objects (add array wrapper)
    lines = content.strip().split("\n")
    brace_count = 0
    potential_objects = []
    current_object = []

    for line in lines:
        current_object.append(line)
        brace_count += line.count("{") - line.count("}")

        if (
            brace_count == 0
            and current_object
            and any("{" in l for l in current_object)
        ):
            potential_objects.append("\n".join(current_object))
            current_object = []

    if len(potential_objects) > 1:
        content = "[\n" + ",\n".join(potential_objects) + "\n]"
        fixes_applied.append("Wrapped multiple objects in array")

    return content, fixes_applied


def fix_specific_file(file_path):
    """Fix a specific JSON file."""
    print(f"\n🔧 Fixing: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            original_content = f.read()

        # Try to parse original content first
        try:
            json.loads(original_content)
            print("   ✅ File is already valid JSON")
            return True
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON Error: {e}")
            print("   🔧 Attempting to fix...")

            # Create backup
            backup_path = backup_file(file_path)

            # Apply fixes
            fixed_content, fixes_applied = fix_json_syntax_errors(original_content)

            # Test if fixes worked
            try:
                json.loads(fixed_content)
                print("   ✅ JSON fixed successfully!")
                print(f"   🛠️ Fixes applied: {', '.join(fixes_applied)}")

                # Save fixed content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

                return True

            except json.JSONDecodeError as e2:
                print(f"   ❌ Still invalid after fixes: {e2}")
                print("   📋 Manual intervention needed")

                # Restore from backup
                shutil.copy2(backup_path, file_path)
                return False

    except Exception as e:
        print(f"   ❌ Error processing file: {e}")
        return False


def analyze_problematic_json_files():
    """Find and analyze all problematic JSON files."""
    print("🔍 RTM JSON File Fixer")
    print("=" * 35)
    print("Scanning for JSON files with syntax errors...")

    problematic_files = []
    valid_files = []

    # Find all JSON files
    for json_file in Path(".").rglob("*.json"):
        if json_file.is_file():
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    content = f.read()

                try:
                    json.loads(content)
                    valid_files.append(json_file)
                except json.JSONDecodeError as e:
                    problematic_files.append((json_file, e))

            except Exception as e:
                print(f"   ⚠️ Could not read {json_file}: {e}")

    print("\n📊 JSON File Status:")
    print(f"   ✅ Valid JSON files: {len(valid_files)}")
    print(f"   ❌ Problematic files: {len(problematic_files)}")

    return problematic_files, valid_files


def fix_vscode_settings():
    """Specifically fix VS Code settings.json issues."""
    settings_file = Path(".vscode/settings.json")

    if not settings_file.exists():
        print("   ℹ️ VS Code settings.json not found")
        return True

    print("\n🔧 Fixing VS Code Settings:")
    print(f"   📄 File: {settings_file}")

    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            content = f.read()

        print(f"   📏 Original size: {len(content)} characters")

        # Common VS Code settings.json issues
        fixes = []

        # Remove trailing commas
        original = content
        content = re.sub(r",(\s*})", r"\1", content)
        if content != original:
            fixes.append("Removed trailing commas")

        # Remove comments
        original = content
        lines = content.split("\n")
        cleaned_lines = []
        for line in lines:
            # Remove // comments but preserve strings
            if "//" in line and not (
                '"' in line and line.index("//") > line.index('"')
            ):
                line = re.sub(r"//.*$", "", line)
            cleaned_lines.append(line)
        content = "\n".join(cleaned_lines)

        if content != original:
            fixes.append("Removed comments")

        # Test if valid now
        try:
            json.loads(content)
            print("   ✅ Settings fixed successfully!")

            if fixes:
                # Create backup and save
                backup_file(settings_file)
                with open(settings_file, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"   🛠️ Applied fixes: {', '.join(fixes)}")

            return True

        except json.JSONDecodeError as e:
            print(f"   ❌ Still invalid: {e}")
            print("   💡 Consider recreating VS Code settings")
            return False

    except Exception as e:
        print(f"   ❌ Error fixing VS Code settings: {e}")
        return False


def create_minimal_vscode_settings():
    """Create a minimal, valid VS Code settings.json file."""
    settings_file = Path(".vscode/settings.json")

    minimal_settings = {
        "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
        "python.terminal.activateEnvironment": True,
        "files.associations": {"*.json": "json", "*.yaml": "yaml", "*.yml": "yaml"},
        "editor.formatOnSave": True,
        "python.formatting.provider": "black",
    }

    try:
        # Ensure .vscode directory exists
        settings_file.parent.mkdir(exist_ok=True)

        # Create backup if file exists
        if settings_file.exists():
            backup_file(settings_file)

        # Write minimal settings
        with open(settings_file, "w", encoding="utf-8") as f:
            json.dump(minimal_settings, f, indent=2)

        print(f"   ✅ Created minimal VS Code settings: {settings_file}")
        return True

    except Exception as e:
        print(f"   ❌ Error creating settings: {e}")
        return False


def main():
    """Main JSON fixing function."""
    print("🛠️ RTM JSON File Fixer")
    print("=" * 35)
    print("Detecting and fixing JSON syntax errors...")

    # Analyze all JSON files
    problematic_files, valid_files = analyze_problematic_json_files()

    if not problematic_files:
        print("\n🎉 All JSON files are valid!")
        print(f"   Total files checked: {len(valid_files)}")
        return 0

    print("\n🔧 Fixing problematic files:")

    fixed_count = 0
    failed_count = 0

    for file_path, error in problematic_files:
        success = fix_specific_file(file_path)
        if success:
            fixed_count += 1
        else:
            failed_count += 1

    # Special handling for VS Code settings
    if any(".vscode/settings.json" in str(f[0]) for f in problematic_files):
        print("\n🔧 Special VS Code Settings Fix:")
        if not fix_vscode_settings():
            print("   💡 Creating minimal settings...")
            create_minimal_vscode_settings()

    # Summary
    print("\n📊 JSON Fix Summary:")
    print(f"   ✅ Files fixed: {fixed_count}")
    print(f"   ❌ Files still problematic: {failed_count}")
    print(f"   📁 Total JSON files: {len(valid_files) + len(problematic_files)}")

    if failed_count == 0:
        print("\n🎉 All JSON files are now valid!")
        print("🚀 Your RTM system's JSON ecosystem is healthy!")
    else:
        print("\n⚠️ Some files still need manual attention")
        print("💡 Check backup files for original content")

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    exit(main())
