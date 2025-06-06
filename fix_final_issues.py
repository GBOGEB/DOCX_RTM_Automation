#!/usr/bin/env python3
"""
Fix the final minor formatting issues found by flake8.
"""

import subprocess
import sys
from pathlib import Path

def fix_formatting_issues():
    """Fix formatting issues using black and manual corrections."""
    print("🔧 Fixing Final Quality Issues")
    print("=" * 30)

    # Files with issues
    files_to_fix = [
        "verify_system_status.py",
        "test_integration.py"
    ]

    for file_path in files_to_fix:
        if Path(file_path).exists():
            print(f"📝 Fixing {file_path}...")

            try:
                # Run black to auto-fix formatting
                result = subprocess.run([
                    sys.executable, "-m", "black",
                    "--line-length=88",
                    file_path
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"   ✅ Black formatting applied")
                else:
                    print(f"   ⚠️ Black formatting issues: {result.stderr}")

                # Check remaining issues
                flake8_result = subprocess.run([
                    "flake8",
                    "--max-line-length=88",
                    "--extend-ignore=E203,W503,E501",
                    file_path
                ], capture_output=True, text=True)

                if flake8_result.stdout.strip():
                    remaining = len(flake8_result.stdout.strip().split('\n'))
                    print(f"   📊 Remaining issues: {remaining}")
                else:
                    print(f"   🎉 All issues fixed!")

            except Exception as e:
                print(f"   ❌ Error fixing {file_path}: {e}")
        else:
            print(f"   ❌ {file_path} not found")

    print("\n🎯 Final Quality Check:")
    # Run quick check again to see improvement
    try:
        result = subprocess.run([
            sys.executable, "quick_quality_check.py"
        ], capture_output=True, text=True, timeout=60)

        if "🎉 All checked files are clean!" in result.stdout:
            print("   🎉 Perfect! All issues resolved!")
        else:
            print("   📊 Check output for remaining issues")

    except Exception as e:
        print(f"   ⚠️ Could not run final check: {e}")

if __name__ == "__main__":
    fix_formatting_issues()
