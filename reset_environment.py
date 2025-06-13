#!/usr/bin/env python3
"""
Reset Environment - Completely reset Python environment
"""

import sys
import subprocess
import os
import shutil
from pathlib import Path

def check_current_environment():
    """Check what environment we're currently in"""
    print("🔍 Current Environment Check")
    print("-" * 35)

    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version.split()[0]}")

    # Check if in virtual environment
    if ".venv" in sys.executable or "venv" in sys.executable:
        print("📋 Currently in virtual environment")
        return True
    else:
        print("📋 Using system Python")
        return False

def remove_virtual_environment():
    """Remove existing virtual environment"""
    print("\n🗑️  Removing Virtual Environment")
    print("-" * 35)

    venv_dirs = [".venv", "venv", "env"]
    removed = False

    for venv_dir in venv_dirs:
        venv_path = Path(venv_dir)
        if venv_path.exists():
            try:
                print(f"   Removing {venv_dir}/...")
                shutil.rmtree(venv_path)
                print(f"   ✅ Removed {venv_dir}/")
                removed = True
            except Exception as e:
                print(f"   ❌ Error removing {venv_dir}: {e}")
                print(f"   💡 Try manually: rmdir /s {venv_dir}")

    if not removed:
        print("   ℹ️  No virtual environment directories found")

    return removed

