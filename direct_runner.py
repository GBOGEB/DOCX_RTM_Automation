#!/usr/bin/env python3
"""
Direct script runner - bypass any command runner issues
"""

import subprocess
import sys
from pathlib import Path


def run_json_analyzer_safe():
    """Run the JSON analyzer safely."""
    script_path = "json_file_analyzer_safe.py"

    if not Path(script_path).exists():
        print(f"❌ {script_path} not found")
        return 1

    print(f"🚀 Running {script_path} directly...")
    print("=" * 50)

    try:
        result = subprocess.run([sys.executable, script_path], check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def run_check_backup():
    """Run backup check and organization."""
    script_path = "check_backup_and_organize.py"

    if not Path(script_path).exists():
        print(f"❌ {script_path} not found")
        return 1

    print(f"🚀 Running {script_path} directly...")
    print("=" * 50)

    try:
        result = subprocess.run([sys.executable, script_path], check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def run_organize_project():
    """Run project organization."""
    script_path = "organize_project_structure.py"

    if not Path(script_path).exists():
        print(f"❌ {script_path} not found")
        return 1

    print(f"🚀 Running {script_path} directly...")
    print("=" * 50)

    try:
        result = subprocess.run([sys.executable, script_path], check=False)
        return result.returncode
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def main():
    """Main direct runner."""
    if len(sys.argv) < 2:
        print("🎯 Direct Script Runner")
        print("=" * 30)
        print("Available commands:")
        print("   python direct_runner.py json_analyzer")
        print("   python direct_runner.py check_backup")
        print("   python direct_runner.py organize")
        return 1

    command = sys.argv[1]

    if command == "json_analyzer":
        return run_json_analyzer_safe()
    elif command == "check_backup":
        return run_check_backup()
    elif command == "organize":
        return run_organize_project()
    else:
        print(f"❌ Unknown command: {command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
