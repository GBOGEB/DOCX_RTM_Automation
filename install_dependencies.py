#!/usr/bin/env python3
"""
Script to install required dependencies for RTM Automation
"""

import sys
import subprocess
import time
from pathlib import Path

# Required packages with versions
REQUIRED_PACKAGES = [
    "pyyaml>=6.0",
    "markdown-it-py>=3.0.0",
    "python-docx>=0.8.11",
    "openai>=1.6.0",
    "black>=23.9.1",
    "flake8>=6.1.0",
    "pre-commit>=3.5.0",
    "python-dotenv>=1.0.0",
]

# Optional packages
OPTIONAL_PACKAGES = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "matplotlib>=3.7.0",
    "requests>=2.31.0",
]


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def install_package(package, upgrade=False, quiet=False):
    """Install a Python package using pip"""
    start_time = time.time()
    print(f"Installing {package}...", end=" ", flush=True)

    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    if quiet:
        cmd.append("--quiet")
    cmd.append(package)

    try:
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )

        if result.returncode == 0:
            duration = time.time() - start_time
            print(f"✓ Done ({duration:.1f}s)")
            return True
        else:
            print("✗ Failed")
            print(f"  Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"✗ Failed (Exception: {str(e)})")
        return False


def ensure_venv_activated():
    """Check if running in virtual environment"""
    if not hasattr(sys, "real_prefix") and (
        not hasattr(sys, "base_prefix") or sys.base_prefix == sys.prefix
    ):
        print("Warning: Not running in a virtual environment!")
        choice = input("Continue anyway? (y/N): ").strip().lower()
        if choice != "y":
            sys.exit(1)


def main():
    """Main function"""
    print_section("RTM Automation Dependency Installer")

    # Check for virtual environment
    ensure_venv_activated()

    # Upgrade pip first
    print("Upgrading pip...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Install required packages
    print_section("Installing Required Packages")
    all_required_ok = True
    for package in REQUIRED_PACKAGES:
        if not install_package(package):
            all_required_ok = False

    if not all_required_ok:
        print("\nWarning: Some required packages failed to install!")
        print("The application may not function correctly.")
    else:
        print("\nAll required packages installed successfully!")

    # Ask about optional packages
    print_section("Optional Packages")
    print("The following packages are optional but may improve functionality:")
    for i, package in enumerate(OPTIONAL_PACKAGES, 1):
        print(f"  {i}. {package}")

    choice = input("\nInstall optional packages? (y/N): ").strip().lower()
    if choice == "y":
        for package in OPTIONAL_PACKAGES:
            install_package(package, quiet=True)

    # Create .env file for OpenAI API key if not exists
    print_section("Configuration")

    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)

    openai_key_file = config_dir / "openai_key.txt"

    if not openai_key_file.exists():
        print("Creating placeholder for OpenAI API key...")
        with open(openai_key_file, "w") as f:
            f.write("sk-your-openai-api-key-goes-here")
        print(f"Please update '{openai_key_file}' with your actual OpenAI API key")

    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write(f"OPENAI_API_KEY_FILE={str(openai_key_file)}\n")
            f.write("PYTHONPATH=${PROJECT_ROOT}\n")

    print_section("Installation Complete")
    print("You can now run the RTM automation pipeline:")
    print("  ./shell_scripts/run_rtm.sh")
    print("\nIf you encounter any issues, try running:")
    print("  ./shell_scripts/fix_critical_issues.sh")


if __name__ == "__main__":
    main()
