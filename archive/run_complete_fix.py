#!/usr/bin/env python3
"""
Run Complete Fix - Simple runner for syntax fixes
"""

import subprocess
import sys
import os

def main():
    """Run the complete syntax fix"""
    print("🚀 RTM Syntax Fix Runner")
    print("=" * 40)

    # Check if fix tool exists
    if not os.path.exists("complete_syntax_fix.py"):
        print("❌ complete_syntax_fix.py not found")
        print("Please ensure all files are in the correct directory")
        return 1

    try:
        # Run the syntax fix tool
        print("Running syntax fix tool...")
        result = subprocess.run([sys.executable, "complete_syntax_fix.py"],
                              capture_output=True, text=True)

        # Display output
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("Errors:", result.stderr)

        if result.returncode == 0:
            print("\n🎉 Syntax fix completed successfully!")
            print("\nYour RTM system is now syntax-error-free!")
        else:
            print(f"\n⚠️  Syntax fix completed with warnings (exit code: {result.returncode})")

        return result.returncode

    except Exception as e:
        print(f"❌ Error running syntax fix: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
