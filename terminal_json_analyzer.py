#!/usr/bin/env python3
"""
Terminal JSON Analyzer - Run JSON analysis without VS Code debug interference
"""

import json
import os
import subprocess
import sys
from pathlib import Path

def load_json(file_path):
    """Load JSON data from a file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, 'r') as file:
        return json.load(file)

def run_json_analysis():
    """Run JSON analysis in terminal mode."""
    print("🔍 Terminal JSON Analysis (VS Code Debug-Free)")
    print("=" * 55)

    # Check which JSON analyzer scripts are available
    analyzers = [
        "json_file_analyzer_safe.py",
        "json_file_analyzer.py",
        "verify_json_health.py"
    ]

    available_analyzers = []
    for analyzer in analyzers:
        if Path(analyzer).exists():
            available_analyzers.append(analyzer)
            print(f"   ✅ Found: {analyzer}")
        else:
            print(f"   ❌ Missing: {analyzer}")

    if not available_analyzers:
        print(f"\n❌ No JSON analyzer scripts found!")
        return 1

    # Run the safe analyzer first (best choice)
    if "json_file_analyzer_safe.py" in available_analyzers:
        print(f"\n🚀 Running safe JSON analyzer...")
        print("=" * 45)

        try:
            # Run in a clean subprocess to avoid VS Code debug issues
            result = subprocess.run(
                [sys.executable, "json_file_analyzer_safe.py"],
                cwd=Path.cwd(),
                check=False,
                capture_output=False,  # Let output go directly to terminal
                text=True
            )

            if result.returncode == 0:
                print(f"\n✅ JSON analysis completed successfully!")
            else:
                print(f"\n⚠️ Analysis completed with warnings (exit code: {result.returncode})")

            return result.returncode

        except Exception as e:
            print(f"❌ Error running analyzer: {e}")
            return 1

    else:
        print(f"\n⚠️ Safe analyzer not available, trying alternatives...")

        for analyzer in available_analyzers:
            try:
                print(f"\n🚀 Trying: {analyzer}")
                result = subprocess.run(
                    [sys.executable, analyzer],
                    cwd=Path.cwd(),
                    check=False,
                    capture_output=False,
                    text=True
                )
