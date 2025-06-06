#!/usr/bin/env python3
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

    print("\n📁 Checking quality check files...")

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

    print("\n📊 Summary:")
    print(f"   Tracked files: {len(tracked_files)}")
    print(f"   Untracked files: {len(untracked_files)}")
    print(f"   Missing files: {len(missing_files)}")

    # Suggest actions
    if untracked_files:
        print("\n🔧 Suggested Git commands:")
        print("   # Add quality check files to git:")
        for file_path in untracked_files:
            print(f"   git add {file_path}")

        print("\n   # Or add all at once:")
        print(f"   git add {' '.join(untracked_files)}")

        print("\n   # Commit the changes:")
        print("   git commit -m 'Add quality check system'")

    # Check overall git status
    print("\n📋 Overall Git Status:")
    try:
        result = subprocess.run(["git", "status", "--porcelain"],
                              capture_output=True, text=True)

        if result.stdout.strip():
            modified_count = len([
                line for line in result.stdout.strip().split('\n')
                if line.strip().startswith('M')
            ])
            untracked_count = len([
                line for line in result.stdout.strip().split('\n')
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
