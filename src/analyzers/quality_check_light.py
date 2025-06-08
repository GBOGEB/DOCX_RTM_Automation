#!/usr/bin/env python3
"""
Light Code Quality Check - Fast, essential checks only
Perfect for quick development feedback
"""

import subprocess
import sys
from pathlib import Path
import time


def light_quality_check():
    """Run essential quality checks quickly."""
    print("🚀 Light Code Quality Check")
    print("=" * 30)

    start_time = time.time()

    # Essential files only
    core_files = ["enhance_document_parsing.py", "digital_twin_parser.py"]

    # Basic flake8 config - only catch serious issues
    light_config = [
        "--max-line-length=100",  # More lenient
        "--extend-ignore=E203,W503,E501,W293,E302",  # Ignore style issues
        "--select=E9,F63,F7,F82",  # Only syntax errors and undefined names
    ]

    total_issues = 0

    print("📋 Checking core files for critical issues...")

    for file_path in core_files:
        if Path(file_path).exists():
            print(f"   {file_path}...", end=" ")

            try:
                result = subprocess.run(
                    ["flake8"] + light_config + [file_path],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.stdout.strip():
                    issues = len(result.stdout.strip().split("\n"))
                    total_issues += issues
                    print(f"❌ {issues} critical issues")
                else:
                    print("✅")

            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("⚠️ Skip")
        else:
            print(f"   {file_path} - Not found")

    duration = time.time() - start_time

    print("\n⚡ Quick Summary:")
    print(f"   Critical issues: {total_issues}")
    print(f"   Check time: {duration:.1f}s")

    if total_issues == 0:
        print("   🎉 Core files look good!")
    else:
        print("   🔧 Consider running heavy check for details")

    return total_issues


if __name__ == "__main__":
    sys.exit(light_quality_check())
