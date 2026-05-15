#!/usr/bin/env python3
"""
Install Dependencies - Ensure all required packages are installed
"""

import subprocess
import sys

def install_package(package_name):
    """Install a Python package using pip"""
    try:
        print(f"📦 Installing {package_name}...")
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', package_name],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ Successfully installed {package_name}")
            return True
        else:
            print(f"❌ Failed to install {package_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def check_package(package_name):
    """Check if a package is already installed"""
    try:
        __import__(package_name)
        print(f"✅ {package_name} is already installed")
        return True
    except ImportError:
        print(f"⚠️  {package_name} not found, will install")
        return False

def main():
    """Main function to install dependencies"""
    print("🔧 RTM Automation - Dependency Installer")
    print("=" * 45)
    print("Installing required packages for full functionality...\n")

    # Required packages
    packages = {
        'docx': 'python-docx',  # Import name vs package name
        'requests': 'requests',
        'pathlib': None,  # Built-in, no install needed
        'json': None,     # Built-in, no install needed
        'datetime': None  # Built-in, no install needed
    }

    installed_count = 0
    total_packages = len([p for p in packages.values() if p is not None])

    for import_name, package_name in packages.items():
        if package_name is None:
            print(f"✅ {import_name} is built-in (no installation needed)")
            continue

        if not check_package(import_name):
            if install_package(package_name):
                installed_count += 1
        else:
            installed_count += 1

    print(f"\n📊 Installation Summary: {installed_count}/{total_packages} packages ready")

    if installed_count == total_packages:
        print("\n🎉 All dependencies installed successfully!")
        print("\nYou can now:")
        print("1. python create_test_document.py   # Create test DOCX")
        print("2. python main.py                   # Run RTM pipeline")
        print("3. python find_output_files.py      # Check results")
        return 0
    else:
        print("\n⚠️  Some packages failed to install")
        print("You may need to install them manually:")
        print("pip install python-docx")
        return 1

if __name__ == "__main__":
    sys.exit(main())
