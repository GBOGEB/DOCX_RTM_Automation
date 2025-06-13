#!/usr/bin/env python3
"""
Simple pre-commit hook for Python code quality checks.
This replaces the complex shell-based pre-commit hook.
"""

import os
import sys
import subprocess
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_command(cmd, cwd=None):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

        if result.returncode != 0:
            logger.error(f"Command failed: {cmd}")
            if result.stderr:
                logger.error(f"Error output: {result.stderr}")
            return False

        logger.info(f"✓ {cmd}")
        return True
    except Exception as e:
        logger.error(f"Failed to run command '{cmd}': {e}")
        return False


def check_python_syntax():
    """Check Python syntax for all staged Python files."""
    logger.info("Checking Python syntax...")

    # Get staged Python files
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        )
        files = result.stdout.strip().split("\n")
        python_files = [f for f in files if f.endswith(".py") and os.path.exists(f)]
    except subprocess.CalledProcessError:
        logger.warning("Could not get staged files, checking all Python files")
        python_files = list(Path(".").rglob("*.py"))

    if not python_files:
        logger.info("No Python files to check")
        return True

    success = True
    for file in python_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                compile(f.read(), file, "exec")
        except SyntaxError as e:
            logger.error(f"Syntax error in {file}: {e}")
            success = False
        except Exception as e:
            logger.error(f"Error checking {file}: {e}")
            success = False

    return success


def check_with_ruff():
    """Run Ruff linting if available."""
    # Check if ruff is available in PATH using cross-platform method
    if not shutil.which("ruff"):
        # Try to use from virtual environment
        ruff_path = Path(".venv/Scripts/ruff.exe")
        if not ruff_path.exists():
            ruff_path = Path(".venv/bin/ruff")

        if ruff_path.exists():
            # Focus on critical files only
            cmd = f'"{ruff_path}" check ascii_art.py simple_pre_commit_hook.py --select E9,F63,F7,F82'
        else:
            logger.info("Ruff not found, skipping linting")
            return True
    else:
        # Focus on critical files only
        cmd = "ruff check ascii_art.py simple_pre_commit_hook.py --select E9,F63,F7,F82"

    logger.info("Running Ruff linting...")
    return run_command(cmd)


def main():
    """Main pre-commit hook function."""
    logger.info("Running pre-commit checks...")

    checks = [
        ("Python syntax", check_python_syntax),
        ("Ruff linting", check_with_ruff),
    ]

    failed_checks = []

    for check_name, check_func in checks:
        logger.info(f"Running {check_name}...")
        if not check_func():
            failed_checks.append(check_name)

    if failed_checks:
        logger.error(f"Pre-commit checks failed: {', '.join(failed_checks)}")
        logger.error("Commit aborted. Please fix the issues and try again.")
        return 1

    logger.info("✓ All pre-commit checks passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
