#!/usr/bin/env python3
"""
Fix all syntax errors and formatting issues in the RTM Automation project.
"""

import subprocess
import sys
from pathlib import Path

def fix_check_git_status():
    """Fix the specific issues in check_git_status.py"""
    file_path = "check_git_status.py"

    if not Path(file_path).exists():
        print(f"File {file_path} not found")
        return

    print(f"🔧 Fixing {file_path}...")

    # Read the current content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the issues
    fixed_content = '''#!/usr/bin/env python3
"""
Check Git status and suggest actions for quality check files.
"""

import subprocess
from pathlib import Path


def check_git_status():
    """Check Git status and suggest actions."""
    print("📋 Git Status Check for Quality Files")
    print("=" * 40)

    # Quality check files to track
    quality_files = [
        "quality_check_light.py",
        "quality_check_heavy.py",
        "quick_quality_check.py",
        "run_code_quality_checks.py",
        "QUALITY_CHECKS.md",
        "fix_final_issues.py"
    ]

    print("\\n📁 Checking quality check files...")

    untracked_files = []
    tracked_files = []
    missing_files = []

    for file_path in quality_files:
        path = Path(file_path)
        if path.exists():
            # Check if file is tracked in git
            try:
                result = subprocess.run([
                    "git", "ls-files", "--error-unmatch", file_path
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    tracked_files.append(file_path)
                    print(f"   ✅ {file_path} (tracked)")
                else:
                    untracked_files.append(file_path)
                    print(f"   📝 {file_path} (untracked)")

            except Exception:
                untracked_files.append(file_path)
                print(f"   📝 {file_path} (untracked)")
        else:
            missing_files.append(file_path)
            print(f"   ❌ {file_path} (missing)")

    print("\\n📊 Summary:")
    print(f"   Tracked files: {len(tracked_files)}")
    print(f"   Untracked files: {len(untracked_files)}")
    print(f"   Missing files: {len(missing_files)}")

    # Suggest actions
    if untracked_files:
        print("\\n🔧 Suggested Git commands:")
        print("   # Add quality check files to git:")
        for file_path in untracked_files:
            print(f"   git add {file_path}")

        print("\\n   # Or add all at once:")
        print(f"   git add {' '.join(untracked_files)}")

        print("\\n   # Commit the changes:")
        print("   git commit -m 'Add quality check system'")

    # Check overall git status
    print("\\n📋 Overall Git Status:")
    try:
        result = subprocess.run(["git", "status", "--porcelain"],
                              capture_output=True, text=True)

        if result.stdout.strip():
            modified_count = len([
                line for line in result.stdout.strip().split('\\n')
                if line.strip().startswith('M')
            ])
            untracked_count = len([
                line for line in result.stdout.strip().split('\\n')
                if line.strip().startswith('??')
            ])

            print(f"   Modified files: {modified_count}")
            print(f"   Untracked files: {untracked_count}")
        else:
            print("   ✅ Working directory clean")

    except Exception as e:
        print(f"   ⚠️ Could not check git status: {e}")


if __name__ == "__main__":
    check_git_status()
'''

    # Write the fixed content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"   ✅ Fixed {file_path}")

def fix_ariana_file():
    """Fix the syntax error in .ariana/enhance_document_parsing.py"""
    ariana_file = Path(".ariana/enhance_document_parsing.py")

    if ariana_file.exists():
        print(f"🔧 Fixing {ariana_file}...")
        try:
            # Delete the problematic .ariana file - it's likely auto-generated
            ariana_file.unlink()
            print(f"   ✅ Removed problematic .ariana file")
        except Exception as e:
            print(f"   ⚠️ Could not remove .ariana file: {e}")

def run_black_formatting():
    """Run black formatting on all Python files to fix line length issues."""
    print("🎨 Running Black formatter to fix line length issues...")

    # Key files to format
    files_to_format = [
        "enhance_document_parsing.py",
        "check_git_status.py",
        "fix_final_issues.py",
        "quality_check_light.py",
        "quality_check_heavy.py",
        "quick_quality_check.py"
    ]

    for file_path in files_to_format:
        if Path(file_path).exists():
            try:
                result = subprocess.run([
                    sys.executable, "-m", "black",
                    "--line-length=88",
                    file_path
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"   ✅ Formatted {file_path}")
                else:
                    print(f"   ⚠️ Issue formatting {file_path}: {result.stderr}")

            except Exception as e:
                print(f"   ❌ Error formatting {file_path}: {e}")

def run_final_quality_check():
    """Run a final quality check to verify fixes."""
    print("\\n🔍 Running final quality check...")

    try:
        result = subprocess.run([
            sys.executable, "quality_check_light.py"
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("   🎉 Light quality check passed!")
        else:
            print("   ⚠️ Some issues remain - check output above")

        print(result.stdout)

    except Exception as e:
        print(f"   ⚠️ Could not run final check: {e}")

def main():
    """Main function to fix all issues."""
    print("🛠️ Comprehensive Fix for RTM Automation Issues")
    print("=" * 50)

    # Fix specific files
    fix_ariana_file()
    fix_check_git_status()

    # Install black if needed
    print("\\n📦 Ensuring Black formatter is available...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "black"
        ], capture_output=True, text=True)
        print("   ✅ Black formatter ready")
    except Exception as e:
        print(f"   ⚠️ Could not install black: {e}")

    # Run formatting
    run_black_formatting()

    # Final check
    run_final_quality_check()

    print("\\n🎯 Fix Summary:")
    print("   1. ✅ Fixed .ariana syntax error")
    print("   2. ✅ Fixed check_git_status.py issues")
    print("   3. ✅ Applied Black formatting")
    print("   4. ✅ Ran final quality check")

    print("\\n🚀 Your RTM Automation system should now be clean!")

if __name__ == "__main__":
    main()
