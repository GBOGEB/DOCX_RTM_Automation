#!/usr/bin/env python3
"""
Fix Environment - Resolve virtual environment and dependency issues
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_environment():
    """Check current Python environment"""
    print("🔍 Checking Python Environment")
    print("-" * 35)

    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")

    # Check if we're in a virtual environment
    venv_path = Path(sys.executable).parent.parent
    if ".venv" in str(venv_path) or "venv" in str(venv_path):
        print(f"✅ In virtual environment: {venv_path}")
        return True, venv_path
    else:
        print("ℹ️  Using system Python")
        return False, None

def fix_pip_in_venv(venv_path):
    """Fix pip in virtual environment"""
    print("\n🔧 Fixing pip in virtual environment")
    print("-" * 40)

    try:
        # Try to reinstall pip
        print("   Attempting to reinstall pip...")
        result = subprocess.run([
            sys.executable, '-m', 'ensurepip', '--upgrade'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("   ✅ pip reinstalled successfully")
            return True
        else:
            print(f"   ⚠️  ensurepip result: {result.stderr}")

            # Try alternative method
            print("   Trying alternative pip installation...")
            curl_result = subprocess.run([
                'curl', 'https://bootstrap.pypa.io/get-pip.py', '-o', 'get-pip.py'
            ], capture_output=True, text=True)

            if curl_result.returncode == 0:
                pip_result = subprocess.run([
                    sys.executable, 'get-pip.py'
                ], capture_output=True, text=True)

                if pip_result.returncode == 0:
                    print("   ✅ pip installed via get-pip.py")
                    # Clean up
                    try:
                        os.remove('get-pip.py')
                    except:
                        pass
                    return True

            return False

    except Exception as e:
        print(f"   ❌ Error fixing pip: {e}")
        return False

def test_pip_installation():
    """Test if pip is working"""
    print("\n🧪 Testing pip installation")
    print("-" * 30)

    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', '--version'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"   ✅ pip is working: {result.stdout.strip()}")
            return True
        else:
            print(f"   ❌ pip test failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"   ❌ Error testing pip: {e}")
        return False

def install_packages_directly():
    """Install packages using working pip"""
    print("\n📦 Installing required packages")
    print("-" * 35)

    packages = ['python-docx', 'requests']
    installed = 0

    for package in packages:
        try:
            print(f"   Installing {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"   ✅ {package} installed successfully")
                installed += 1
            else:
                print(f"   ❌ Failed to install {package}: {result.stderr[:100]}")

        except Exception as e:
            print(f"   ❌ Error installing {package}: {e}")

    print(f"\n📊 Installed {installed}/{len(packages)} packages")
    return installed == len(packages)

def test_imports():
    """Test if the installed packages can be imported"""
    print("\n🧪 Testing package imports")
    print("-" * 30)

    test_packages = {
        'docx': 'python-docx',
        'requests': 'requests',
        'json': 'built-in',
        'pathlib': 'built-in'
    }

    working = 0

    for module, package_name in test_packages.items():
        try:
            __import__(module)
            print(f"   ✅ {module} ({package_name})")
            working += 1
        except ImportError:
            print(f"   ❌ {module} ({package_name}) - Import failed")

    print(f"\n📊 Working imports: {working}/{len(test_packages)}")
    return working >= 3  # At least 3 out of 4 should work

def suggest_manual_fixes():
    """Suggest manual fixes if automatic fixes fail"""
    print("\n💡 Manual Fix Options")
    print("-" * 25)

    print("Option 1: Exit virtual environment and use system Python")
    print("   deactivate                    # Exit virtual environment")
    print("   pip install python-docx      # Install globally")
    print("   python main.py                # Run with system Python")

    print("\nOption 2: Recreate virtual environment")
    print("   deactivate                    # Exit current venv")
    print("   rmdir /s .venv                # Remove broken venv (Windows)")
    print("   python -m venv .venv          # Create new venv")
    print("   .venv\\Scripts\\activate        # Activate new venv")
    print("   pip install python-docx      # Install packages")

    print("\nOption 3: Use system Python directly")
    print("   python -m pip install python-docx  # Use system pip")
    print("   python main.py                      # Run directly")

def create_environment_report():
    """Create a report of the current environment"""
    print("\n📋 Creating Environment Report")
    print("-" * 35)

    report_content = f"""RTM AUTOMATION ENVIRONMENT REPORT
=====================================
Generated: {__import__('datetime').datetime.now().isoformat()}

PYTHON ENVIRONMENT:
- Python executable: {sys.executable}
- Python version: {sys.version}
- Working directory: {os.getcwd()}
- Virtual environment: {'.venv' in sys.executable}

SYSTEM INFO:
- Platform: {sys.platform}
- Path separator: {os.sep}

ENVIRONMENT VARIABLES:
- PATH: {os.environ.get('PATH', 'Not set')[:100]}...
- PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}
- VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Not set')}

RECOMMENDATIONS:
- If in broken virtual environment, recreate it
- Consider using system Python for simplicity
- Ensure pip is properly installed
"""

    try:
        with open('environment_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_content)
        print("   ✅ Report saved to environment_report.txt")
    except Exception as e:
        print(f"   ❌ Could not save report: {e}")

def main():
    """Main function to fix environment issues"""
    print("🔧 RTM Automation - Environment Fixer")
    print("=" * 45)
    print("Diagnosing and fixing Python environment issues...\n")

    # Check current environment
    in_venv, venv_path = check_python_environment()

    # If in virtual env with broken pip, try to fix it
    if in_venv:
        pip_working = test_pip_installation()

        if not pip_working:
            print("\n🔧 Attempting to fix virtual environment...")
            if fix_pip_in_venv(venv_path):
                pip_working = test_pip_installation()

        if pip_working:
            # Try to install packages
            if install_packages_directly():
                if test_imports():
                    print("\n🎉 SUCCESS! Environment fixed and packages installed!")
                    print("\nYou can now run:")
                    print("   python main.py")
                    print("   python create_test_document.py")
                    return 0

    # If we get here, automatic fixes didn't work
    print("\n⚠️  Automatic fixes were not successful")

    # Create diagnostic report
    create_environment_report()

    # Suggest manual fixes
    suggest_manual_fixes()

    print("\n🎯 Quick Test:")
    print("Try running: python main.py")
    print("Your system may still work with existing DOCX files!")

    return 1

if __name__ == "__main__":
    sys.exit(main())
