"""
This script attempts to install the pandas library if it's not already installed.
It's a utility for ensuring pandas is available for projects that depend on it.
"""
import subprocess
import sys

def install_pandas():
    """Installs the pandas library using pip."""
    try:
        # Try to import pandas to check if it's installed
        import pandas # pylint: disable=import-outside-toplevel, unused-import # noqa: F401
        print("pandas is already installed.")
    except ImportError:
        print("pandas not found. Attempting to install...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
            print("pandas installed successfully.")
        except Exception as e: # pylint: disable=broad-except
            print(f"Error installing pandas: {e}")
            sys.exit(1)

if __name__ == "__main__":
    install_pandas()
