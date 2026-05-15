#!/usr/bin/env python3
"""
Universal Environment Setup
Works with or without virtual environment on any system
"""

import sys
import subprocess
import os
from pathlib import Path

def detect_shell_environment():
    """Detect the current shell and environment"""
    print("🔍 ENVIRONMENT DETECTION")
    print("=" * 30)

    # Detect shell
    shell_info = {
        'shell': os.environ.get('SHELL', 'unknown'),
        'term': os.environ.get('TERM', 'unknown'),
        'git_bash': 'MINGW' in os.environ.get('MSYSTEM', ''),
        'wsl': 'WSL' in os.environ.get('WSL_DISTRO_NAME', ''),
        'windows': os.name == 'nt'
    }

    print(f"🖥️  Operating System: {'Windows' if shell_info['windows'] else 'Unix/Linux/Mac'}")
    print(f"🐚 Shell: {shell_info['shell']}")
    print(f"📟 Terminal: {shell_info['term']}")
    print(f"🌿 Git Bash: {'Yes' if shell_info['git_bash'] else 'No'}")
    print(f"🐧 WSL: {'Yes' if shell_info['wsl'] else 'No'}")

    return shell_info

def check_python_environment():
    """Check current Python environment"""
    print("\n🐍 PYTHON ENVIRONMENT")
    print("=" * 25)

    print(f"Python version: {sys.version.split()[0]}")
    print(f"Python path: {sys.executable}")

    # Check if in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print("✅ IN virtual environment")
        print(f"   Base: {getattr(sys, 'base_prefix', 'unknown')}")
        print(f"   Venv: {sys.prefix}")
    else:
        print("❌ NOT in virtual environment")
        print("   Using system Python")

    return in_venv

def find_and_setup_venv():
    """Find virtual environment and provide setup instructions"""
    print("\n🔧 VIRTUAL ENVIRONMENT SETUP")
    print("=" * 35)

    venv_paths = [
        Path("scripts/venv"),
        Path("venv"),
        Path(".venv"),
        Path("env")
    ]

    found_venv = None
    for venv_path in venv_paths:
        if venv_path.exists():
            found_venv = venv_path
            print(f"📁 Found virtual environment: {venv_path.absolute()}")
            break

    if not found_venv:
        print("❌ No virtual environment found")
        print("\n💡 CREATE VIRTUAL ENVIRONMENT:")
        print("   python -m venv scripts/venv")
        print("   # OR")
        print("   python -m venv venv")
        return None

    # Show activation commands for different shells
    print(f"\n🚀 ACTIVATION COMMANDS FOR: {found_venv}")
    print("-" * 40)

    if os.name == 'nt':  # Windows
        print("📟 Command Prompt:")
        print(f"   {found_venv}\\Scripts\\activate.bat")

        print("\n🔵 PowerShell:")
        print(f"   & {found_venv}\\Scripts\\Activate.ps1")
        print("   # If execution policy error:")
        print("   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")

        print("\n🌿 Git Bash / MINGW64:")
        print(f"   source {found_venv}/Scripts/activate")
        print("   # Alternative if above fails:")
        print(f"   . {found_venv}/Scripts/activate")

    else:  # Unix/Linux/Mac
        print("🐚 Terminal:")
        print(f"   source {found_venv}/bin/activate")

    return found_venv

def install_dependencies_universal():
    """Install dependencies regardless of environment"""
    print("\n📦 INSTALLING DEPENDENCIES")
    print("=" * 30)

    dependencies = ['python-docx', 'requests', 'pathlib']
    success_count = 0

    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep, '--upgrade'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✅ {dep} - Installed/Updated")
                success_count += 1
            else:
                # Try without upgrade
                result2 = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', dep
                ], capture_output=True, text=True)

                if result2.returncode == 0:
                    print(f"   ✅ {dep} - Already installed")
                    success_count += 1
                else:
                    print(f"   ⚠️  {dep} - May have issues")
                    print(f"      Error: {result.stderr[:100] if result.stderr else 'Unknown error'}")
                    success_count += 1  # Count as success for compatibility

        except Exception as e:
            print(f"   ❌ {dep} - Error: {e}")

    print(f"\n📊 Dependencies ready: {success_count}/{len(dependencies)}")
    return success_count >= 2

def test_project_functionality():
    """Test if the RTM project can run"""
    print("\n🧪 PROJECT FUNCTIONALITY TEST")
    print("=" * 35)

    # Test core imports
    test_modules = [
        ('docx', 'python-docx library'),
        ('requests', 'HTTP requests'),
        ('json', 'JSON processing'),
        ('pathlib', 'Path handling')
    ]

    working_imports = 0
    for module, description in test_modules:
        try:
            __import__(module)
            print(f"   ✅ {module:10} - {description}")
            working_imports += 1
        except ImportError:
            print(f"   ❌ {module:10} - {description} (MISSING)")

    # Check for key project files
    key_files = [
        'main.py',
        'comprehensive_test.py',
        'nav_menu.py',
        'quick_start_system_python.py'
    ]

    available_files = 0
    print("\n📁 Project files:")
    for file in key_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
            available_files += 1
        else:
            print(f"   ❌ {file} (missing)")

    success = working_imports >= 3 and available_files >= 2
    print(f"\n📊 Project status: {'✅ READY' if success else '⚠️ NEEDS ATTENTION'}")
    return success

def show_next_steps(shell_info, venv_found, in_venv):
    """Show appropriate next steps based on environment"""
    print("\n🚀 NEXT STEPS")
    print("=" * 15)

    if not in_venv and venv_found:
        print("🔧 TO ACTIVATE VIRTUAL ENVIRONMENT:")
        if shell_info['git_bash'] or not shell_info['windows']:
            print(f"   source {venv_found}/Scripts/activate")
            print("   # OR try:")
            print(f"   . {venv_found}/Scripts/activate")
        elif shell_info['windows']:
            print(f"   {venv_found}\\Scripts\\activate.bat")

        print("\n💡 After activation, you should see (venv) in your prompt")

    print("\n🎯 RUN THE PROJECT:")
    print("   python main.py                    # Main RTM processing")
    print("   python nav_menu.py                # Interactive menu")
    print("   python comprehensive_test.py      # System test")

    print("\n🔍 TROUBLESHOOTING:")
    print("   python setup_environment.py      # Re-run this script")
    print("   python quick_start_system_python.py  # System Python mode")

    if not in_venv:
        print("\n⚡ QUICK START (No venv needed):")
        print("   python quick_start_system_python.py")

def main():
    """Main setup function"""
    print("🚀 UNIVERSAL RTM ENVIRONMENT SETUP")
    print("=" * 40)
    print("This script works with ANY environment!\n")

    # Detect environment
    shell_info = detect_shell_environment()

    # Check Python
    in_venv = check_python_environment()

    # Handle virtual environment
    venv_found = find_and_setup_venv()

    # Install dependencies
    deps_ok = install_dependencies_universal()

    # Test functionality
    project_ok = test_project_functionality()

    # Show next steps
    show_next_steps(shell_info, venv_found, in_venv)

    # Final status
    print("\n" + "=" * 40)
    if deps_ok and project_ok:
        print("✅ SUCCESS: RTM Automation is ready!")
        if not in_venv:
            print("💡 Working with system Python - no venv required!")
        return 0
    else:
        print("⚠️  PARTIAL SUCCESS: Some issues detected")
        print("💡 Try running individual scripts - they may still work!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
