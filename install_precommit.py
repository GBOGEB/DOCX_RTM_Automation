#!/usr/bin/env python3
"""
Pre-commit installer and configurator for the RTM Automation project.
This script works across Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def run_command(command, capture_output=True):
    """Run a command and return result."""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(
            command, capture_output=capture_output, text=True, check=False
        )
        if result.returncode != 0:
            print(f"Command failed with code {result.returncode}")
            if capture_output:
                print(f"Output: {result.stdout}")
                print(f"Error: {result.stderr}")
        return result
    except Exception as e:
        print(f"Error executing command: {e}")
        return None


def install_precommit():
    """Install pre-commit package if not already installed."""
    print("\n=== Checking for pre-commit installation ===")

    # First check if pre-commit is installed
    try:
        import importlib.util

        precommit_spec = importlib.util.find_spec("pre_commit")
        if precommit_spec is not None:
            print("pre-commit is already installed.")
            return True
    except ImportError:
        pass

    print("Installing pre-commit...")
    result = run_command([sys.executable, "-m", "pip", "install", "pre-commit"])

    if result and result.returncode == 0:
        print("pre-commit installed successfully.")
        return True
    else:
        print("Failed to install pre-commit. Please install it manually:")
        print("  pip install pre-commit")
        return False


def create_precommit_config():
    """Create or update .pre-commit-config.yaml file."""
    print("\n=== Creating pre-commit configuration ===")

    config_path = Path(".pre-commit-config.yaml")

    if config_path.exists():
        print(".pre-commit-config.yaml already exists.")
        response = input("Do you want to replace it? (y/n): ")
        if response.lower() != "y":
            print("Keeping existing config file.")
            return

    config_content = """# Pre-commit Git hooks configuration
# See https://pre-commit.com for more information

repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files
        args: ['--maxkb=500']
    -   id: debug-statements
    -   id: check-merge-conflict

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        args: ["--profile", "black", "--filter-files"]

# Use our simple custom hook instead of framework hooks that have cache issues
-   repo: local
    hooks:
    -   id: custom-pre-commit
        name: Custom Pre-commit Hook
        entry: python check_precommit.py
        language: system
        pass_filenames: false
        always_run: true
        verbose: true
"""

    with open(config_path, "w") as f:
        f.write(config_content)

    print(f"Created {config_path}")


def create_check_script():
    """Create a simple Python script for pre-commit checks."""
    print("\n=== Creating simple pre-commit check script ===")

    script_path = Path("check_precommit.py")

    script_content = """#!/usr/bin/env python3
\"\"\"
Simple pre-commit check script that doesn't rely on pre-commit cache.
\"\"\"
import os
import re
import subprocess
import sys

def get_staged_files():
    \"\"\"Get list of staged files\"\"\"
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        return [f for f in result.stdout.strip().split('\\n') if f]
    except Exception as e:
        print(f"Error getting staged files: {e}")
        return []

def check_python_debug_prints(files):
    \"\"\"Check for debug print statements in Python files\"\"\"
    python_files = [f for f in files if f.endswith('.py')]
    issues = []

    for file_path in python_files:
        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if re.search(r'^\s*print\(', line):
                        issues.append(f"{file_path}:{i}: {line.strip()}")
        except Exception as e:
            print(f"Error checking {file_path}: {e}")

    return issues

def check_trailing_whitespace(files):
    \"\"\"Check for trailing whitespace\"\"\"
    issues = []

    for file_path in files:
        if not os.path.exists(file_path):
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    if re.search(r'[ \\t]+$', line):
                        issues.append(f"{file_path}:{i}: Trailing whitespace")
        except Exception as e:
            print(f"Error checking {file_path}: {e}")

    return issues

def check_large_files(files):
    \"\"\"Check for files over 500KB\"\"\"
    issues = []
    size_limit = 500 * 1024  # 500KB

    for file_path in files:
        if not os.path.exists(file_path):
            continue

        try:
            size = os.path.getsize(file_path)
            if size > size_limit:
                issues.append(f"{file_path}: File size is {size/1024:.2f}KB (limit: 500KB)")
        except Exception as e:
            print(f"Error checking {file_path}: {e}")

    return issues

