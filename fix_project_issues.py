#!/usr/bin/env python3
"""
Fix Project Issues - Repair corrupted pyproject.toml and other issues
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def fix_pyproject_toml():
    """Fix the corrupted pyproject.toml file."""
    print("🔧 FIXING PYPROJECT.TOML")
    print("=" * 30)

    pyproject_path = Path("pyproject.toml")
    backup_path = Path(f"pyproject.toml.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    if pyproject_path.exists():
        # Create backup
        shutil.copy2(pyproject_path, backup_path)
        print(f"✅ Backup created: {backup_path}")

        # Check content
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.strip().startswith('@echo off') or 'batch' in content.lower():
                print("❌ Found batch script content in pyproject.toml")
                print("🔧 Replacing with proper TOML configuration...")
                create_proper_pyproject_toml()
                return True
            else:
                print("✅ pyproject.toml appears to have valid content")
                return False
        except Exception as e:
            print(f"❌ Error reading pyproject.toml: {e}")
            create_proper_pyproject_toml()
            return True
    else:
        print("⚠️ pyproject.toml not found, creating new one...")
        create_proper_pyproject_toml()
        return True

def create_proper_pyproject_toml():
    """Create a clean, proper pyproject.toml file."""
    toml_content = '''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "docx-rtm-automation"
version = "1.0.0"
description = "Document Requirements Traceability Matrix (RTM) Automation System"
authors = [
    {name = "RTM System", email = "rtm@automation.local"}
]
requires-python = ">=3.8"
dependencies = [
    "python-docx>=0.8.11",
    "markdown>=3.4.0",
    "beautifulsoup4>=4.11.0",
    "lxml>=4.9.0",
]

[project.scripts]
rtm-find-outputs = "find_output_files:main"
rtm-fix-issues = "fix_project_issues:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["*"]
exclude = ["tests*", "temp_*", "output*"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
'''

    with open("pyproject.toml", 'w', encoding='utf-8') as f:
        f.write(toml_content)
    print("✅ Created clean pyproject.toml")

def cleanup_problematic_files():
    """Clean up files that might cause parsing issues."""
    print("\n🧹 CLEANING PROBLEMATIC FILES")
    print("=" * 35)

    cleanup_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.tmp",
        ".mypy_cache",
        "*.pickle",
        "*.pkl"
    ]

    cleaned = 0
    for pattern in cleanup_patterns:
        if pattern.startswith("__") or pattern.startswith("."):
            # Directory patterns
            for path in Path('.').glob(f"**/{pattern}"):
                if path.is_dir():
                    try:
                        shutil.rmtree(path)
                        print(f"🗑️ Removed directory: {path}")
                        cleaned += 1
                    except Exception as e:
                        print(f"⚠️ Could not remove {path}: {e}")
        else:
            # File patterns
            for path in Path('.').glob(f"**/{pattern}"):
                if path.is_file():
                    try:
                        path.unlink()
                        print(f"🗑️ Removed file: {path}")
                        cleaned += 1
                    except Exception as e:
                        print(f"⚠️ Could not remove {path}: {e}")

    if cleaned > 0:
        print(f"✅ Cleaned up {cleaned} problematic files")
    else:
        print("✅ No problematic files found")

def main():
    """Main repair function."""
    print("🚨 RTM PROJECT EMERGENCY REPAIR")
    print("=" * 40)
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    issues_fixed = 0

    # Fix the main issue
    if fix_pyproject_toml():
        issues_fixed += 1

    # Clean up problematic files
    cleanup_problematic_files()

    print(f"\n🎉 REPAIR COMPLETE!")
    print(f"✅ Fixed {issues_fixed} critical issues")
    print()
    print("💡 NEXT STEPS:")
    print("   1. Restart VS Code to clear cached errors")
    print("   2. Run: python test_system_health.py")
    print("   3. Run: python find_output_files.py")
    print()
    print("🔄 If VS Code still shows errors, reload the window:")
    print("   Ctrl+Shift+P → 'Developer: Reload Window'")

if __name__ == "__main__":
    main()
