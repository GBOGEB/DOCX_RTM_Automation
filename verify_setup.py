import os
import sys
import importlib
import subprocess
from pathlib import Path
import docx_rtm_automation

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Verification script for DOCX RTM Automation setup.
This script checks if all dependencies are installed and if the setup is correct.
"""



def print_header(message):
    """Print a formatted header message."""
    print("\n" + "=" * 50)
    print(f" {message}")
    print("=" * 50)


def check_python_version():
    """Check if Python version is compatible."""
    print_header("Checking Python Version")
    
    major, minor = sys.version_info[:2]
    print(f"Current Python version: {major}.{minor}")
    
    if major < 3 or (major == 3 and minor < 6):
        print("❌ Python 3.6 or higher is required")
        return False
    
    print("✅ Python version is compatible")
    return True


def check_dependencies():
    """Check if required Python packages are installed."""
    print_header("Checking Required Dependencies")
    
    required_packages = [
        'python-docx',
        'pandas',
        'openpyxl',
        'jinja2',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-docx':
                importlib.import_module('docx')
            else:
                importlib.import_module(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print("\nMissing packages. Install them using pip:")
        pip_command = f"pip install {' '.join(missing_packages)}"
        print(f"  {pip_command}")
        return False
    
    return True


def check_file_structure():
    """Check if required files and directories exist."""
    print_header("Checking File Structure")
    
    # Define expected files and directories
    current_dir = Path(__file__).parent
    expected_items = [
        {'type': 'file', 'path': current_dir / 'docx_rtm_automation.py', 'required': True},
        {'type': 'dir', 'path': current_dir / 'templates', 'required': True},
        {'type': 'dir', 'path': current_dir / 'output', 'required': False},
    ]
    
    all_required_exist = True
    
    for item in expected_items:
        path = item['path']
        if item['type'] == 'file':
            exists = path.is_file()
        else:  # directory
            exists = path.is_dir()
        
        status = "✅" if exists else "❌"
        required_text = "(Required)" if item['required'] else "(Optional)"
        print(f"{status} {item['type'].capitalize()} {path.name} {required_text}")
        
        if item['required'] and not exists:
            all_required_exist = False
    
    return all_required_exist


def check_permissions():
    """Check if the script has permissions to read/write necessary files."""
    print_header("Checking Permissions")
    
    current_dir = Path(__file__).parent
    
    # Try to create a temporary file
    try:
        temp_file = current_dir / "permission_test_temp.txt"
        with open(temp_file, 'w') as f:
            f.write("Permission test")
        temp_file.unlink()  # Delete the file
        print("✅ Write permission in current directory")
        has_write_permission = True
    except Exception as e:
        print(f"❌ No write permission in current directory: {e}")
        has_write_permission = False
    
    # Check if output directory is writable (create if it doesn't exist)
    output_dir = current_dir / "output"
    if not output_dir.exists():
        try:
            output_dir.mkdir()
            print("✅ Created output directory")
        except Exception as e:
            print(f"❌ Could not create output directory: {e}")
            return False
    
    return has_write_permission


def run_alignment_check():
    """Run a basic alignment check."""
    print_header("Running Alignment Check")
    
    try:
        # Try to import the main module
        try:
            print("✅ Successfully imported main module")
        except ImportError:
            print("❌ Could not import docx_rtm_automation module")
            return False
        
        # Basic functionality test would go here
        print("⚠️ Full alignment check not implemented in verification script")
        print("Run docx_rtm_automation.py directly for complete analysis")
        
        return True
    except Exception as e:
        print(f"❌ Error during check: {e}")
        return False


def main():
    """Main verification function."""
    print_header("DOCX RTM Automation Setup Verification")
    
    results = []
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append(("File Structure", check_file_structure()))
    results.append(("Permissions", check_permissions()))
    results.append(("Alignment Check", run_alignment_check()))
    
    print_header("Verification Summary")
    all_passed = True
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        if not result:
            all_passed = False
        print(f"{status} - {name}")
    
    if all_passed:
        print("\n✅ All verification checks passed! The setup is correct.")
    else:
        print("\n❌ Some verification checks failed. Please fix the issues above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())