#!/usr/bin/env python3
"""
Quick Code Quality Check - Balanced approach
Good balance of speed and thoroughness for regular development
"""

import subprocess
import sys
from pathlib import Path
import time

def quick_flake8_check():
    """Run a quick flake8 check with progress feedback."""
    print("🔍 Quick Code Quality Check")
    print("=" * 30)

    # Check if flake8 is available
    try:
        result = subprocess.run(["flake8", "--version"], capture_output=True, text=True)
        print(f"✅ flake8 available: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ flake8 not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "flake8"])

    print("\n📁 Checking key files...")

    # Check specific important files first
    key_files = [
        "enhance_document_parsing.py",
        "digital_twin_parser.py",
        "verify_system_status.py",
        "test_integration.py"
    ]

    total_issues = 0

    for file_path in key_files:
        if Path(file_path).exists():
            print(f"   Checking {file_path}...", end=" ")

            try:
                result = subprocess.run([
                    "flake8",
                    "--max-line-length=88",
                    "--extend-ignore=E203,W503,E501",
                    file_path
                ], capture_output=True, text=True, timeout=30)

                if result.stdout.strip():
                    issues = len(result.stdout.strip().split('\n'))
                    total_issues += issues
                    print(f"⚠️ {issues} issues")
                else:
                    print("✅ Clean")

            except subprocess.TimeoutExpired:
                print("⏰ Timeout")
            except Exception as e:
                print(f"❌ Error: {e}")
        else:
            print(f"   {file_path} not found")

    print(f"\n📊 Summary:")
    print(f"   Total issues found: {total_issues}")

    if total_issues == 0:
        print("   🎉 All checked files are clean!")
    elif total_issues < 10:
        print("   ✅ Good code quality (minor issues)")
    else:
        print("   ⚠️ Consider reviewing and fixing issues")

    return total_issues

def check_project_structure():
    """Check if project has expected structure."""
    print("\n🏗️ Project Structure Check:")

    expected_dirs = ["input", "output", "src"]
    expected_files = [
        "enhance_document_parsing.py",
        "digital_twin_parser.py",
        "Project Requirements.py"
    ]

    for directory in expected_dirs:
        if Path(directory).exists():
            print(f"   ✅ {directory}/ directory")
        else:
            print(f"   ❌ {directory}/ directory missing")

    for file_path in expected_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} missing")

def main():
    """Main function for quick quality check."""
    print("⚡ Quick Code Quality Check")
    print("=" * 30)
    print("💡 Tip: Use quality_check_light.py for fastest checks")
    print("💡 Tip: Use quality_check_heavy.py for comprehensive analysis")

    start_time = time.time()

    # Run quick checks
    total_issues = quick_flake8_check()
    check_project_structure()

    duration = time.time() - start_time
    print(f"\n⏱️ Check completed in {duration:.1f} seconds")

    # Return exit code based on issues found
    return 1 if total_issues > 20 else 0

if __name__ == "__main__":
    sys.exit(main())
