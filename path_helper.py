#!/usr/bin/env python3
"""
Path Helper - Add src directory to Python path for organized imports
"""

import sys
from pathlib import Path

def setup_paths():
    """Add src directory to Python path."""
    src_path = Path(__file__).parent / "src"
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
        return True
    return False

# Auto-setup when imported
if __name__ != "__main__":
    setup_paths()

def main():
    """Manual path setup."""
    success = setup_paths()
    if success:
        print("✅ Python path configured for organized imports")
        print(f"📁 Added: {Path(__file__).parent / 'src'}")
    else:
        print("❌ Could not configure Python path")

if __name__ == "__main__":
    main()
