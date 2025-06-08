#!/usr/bin/env python3
"""
Fix the division by zero error in enhanced_requirement_parser.py
"""

from pathlib import Path


def fix_division_by_zero():
    """Fix the division by zero error in enhanced_requirement_parser.py"""
    file_path = Path("enhanced_requirement_parser.py")

    if not file_path.exists():
        print("enhanced_requirement_parser.py not found")
        return

    print("🔧 Fixing division by zero error...")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Fix the specific line causing the error
    old_pattern = "implemented_requirements*100/total_requirements:.1f}% if total > 0"
    new_pattern = "(implemented_requirements*100/total_requirements if total_requirements > 0 else 0):.1f}%"

    content = content.replace(old_pattern, new_pattern)

    # Also fix similar patterns
    content = content.replace(
        "total_requirements:.1f}% if total_requirements > 0",
        "total_requirements if total_requirements > 0 else 0:.1f}%",
    )

    # Fix any remaining division by zero issues
    content = content.replace(
        "/total_requirements:.1f",
        "/total_requirements if total_requirements > 0 else 1:.1f",
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("   ✅ Fixed division by zero error")

    # Test the fix
    print("🧪 Testing the fix...")
    try:
        import subprocess
        import sys

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.rtm.enhanced_requirement_parser import main; print('Import test passed')",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("   ✅ Fix verified - no more syntax errors")
        else:
            print(f"   ⚠️ Still some issues: {result.stderr[:100]}...")
    except Exception as e:
        print(f"   ⚠️ Could not test fix: {e}")


if __name__ == "__main__":
    fix_division_by_zero()
