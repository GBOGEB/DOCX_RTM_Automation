#!/usr/bin/env python3
"""
Quick Run Fix - Simple fix runner with error handling
"""

import sys
import os

def main():
    """Run the encoding-aware syntax fix"""
    print("🚀 RTM Quick Syntax Fix")
    print("=" * 30)

    # Check if the v2 fix tool exists
    if os.path.exists("complete_syntax_fix_v2.py"):
        print("Running encoding-aware syntax fix...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, "complete_syntax_fix_v2.py"],
                                  capture_output=True, text=True, encoding='utf-8')

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print("Warnings/Errors:", result.stderr)

            return result.returncode

        except Exception as e:
            print(f"❌ Error running fix: {e}")
            print("Trying direct execution...")

            try:
                # Try direct execution
                exec(open("complete_syntax_fix_v2.py", encoding='utf-8').read())
                return 0
            except Exception as e2:
                print(f"❌ Direct execution also failed: {e2}")
                return 1
    else:
        print("❌ complete_syntax_fix_v2.py not found")
        return 1

if __name__ == "__main__":
    sys.exit(main())
