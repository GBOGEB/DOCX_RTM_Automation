#!/usr/bin/env python3
"""
Complete Syntax Fix - Automatically fix syntax issues
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def fix_find_output_files():
    """Fix the find_output_files.py syntax issue"""
    print("🔧 Fixing find_output_files.py...")

    source_file = Path("find_output_files_fixed.py")
    target_file = Path("find_output_files.py")

    if source_file.exists():
        # Create backup
        if target_file.exists():
            backup_file = target_file.with_suffix(".py.backup")
            shutil.copy2(target_file, backup_file)
            print(f"   📋 Created backup: {backup_file}")

        # Replace with fixed version
        shutil.copy2(source_file, target_file)
        print("   ✅ Fixed find_output_files.py")
        return True
    else:
        print("   ❌ Fixed version not found")
        return False

def fix_shell_script():
    """Fix the shell script shebang issue"""
    print("🔧 Fixing quick_start.sh...")

    script_file = Path("quick_start.sh")

    if not script_file.exists():
        print("   ❌ quick_start.sh not found")
        return False

    try:
        # Read current content
        with open(script_file, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')

        # Check if shebang is properly formatted
        needs_fix = False
        if not lines[0].startswith('#!/bin/bash'):
            needs_fix = True
        elif len(lines) < 2 or 'shellcheck' not in lines[1]:
            needs_fix = True

        if needs_fix:
            # Create backup
            backup_file = script_file.with_suffix(".sh.backup")
            shutil.copy2(script_file, backup_file)
            print(f"   📋 Created backup: {backup_file}")

            # Fix the shebang and add shellcheck directive
            if not lines[0].startswith('#!/bin/bash'):
                lines.insert(0, '#!/bin/bash')

            # Add shellcheck directive if missing
            if len(lines) < 2 or 'shellcheck' not in lines[1]:
                lines.insert(1, '# shellcheck shell=bash')

            # Write fixed content
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            print("   ✅ Fixed shell script")
            return True
        else:
            print("   ✅ Shell script already correct")
            return True

    except Exception as e:
        print(f"   ❌ Error fixing shell script: {e}")
        return False

def verify_fixes():
    """Verify that fixes worked"""
    print("\n🔍 Verifying fixes...")

    success = True

    # Test Python syntax
    try:
        import ast
        with open("find_output_files.py", 'r') as f:
            content = f.read()
        ast.parse(content)
        print("   ✅ find_output_files.py syntax valid")
    except Exception as e:
        print(f"   ❌ find_output_files.py still has issues: {e}")
        success = False

    # Test shell script
    shell_file = Path("quick_start.sh")
    if shell_file.exists():
        with open(shell_file, 'r') as f:
            first_line = f.readline().strip()

        if first_line == '#!/bin/bash':
            print("   ✅ quick_start.sh shebang correct")
        else:
            print(f"   ❌ quick_start.sh shebang issue: {first_line}")
            success = False

    return success

def main():
    """Main function"""
    print("🔧 Complete Syntax Fix Tool")
    print("=" * 50)
    print("Automatically fixing syntax issues in RTM system files\n")

    fixes_applied = 0

    # Fix Python file
    if fix_find_output_files():
        fixes_applied += 1

    # Fix shell script
    if fix_shell_script():
        fixes_applied += 1

    # Verify fixes
    print("\n" + "=" * 50)
    if verify_fixes():
        print("🎉 All syntax issues have been resolved!")
        print(f"✅ Applied {fixes_applied} fixes successfully")

        print("\n📁 Backup files created:")
        for backup in Path(".").glob("*.backup"):
            print(f"   • {backup}")

        print("\n💡 You can now run:")
        print("   python find_output_files.py")
        print("   ./quick_start.sh")
        print("   python syntax_checker.py")

        return 0
    else:
        print("⚠️  Some issues may still remain")
        print("Please check the error messages above")
        return 1

if __name__ == "__main__":
    exit(main())