def create_fresh_virtual_environment():
    """Create a new virtual environment"""
    print("\n🏗️  Creating Fresh Virtual Environment")
    print("-" * 40)

    try:
        # Create new virtual environment
        print("   Creating .venv/...")
        result = subprocess.run([
            sys.executable, '-m', 'venv', '.venv'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("   ✅ Virtual environment created")

            # Get the new Python executable path
            if os.name == 'nt':  # Windows
                new_python = Path('.venv/Scripts/python.exe')
                activate_script = Path('.venv/Scripts/activate.bat')
            else:  # Unix/Linux/Mac
                new_python = Path('.venv/bin/python')
                activate_script = Path('.venv/bin/activate')

            if new_python.exists():
                print(f"   📍 New Python: {new_python}")
                print(f"   🔗 Activate with: {activate_script}")
                return str(new_python)
            else:
                print("   ❌ Virtual environment creation issue")
                return None
        else:
            print(f"   ❌ Virtual environment creation failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"   ❌ Error creating virtual environment: {e}")
        return None

def install_packages_in_new_env(python_executable):
    """Install packages in the new environment"""
    print("\n📦 Installing Packages in New Environment")
    print("-" * 45)

    packages = ['python-docx', 'requests']
    installed = 0

    for package in packages:
        try:
            print(f"   Installing {package}...")
            result = subprocess.run([
                python_executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✅ {package} installed successfully")
                installed += 1
            else:
                print(f"   ❌ Failed to install {package}")
                print(f"      Error: {result.stderr[:100]}...")

        except Exception as e:
            print(f"   ❌ Error installing {package}: {e}")

    print(f"\n📊 Installed {installed}/{len(packages)} packages")
    return installed == len(packages)

def test_new_environment(python_executable):
    """Test the new environment"""
    print("\n🧪 Testing New Environment")
    print("-" * 30)

    test_script = '''
import sys
print(f"Python: {sys.executable}")

# Test imports
test_results = {}
packages = ["docx", "requests", "json", "pathlib"]

for pkg in packages:
    try:
        __import__(pkg)
        test_results[pkg] = True
    except ImportError:
        test_results[pkg] = False

# Show results
for pkg, works in test_results.items():
    status = "✅" if works else "❌"
    print(f"{status} {pkg}")

working = sum(test_results.values())
total = len(test_results)
print(f"Working: {working}/{total}")

# Return exit code
sys.exit(0 if working >= 3 else 1)
'''

    try:
        result = subprocess.run([
            python_executable, '-c', test_script
        ], capture_output=True, text=True, timeout=30)

        print("   Test results:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"      {line}")

        return result.returncode == 0

    except Exception as e:
        print(f"   ❌ Error testing environment: {e}")
        return False

def use_system_python():
    """Setup to use system Python instead"""
    print("\n🌐 Using System Python")
    print("-" * 25)

    try:
        # Install packages with system Python
        packages = ['python-docx', 'requests']

        for package in packages:
            print(f"   Installing {package} globally...")
            result = subprocess.run([
                'python', '-m', 'pip', 'install', package
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✅ {package} installed")
            else:
                print(f"   ⚠️  {package} install issue (may already exist)")

        # Test system Python
        print("\n   Testing system Python...")
        result = subprocess.run([
            'python', '-c', 'import docx; print("✅ python-docx works")'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("   ✅ System Python is ready!")
            return True
        else:
            print("   ⚠️  System Python test had issues")
            return False

    except Exception as e:
        print(f"   ❌ Error with system Python: {e}")
        return False

def create_activation_instructions():
    """Create instructions for using the environment"""
    instructions = """
RTM AUTOMATION ENVIRONMENT SETUP COMPLETE
==========================================

OPTION 1: Use Virtual Environment (Recommended)
------------------------------------------------
1. Activate the environment:
   .venv\\Scripts\\activate    (Windows)
   source .venv/bin/activate  (Linux/Mac)

2. Run RTM automation:
   python main.py
   python create_test_document.py

3. When done, deactivate:
   deactivate

OPTION 2: Use System Python (Simple)
-------------------------------------
1. Make sure you're not in virtual environment:
   deactivate

2. Run RTM automation directly:
   python main.py
   python create_test_document.py

TESTING YOUR SETUP:
-------------------
python comprehensive_test.py     # Full system test
python main.py                   # Process DOCX files
python find_output_files.py      # Check results

Your RTM automation system is ready! 🚀
"""

    try:
        with open('environment_setup_instructions.txt', 'w', encoding='utf-8') as f:
            f.write(instructions)
        print("📋 Instructions saved to: environment_setup_instructions.txt")
    except Exception as e:
        print(f"⚠️  Could not save instructions: {e}")

def main():
    """Main function to reset environment"""
    print("🔄 RTM Automation - Environment Reset")
    print("=" * 45)
    print("Completely resetting Python environment for clean setup...\n")

    # Check current environment
    in_venv = check_current_environment()

    print("\nChoose your setup option:")
    print("1. Fresh virtual environment (isolated, recommended)")
    print("2. System Python (simple, global)")

    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        return 1

    if choice == "1":
        # Virtual environment approach
        if in_venv:
            print("\n⚠️  Please exit virtual environment first:")
            print("   deactivate")
            print("   python reset_environment.py")
            return 1

        # Remove old environment
        remove_virtual_environment()

        # Create fresh environment
        new_python = create_fresh_virtual_environment()

        if new_python:
            # Install packages
            if install_packages_in_new_env(new_python):
                # Test environment
                if test_new_environment(new_python):
                    print("\n🎉 SUCCESS! Fresh virtual environment ready!")
                    create_activation_instructions()
                    print("\nNext: Activate with .venv\\Scripts\\activate")
                    return 0
                else:
                    print("\n⚠️  Environment created but has issues")
                    return 1
            else:
                print("\n❌ Package installation failed")
                return 1
        else:
            print("\n❌ Virtual environment creation failed")
            return 1

    elif choice == "2":
        # System Python approach
        if in_venv:
            print("\n⚠️  Please exit virtual environment first:")
            print("   deactivate")
            print("   python reset_environment.py")
            return 1

        if use_system_python():
            print("\n🎉 SUCCESS! System Python is ready!")
            create_activation_instructions()
            print("\nNext: python main.py")
            return 0
        else:
            print("\n⚠️  System Python setup had issues")
            return 1

    else:
        print("\n❌ Invalid choice. Please run again and choose 1 or 2.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
