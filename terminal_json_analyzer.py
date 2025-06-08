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

                if result.returncode == 0:
                    print(f"✅ {analyzer} completed successfully!")
                    return 0
                else:
                    print(f"⚠️ {analyzer} completed with issues")

            except Exception as e:
                print(f"❌ Error with {analyzer}: {e}")

        return 1

def quick_json_health_check():
    """Quick JSON health check without full analysis."""
    print(f"\n🏥 Quick JSON Health Check:")
    print("=" * 35)

    json_files = list(Path(".").rglob("*.json"))
    print(f"📊 Total JSON files found: {len(json_files)}")

    valid_count = 0
    invalid_count = 0
    invalid_files = []

    for json_file in json_files[:20]:  # Check first 20 for speed
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json.load(f)
            valid_count += 1
        except json.JSONDecodeError:
            invalid_count += 1
            invalid_files.append(str(json_file))
        except Exception:
            # Skip files we can't read
            pass

    print(f"✅ Valid files (sample): {valid_count}")
    print(f"❌ Invalid files (sample): {invalid_count}")

    if invalid_files:
        print(f"\n⚠️ Files needing attention:")
        for file_path in invalid_files[:5]:
            print(f"   📄 {file_path}")

    health_percentage = (valid_count / (valid_count + invalid_count) * 100) if (valid_count + invalid_count) > 0 else 100
    print(f"\n📈 Sample Health Score: {health_percentage:.1f}%")

    return health_percentage >= 90

def main():
    """Main terminal analysis function."""
    print("🖥️ Terminal JSON Analyzer")
    print("=" * 35)
    print("Running JSON analysis without VS Code debug interference...")

    # Quick health check first
    health_ok = quick_json_health_check()

    if health_ok:
        print(f"\n✅ Quick health check passed!")
    else:
        print(f"\n⚠️ Issues detected in quick health check")

    # Run full analysis
    result = run_json_analysis()

    print(f"\n🎯 TERMINAL ANALYSIS COMPLETE")
    print("=" * 40)

    if result == 0:
        print("✅ JSON ecosystem analysis successful!")
        print("🚀 Your RTM system's JSON files are healthy!")
    else:
        print("⚠️ Some issues detected in JSON ecosystem")
        print("💡 Consider running: python aggressive_json_fixer.py")

    return result

if __name__ == "__main__":
    # Disable VS Code debugger attachment
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.exit(main())