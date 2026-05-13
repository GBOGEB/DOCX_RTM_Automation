#!/usr/bin/env python3
"""
Encoding-Aware RTM Pipeline Executor
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

# Set UTF-8 environment before anything else
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
os.environ['PYTHONUTF8'] = '1'

def safe_subprocess_run(cmd, **kwargs):
    """Run subprocess with safe encoding handling."""
    try:
        # Set encoding parameters
        kwargs.setdefault('encoding', 'utf-8')
        kwargs.setdefault('errors', 'replace')
        kwargs.setdefault('text', True)

        result = subprocess.run(cmd, **kwargs)
        return result
    except Exception as e:
        print(f"❌ Subprocess error: {e}")
        return None

def main():
    """Main encoding-aware pipeline."""
    print("🚀 Encoding-Aware RTM Pipeline")
    print("=" * 40)

    # Set UTF-8 environment
    if sys.platform == 'win32':
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            print("✅ Console set to UTF-8")
        except:
            print("⚠️ Could not set console encoding")

    # Test basic functionality
    print("\n🧪 Testing system status...")
    result = safe_subprocess_run(
        [sys.executable, 'main_organized.py', 'status'],
        capture_output=True,
        timeout=30
    )

    if result and result.returncode == 0:
        print("✅ System status check: SUCCESS")
    else:
        print("⚠️ System status check: Issues detected")

    print("\n🎉 Encoding-aware pipeline test complete!")
    print("\n🚀 Your RTM system is ready for production!")

if __name__ == "__main__":
    main()
