#!/usr/bin/env python3
"""
Check Environment - Quick environment status and activation guide
"""

import sys
import os
from pathlib import Path
import subprocess

def check_current_python():
    """Check current Python environment"""
    print("🐍 CURRENT PYTHON ENVIRONMENT")
    print("=" * 40)

    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Working directory: {os.getcwd()}")

    # Check if in virtual environment
    if "venv" in sys.executable or ".venv" in sys.executable:
        print("✅ Currently in virtual environment")
        venv_active = True
    else:
        print("ℹ️  Using system Python")
        venv_active = False

    return venv_active

def check_available_venvs():
    """Check for available virtual environments"""
    print("\n📁 AVAILABLE VIRTUAL ENVIRONMENTS")
    print("=" * 40)

    venv_paths = [
        Path(".venv"),
        Path("venv"),
        Path("env"),
        Path("scripts/venv")
    ]

    found_venvs = []

    for venv_path in venv_paths:
        if venv_path.exists():
            # Check if it's a valid virtual environment
            if os.name == 'nt':  # Windows
                python_exe = venv_path / "Scripts" / "python.exe"
                activate_script = venv_path / "Scripts" / "activate.bat"
            else:  # Unix/Linux/Mac
                python_exe = venv_path / "bin" / "python"
                activate_script = venv_path / "bin" / "activate"

            if python_exe.exists():
                print(f"✅ Found: {venv_path}/")
                print(f"   Python: {python_exe}")
                print(f"   Activate: {activate_script}")
                found_venvs.append(venv_path)
            else:
                print(f"⚠️  Invalid: {venv_path}/ (missing Python executable)")
        else:
            print(f"❌ Not found: {venv_path}/")

    return found_venvs

def show_activation_commands(found_venvs):
    """Show correct activation commands"""
    print("\n🚀 ACTIVATION COMMANDS")
    print("=" * 30)

    if found_venvs:
        for venv_path in found_venvs:
            print(f"\nFor {venv_path}/:")
            if os.name == 'nt':  # Windows
                print(f"   {venv_path}\\Scripts\\activate")
                print(f"   # or")
                print(f"   call {venv_path}\\Scripts\\activate.bat")
            else:  # Unix/Linux/Mac
                print(f"   source {venv_path}/bin/activate")
    else:
        print("No virtual environments found.")
        print("\nCreate one with:")
        print("   python -m venv .venv")
        if os.name == 'nt':
            print("   .venv\\Scripts\\activate")
        else:
            print("   source .venv/bin/activate")

def test_dependencies():
    """Test if required dependencies are available"""
    print("\n📦 DEPENDENCY CHECK")
    print("=" * 25)

    dependencies = ['docx', 'requests', 'json', 'pathlib']
    working = 0

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
            working += 1
        except ImportError:
            print(f"❌ {dep} - Not available")

    print(f"\nWorking: {working}/{len(dependencies)}")

    if working < len(dependencies):
        print("\nInstall missing dependencies:")
        print("   pip install python-docx requests")

    return working == len(dependencies)

def show_quick_commands():
    """Show quick commands to get started"""
    print("\n⚡ QUICK START COMMANDS")
    print("=" * 30)

    print("Without virtual environment:")
    print("   python main.py                    # Run RTM pipeline")
    print("   python comprehensive_test.py      # Test system")
    print("   python nav_menu.py                # Interactive menu")

    print("\nWith virtual environment:")
    print("   .venv\\Scripts\\activate            # Activate (Windows)")
    print("   source .venv/bin/activate         # Activate (Linux/Mac)")
    print("   python main.py                    # Run RTM pipeline")
    print("   deactivate                        # Exit when done")

def main():
    """Main function"""
    print("🔍 RTM AUTOMATION - ENVIRONMENT CHECKER")
    print("=" * 50)
    print("Checking your Python environment and virtual environments...\n")

    # Check current Python
    venv_active = check_current_python()

    # Check available virtual environments
    found_venvs = check_available_venvs()

    # Show activation commands
    show_activation_commands(found_venvs)

    # Test dependencies
    deps_ok = test_dependencies()

    # Show quick commands
    show_quick_commands()

    # Final recommendations
    print("\n🎯 RECOMMENDATIONS")
    print("=" * 20)

    if venv_active:
        print("✅ You're in a virtual environment")
        if deps_ok:
            print("✅ Dependencies are installed")
            print("👉 Ready to run: python main.py")
        else:
            print("👉 Install dependencies: pip install python-docx requests")
    else:
        if found_venvs:
            print("👉 Activate virtual environment first, then run RTM automation")
        else:
            if deps_ok:
                print("✅ System Python has dependencies")
                print("👉 Ready to run: python main.py")
            else:
                print("👉 Install dependencies: pip install python-docx requests")
                print("👉 Then run: python main.py")

if __name__ == "__main__":
    main()