def main():
    \"\"\"Run checks on staged files\"\"\"
    print("Running custom pre-commit checks...")

    staged_files = get_staged_files()
    if not staged_files:
        print("No staged files found.")
        return 0

    print(f"Checking {len(staged_files)} staged files...")

    debug_print_issues = check_python_debug_prints(staged_files)
    whitespace_issues = check_trailing_whitespace(staged_files)
    large_file_issues = check_large_files(staged_files)

    has_issues = False

    if debug_print_issues:
        print("\\nPossible debug print statements found:")
        for issue in debug_print_issues:
            print(f"  {issue}")
        has_issues = True

    if whitespace_issues:
        print("\\nTrailing whitespace found:")
        for issue in whitespace_issues:
            print(f"  {issue}")
        has_issues = True

    if large_file_issues:
        print("\\nLarge files found:")
        for issue in large_file_issues:
            print(f"  {issue}")
        has_issues = True

    if has_issues:
        print("\\nIssues were found. Please fix them before committing.")
        response = input("Do you want to proceed with the commit anyway? (y/n): ")
        if response.lower() != 'y':
            print("Commit aborted.")
            return 1

    print("All checks passed or issues acknowledged.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""

    with open(script_path, "w") as f:
        f.write(script_content)

    # Make executable
    try:
        os.chmod(script_path, 0o755)
    except:
        pass

    print(f"Created {script_path}")


def configure_env_variables():
    """Configure environment variables to use local pre-commit cache."""
    print("\n=== Configuring pre-commit environment ===")

    # Create .env file
    env_path = Path(".env")
    project_dir = os.path.abspath(".")
    cache_dir = os.path.join(project_dir, ".pre-commit-cache")
    temp_dir = os.path.join(project_dir, ".pre-commit-temp")

    env_content = f"""# pre-commit environment settings
PRE_COMMIT_HOME={cache_dir}
TMPDIR={temp_dir}
TEMP={temp_dir}
TMP={temp_dir}
"""

    with open(env_path, "w") as f:
        f.write(env_content)

    print(f"Created {env_path} with local cache settings")

    # Create directories
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(temp_dir, exist_ok=True)

    # Set environment variables for current process
    os.environ["PRE_COMMIT_HOME"] = cache_dir
    os.environ["TMPDIR"] = temp_dir
    os.environ["TEMP"] = temp_dir
    os.environ["TMP"] = temp_dir

    print(f"Created cache directory: {cache_dir}")
    print(f"Created temp directory: {temp_dir}")


def clean_cache_dirs():
    """Clean up existing pre-commit cache directories."""
    print("\n=== Cleaning pre-commit cache directories ===")

    # Remove project cache directory
    project_cache_dir = os.path.join(os.path.abspath("."), ".pre-commit-cache")
    if os.path.exists(project_cache_dir):
        print(f"Removing {project_cache_dir}...")
        try:
            shutil.rmtree(project_cache_dir)
            print(f"Removed {project_cache_dir}")
        except Exception as e:
            print(f"Error removing {project_cache_dir}: {e}")
    else:
        print(f"{project_cache_dir} does not exist")

    # Remove user cache directory
    user_cache_dir = os.path.join(os.path.expanduser("~"), "new-pre-commit-cache")
    if os.path.exists(user_cache_dir):
        print(f"Removing {user_cache_dir}...")
        try:
            shutil.rmtree(user_cache_dir)
            print(f"Removed {user_cache_dir}")
        except Exception as e:
            print(f"Error removing {user_cache_dir}: {e}")
    else:
        print(f"{user_cache_dir} does not exist")


def install_git_hooks():
    """Install the pre-commit hook."""
    print("\n=== Installing Git hooks ===")

    # Check if this is a git repository
    if not os.path.isdir(".git"):
        print(
            "Not a Git repository. Run this script from the root of your Git repository."
        )
        return False

    # Ensure .git/hooks directory exists
    hooks_dir = os.path.join(".git", "hooks")
    os.makedirs(hooks_dir, exist_ok=True)

    # Install hooks using pre-commit
    try:
        import pre_commit.main

        pre_commit.main.main(["install"])
        print("Pre-commit hooks installed via pre-commit framework.")
    except ImportError:
        print("Using direct hook installation...")

        # Create pre-commit hook file
        hook_path = os.path.join(hooks_dir, "pre-commit")

        # Determine if we're on Windows
        is_windows = platform.system() == "Windows"

        if is_windows:
            hook_content = f"""#!/bin/sh
# Simple pre-commit hook for RTM Automation
python {os.path.abspath("check_precommit.py")}
exit $?
"""
        else:
            hook_content = f"""#!/bin/sh
# Simple pre-commit hook for RTM Automation
python {os.path.abspath("check_precommit.py")}
exit $?
"""

        with open(hook_path, "w") as f:
            f.write(hook_content)

        # Make executable (may not work on Windows)
        try:
            os.chmod(hook_path, 0o755)
        except:
            pass

        print(f"Created hook at {hook_path}")

        # For Windows, also create a .bat version
        if is_windows:
            bat_path = os.path.join(hooks_dir, "pre-commit.bat")
            bat_content = f"""@echo off
REM Pre-commit hook for Windows
python "{os.path.abspath("check_precommit.py")}"
exit /b %ERRORLEVEL%
"""
            with open(bat_path, "w") as f:
                f.write(bat_content)

            print(f"Created Windows batch hook at {bat_path}")

    print("Git hooks installation completed")
    return True


def test_precommit():
    """Test if pre-commit is working."""
    print("\n=== Testing pre-commit ===")

    # Try running pre-commit directly
    try:
        import pre_commit.main

        print("Running pre-commit check using installed module...")
        try:
            pre_commit.main.main(["run", "--all-files"])
            print("Pre-commit checks completed successfully!")
        except SystemExit as e:
            if e.code == 0:
                print("Pre-commit checks completed successfully!")
            else:
                print(f"Pre-commit checks completed with code {e.code}")
    except ImportError:
        print("Running check script directly...")
        # Run the check script directly
        if os.path.exists("check_precommit.py"):
            result = run_command([sys.executable, "check_precommit.py"])
            if result and result.returncode == 0:
                print("Custom checks completed successfully!")
            else:
                print("Custom checks failed or had issues.")
        else:
            print("check_precommit.py not found. Skipping test.")


def main():
    print("=================================================")
    print("    Pre-commit Setup for RTM Automation")
    print("=================================================")

    # Make sure we're in the right directory
    if not os.path.exists("pyproject.toml") and not os.path.isdir(".git"):
        print("This script should be run from the root of the project.")
        print("Please cd to the project root directory first.")
        return 1

    # Clean cache dirs
    clean_cache_dirs()

    # Configure environment
    configure_env_variables()

    # Install pre-commit
    install_precommit()

    # Create configuration
    create_precommit_config()

    # Create check script
    create_check_script()

    # Install git hooks
    install_git_hooks()

    # Test pre-commit
    test_precommit()

    print("\n=================================================")
    print("Pre-commit setup completed!")
    print("")
    print("To check your staged files before a commit:")
    print("  python check_precommit.py")
    print("")
    print("Git will now automatically run checks before each commit.")
    print("=================================================")

    return 0


if __name__ == "__main__":
    sys.exit(main())
