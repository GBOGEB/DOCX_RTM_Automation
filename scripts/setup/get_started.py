#!/usr/bin/env python3
"""
RTM Automation Project Development Guide
This script displays the available development tools and next steps.
"""

import os
import sys
import subprocess


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def check_tools():
    """Check for required development tools."""
    print_header("CHECKING DEVELOPMENT ENVIRONMENT")

    # Check Python
    print("Python:", sys.version)

    # Check Git
    try:
        git_version = subprocess.check_output(["git", "--version"], text=True).strip()
        print("Git:", git_version)
    except:
        print("Git: Not found")

    # Check virtual environment
    venv_active = hasattr(sys, "real_prefix") or sys.base_prefix != sys.prefix
    print("Virtual Environment:", "Active" if venv_active else "Not active")

    # Check for key Python packages
    packages = ["pandas", "pytest", "black", "ruff"]
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"{pkg}: Installed")
        except ImportError:
            print(f"{pkg}: Not installed")


def show_dev_tools():
    """Show available development tools."""
    print_header("AVAILABLE DEVELOPMENT TOOLS")

    tools = [
        ("Debugging", "Run VS Code debugger with F5 or use debug_helpers.py"),
        ("Testing", "Run tests with pytest or run_tests.sh/bat"),
        ("Linting/Formatting", "Use Black (formatting) and Ruff (linting)"),
        ("Git Hooks", "Pre-commit checks run automatically on commit"),
        ("Navigation", "Use goto_project.bat (Windows) or bash_nav.sh (Bash)"),
    ]

    for category, description in tools:
        print(f"{category:15} - {description}")


def suggest_next_steps():
    """Suggest next development steps."""
    print_header("RECOMMENDED NEXT STEPS")

    # Check for common directories
    dirs_to_check = ["src", "tests", "docs"]
    missing_dirs = [d for d in dirs_to_check if not os.path.isdir(d)]

    steps = []

    if missing_dirs:
        steps.append(f"Create missing directories: {', '.join(missing_dirs)}")

    steps.extend(
        [
            "Refactor code using the agents/ directory structure",
            "Add unit tests in tests/ directory",
            "Update documentation in docs/",
            "Use the dashboard for project management: python rtm_dashboard.py",
        ]
    )

    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")


def suggest_vs_code_extensions():
    """Suggest VS Code extensions for development."""
    print_header("RECOMMENDED VS CODE EXTENSIONS")

    extensions = [
        ("ms-python.python", "Python extension"),
        ("ms-python.vscode-pylance", "Pylance for Python language support"),
        ("ms-python.black-formatter", "Black formatter integration"),
        ("charliermarsh.ruff", "Ruff linter integration"),
        ("ms-python.debugpy", "Python debugger"),
        ("njpwerner.autodocstring", "Python docstring generator"),
        ("streetsidesoftware.code-spell-checker", "Spell checking"),
        ("mhutchie.git-graph", "Git graph visualization"),
    ]

    for ext_id, description in extensions:
        print(f"{ext_id:30} - {description}")


# Define check_system_dependencies at the module level
def check_system_dependencies():
    """Check for essential system dependencies."""
    print_header("CHECKING SYSTEM DEPENDENCIES")

    dependencies = [
        ("curl", "Command-line tool for transferring data"),
        ("wget", "Command-line utility for downloading files"),
        ("make", "Build automation tool"),
        ("gcc", "GNU Compiler Collection"),
    ]

    for dep, description in dependencies:
        try:
            # Using subprocess.run instead of check_output for better error handling
            # Adding shell=True for Windows compatibility
            result = subprocess.run(
                f"{dep} --version",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2  # Add timeout to prevent hanging
            )
            if result.returncode == 0:
                print(f"{dep:10} - Installed ({description})")
            else:
                print(f"{dep:10} - Not installed or not working ({description})")
        except (FileNotFoundError, subprocess.SubprocessError):
            print(f"{dep:10} - Not installed ({description})")
        except Exception as e:
            print(f"{dep:10} - Error checking: {str(e)} ({description})")


def main():
    """Main function."""
    print("\n📋 RTM AUTOMATION PROJECT DEVELOPMENT GUIDE 📋\n")
    print("This guide will help you get started with development tasks.")

    check_tools()
    show_dev_tools()
    suggest_next_steps()
    suggest_vs_code_extensions()
    check_system_dependencies()  # Call the new function here

    print_header("READY TO START")
    print("Your development environment is set up and ready for:")
    print("  - Debugging the application")
    print("  - Writing and running tests")
    print("  - Refactoring code")
    print("  - Adding new features")
    print("\nHappy coding!")


if __name__ == "__main__":
    main()
