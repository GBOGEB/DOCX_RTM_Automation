#!/usr/bin/env python3
"""
System Health Test - Comprehensive system diagnostics
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def test_critical_issues():
    """Test for the critical pyproject.toml issue."""
    print("🚨 CRITICAL ISSUES CHECK")
    print("=" * 30)

    critical_issues = []

    # Check pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if pyproject_path.exists():
        try:
            with open(pyproject_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.strip().startswith('@echo off'):
                critical_issues.append("❌ pyproject.toml contains batch script content")
            elif len(content.strip()) == 0:
                critical_issues.append("❌ pyproject.toml is empty")
            else:
                print("✅ pyproject.toml content looks valid")
        except Exception as e:
            critical_issues.append(f"❌ Cannot read pyproject.toml: {e}")
    else:
        critical_issues.append("❌ pyproject.toml missing")

    # Check for pickle cache issues
    cache_dirs = [
        Path("__pycache__"),
        Path(".mypy_cache"),
    ]

    for cache_dir in cache_dirs:
        if cache_dir.exists():
            print(f"🧹 Found cache directory: {cache_dir}")

    if critical_issues:
        print("\n🚨 CRITICAL ISSUES FOUND:")
        for issue in critical_issues:
            print(f"   {issue}")
        print("\n💡 RUN THIS TO FIX: python fix_project_issues.py")
        return False
    else:
        print("✅ No critical issues detected")
        return True

def test_python_environment():
    """Test Python environment."""
    print("\n🐍 PYTHON ENVIRONMENT")
    print("=" * 25)

    print(f"✅ Python: {sys.version}")
    print(f"✅ Executable: {sys.executable}")
    print(f"✅ Working dir: {os.getcwd()}")

    # Test core modules
    modules = ['pathlib', 'json', 'datetime', 'logging']
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")

def test_file_structure():
    """Test project file structure."""
    print("\n📁 PROJECT STRUCTURE")
    print("=" * 25)

    expected_files = [
        'find_output_files.py',
        'fix_project_issues.py',
        'test_system_health.py',
    ]

    for file_name in expected_files:
        if Path(file_name).exists():
            print(f"✅ {file_name}")
        else:
            print(f"❌ {file_name}")

def main():
    """Run health check."""
    print("🏥 RTM SYSTEM HEALTH CHECK")
    print("=" * 40)
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test critical issues first
    if not test_critical_issues():
        print("\n⚠️ CRITICAL ISSUES DETECTED!")
        print("🔧 Please run: python fix_project_issues.py")
        return

    # Other tests
    test_python_environment()
    test_file_structure()

    print(f"\n🎯 HEALTH CHECK COMPLETE")
    print("✅ System appears healthy!")
    print("💡 You can now run: python find_output_files.py")

if __name__ == "__main__":
    main()
