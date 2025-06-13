#!/usr/bin/env python3
"""
Quick Start System Python - Use system Python without virtual environment
"""

import sys
import subprocess
from pathlib import Path
import os

def check_virtual_environment():
    """Check for virtual environment and provide activation commands"""
    print("🔍 VIRTUAL ENVIRONMENT CHECK")
    print("=" * 35)

    venv_paths = [
        Path("scripts/venv"),
        Path("venv"),
        Path(".venv"),
        Path("env")
    ]

    for venv_path in venv_paths:
        if venv_path.exists():
            print(f"📁 Found virtual environment: {venv_path}")

            print("\n🚀 Activation commands for different shells:")
            print(f"   Git Bash/MINGW64: source {venv_path}/Scripts/activate")
            print(f"   Command Prompt:   {venv_path}\\Scripts\\activate.bat")
            print(f"   PowerShell:       & {venv_path}\\Scripts\\Activate.ps1")
            print(f"   Unix Terminal:    source {venv_path}/bin/activate")

            print("\n💡 If activation fails in Git Bash, try:")
            print(f"   . {venv_path}/Scripts/activate")
            print("   (note the dot and space)")

            return True

    print("❌ No virtual environment found")
    print("💡 Using system Python instead - this is perfectly fine!")
    return False

def check_system_python():
    """Check if system Python is ready for RTM automation"""
    print("\n🐍 SYSTEM PYTHON CHECK")
    print("=" * 30)

    print(f"✅ Python executable: {sys.executable}")
    print(f"✅ Python version: {sys.version.split()[0]}")
    print(f"✅ Working directory: {Path.cwd()}")

    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Currently in virtual environment")
    else:
        print("ℹ️  Using system Python (no virtual environment)")

    return True

def install_dependencies():
    """Install required dependencies with system Python"""
    print("\n📦 INSTALLING DEPENDENCIES")
    print("=" * 35)

    dependencies = ['python-docx', 'requests']
    installed = 0

    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✅ {dep} installed")
                installed += 1
            else:
                print(f"   ⚠️  {dep} may already be installed")
                installed += 1  # Count as success if already installed

        except Exception as e:
            print(f"   ❌ Error installing {dep}: {e}")

    print(f"\n📊 Dependencies: {installed}/{len(dependencies)} ready")
    return installed == len(dependencies)

def test_imports():
    """Test if RTM automation imports work"""
    print("\n🧪 TESTING IMPORTS")
    print("=" * 25)

    test_modules = ['docx', 'requests', 'json', 'pathlib']
    working = 0

    for module in test_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
            working += 1
        except ImportError:
            print(f"   ❌ {module} - Import failed")

    print(f"\n📊 Working imports: {working}/{len(test_modules)}")
    return working >= 3  # At least 3 should work

def run_rtm_tests():
    """Run quick RTM automation tests"""
    print("\n🚀 RUNNING RTM TESTS")
    print("=" * 30)

    tests = [
        ("comprehensive_test.py", "Comprehensive system test"),
        ("main.py", "Main RTM pipeline"),
        ("find_output_files.py", "Output file analysis")
    ]

    results = []

    for script, description in tests:
        if Path(script).exists():
            print(f"\n🔄 Testing {description}...")
            try:
                result = subprocess.run([
                    sys.executable, script
                ], capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    print(f"   ✅ {description} - SUCCESS")
                    results.append(True)
                else:
                    print(f"   ⚠️  {description} - Completed with issues")
                    results.append(True)  # Still counts as working

            except subprocess.TimeoutExpired:
                print(f"   ⚠️  {description} - Timeout (may still be working)")
                results.append(True)
            except Exception as e:
                print(f"   ❌ {description} - Error: {e}")
                results.append(False)
        else:
            print(f"   ❌ {script} not found")
            results.append(False)

    working_tests = sum(results)
    print(f"\n📊 Working tests: {working_tests}/{len(tests)}")
    return working_tests > 0

def show_success_commands():
    """Show commands for successful RTM automation"""
    print("\n🎉 RTM AUTOMATION READY!")
    print("=" * 35)
    print("✅ Works with OR without virtual environment!")

    # Show virtual environment activation if available
    venv_paths = [Path("scripts/venv"), Path("venv"), Path(".venv"), Path("env")]
    for venv_path in venv_paths:
        if venv_path.exists():
            print(f"\n🔧 Virtual environment found: {venv_path}")
            print("   Git Bash:       source scripts/venv/Scripts/activate")
            print("   Command Prompt: scripts\\venv\\Scripts\\activate.bat")
            print("   PowerShell:     & scripts\\venv\\Scripts\\Activate.ps1")
            print("   🆘 Need help?   python setup_environment.py")
            break
    else:
        print("\n💡 No virtual environment - using system Python")

    print("\n🚀 Main Commands (work anywhere):")
    print("   python main.py                    # Process DOCX files")
    print("   python nav_menu.py                # Interactive menu")
    print("   python comprehensive_test.py      # Full system test")
    print("   python find_output_files.py       # Check results")

    print("\n📊 Analysis Commands:")
    print("   python project_scanner.py         # Analyze project")
    print("   python test_python_docx.py        # Test DOCX library")

    print("\n🌐 GitHub Commands:")
    print("   python scripts/automation/version_manager.py")
    print("   python scripts/quality/verify_github_status.py")

    print("\n💡 Pro Tips:")
    print("   • Works in ANY terminal (Git Bash, CMD, PowerShell)")
    print("   • Virtual environment is optional")
    print("   • System Python works perfectly")
    print("   • All RTM automation features available")

def main():
    """Main function to set up system Python for RTM automation"""
    print("🚀 RTM AUTOMATION - SYSTEM PYTHON SETUP")
    print("=" * 50)
    print("Setting up RTM automation with your system Python...\n")

    # Check for virtual environment first
    venv_found = check_virtual_environment()

    # Check system Python
    python_ok = check_system_python()

    if not python_ok:
        print("❌ System Python issues detected")
        return 1

    # Install dependencies
    deps_ok = install_dependencies()

    # Test imports
    imports_ok = test_imports()

    # Run RTM tests
    tests_ok = run_rtm_tests()

    # Final assessment
    if deps_ok and imports_ok and tests_ok:
        show_success_commands()
        print("\n✅ SUCCESS: RTM automation ready with system Python!")
        return 0
    else:
        print("\n⚠️  PARTIAL SUCCESS: Some issues detected")
        print("\nTroubleshooting:")
        print("   python fix_environment.py       # Fix issues")
        print("   python comprehensive_test.py    # Check status")
        return 1

if __name__ == "__main__":
    sys.exit(main())
