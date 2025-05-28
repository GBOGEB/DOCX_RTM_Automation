#!/usr/bin/env python3
"""
Simple script to install PyYAML package.
"""
import subprocess
import sys
import os

def install_pyyaml():
    """Install PyYAML package."""
    print("Installing PyYAML...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        print("PyYAML installed successfully.")
        return True
    except Exception as e:
        print(f"Error installing PyYAML: {e}")
        return False

def verify_installation():
    """Verify that PyYAML is installed and working."""
    try:
        import yaml
        print(f"PyYAML version {yaml.__version__} is installed.")

        # Create a simple YAML test
        test_data = {"test": "success", "nested": {"value": 123}}
        yaml_str = yaml.dump(test_data)
        loaded_data = yaml.safe_load(yaml_str)

        if loaded_data == test_data:
            print("PyYAML working correctly - successfully dumped and loaded test data.")
            return True
        else:
            print("PyYAML test failed - loaded data doesn't match original!")
            return False
    except ImportError:
        print("Failed to import yaml module. Installation may have failed.")
        return False
    except Exception as e:
        print(f"PyYAML verification failed: {e}")
        return False

def main():
    """Main entry point."""
    # Check if virtual environment is active
    in_venv = hasattr(sys, 'real_prefix') or sys.base_prefix != sys.prefix

    if not in_venv:
        print("Warning: Not running in a virtual environment!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted. Please activate a virtual environment first.")
            return 1

    # Install PyYAML
    if not install_pyyaml():
        return 1

    # Verify installation
    if not verify_installation():
        return 1

    print("\nYou can now import yaml in your Python scripts.")
    print("Example usage:\n")
    print("import yaml")
    print("data = yaml.safe_load(open('config.yaml'))")
    print("yaml.dump(data, open('output.yaml', 'w'))")

    return 0

if __name__ == "__main__":
    sys.exit(main())
