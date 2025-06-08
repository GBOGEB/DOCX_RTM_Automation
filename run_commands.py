#!/usr/bin/env python3
"""
Simple command runner for RTM system - handles common command issues
"""

import subprocess
import sys
from pathlib import Path

def run_command(command_name):
    """Run a specific RTM command."""
    commands = {
        "json_analyzer": "json_file_analyzer.py",
        "json_analyzer_safe": "json_file_analyzer_safe.py",
        "json_fixer": "json_file_fixer.py",
        "aggressive_fixer": "aggressive_json_fixer.py",
        "fix_specific": "fix_specific_json_files.py",
        "quality_check": "simple_quality_check.py",
        "process_docs": "process_real_documents.py",
        "web_dashboard": "rtm_web_dashboard.py",
        "celebration": "rtm_ecosystem_celebration.py",
        "port_monitor": "port_service_monitor_fixed.py",
        "git_commit": "simple_git_commit.py",
        "verify_health": "verify_json_health.py",
        "terminal_analyzer": "terminal_json_analyzer.py",
        "quick_health": "quick_health_check.py",
        "organize": "organize_project_structure.py",
        "check_backup": "check_backup_and_organize.py"
    }

    if command_name not in commands:
        print(f"❌ Unknown command: {command_name}")
        print(f"📋 Available commands:")
        for cmd, script in commands.items():
            exists = "✅" if Path(script).exists() else "❌"
            print(f"   {exists} {cmd:20} -> {script}")
        return 1

    script_path = commands[command_name]

    if not Path(script_path).exists():
        print(f"❌ Script not found: {script_path}")
        print(f"💡 Available scripts in directory:")

        # Show what Python files are actually available
        py_files = list(Path(".").glob("*.py"))
        for py_file in sorted(py_files):
            print(f"   📄 {py_file}")

        return 1

    print(f"🚀 Running: {script_path}")
    print("=" * 50)

    try:
        result = subprocess.run([sys.executable, script_path], check=False)
        print(f"\n✅ Command completed with exit code: {result.returncode}")
        return result.returncode
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return 1

def main():
    """Main command runner."""
    if len(sys.argv) != 2:
        print("🎯 RTM Command Runner")
        print("=" * 30)
        print("Usage: python run_commands.py <command_name>")
        print()
        print("📋 Quick commands:")
        print("   python run_commands.py json_analyzer_safe")
        print("   python run_commands.py verify_health")
        print("   python run_commands.py celebration")
        print("   python run_commands.py terminal_analyzer")
        print("   python run_commands.py quick_health")
        print("   python run_commands.py organize")
        print("   python run_commands.py check_backup")

        # Show available scripts
        print(f"\n📁 Available Python files:")
        py_files = list(Path(".").glob("*.py"))
        for py_file in sorted(py_files):
            print(f"   📄 {py_file}")

        return 1

    command_name = sys.argv[1]
    return run_command(command_name)

if __name__ == "__main__":
    sys.exit(main())