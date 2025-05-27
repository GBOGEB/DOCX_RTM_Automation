import sys

def check_package(package):
    try:
        __import__(package)
        return True, None
    except ImportError:
        try:
            spec = importlib.util.find_spec(package)
            if spec is None:
                return False, f"Required package '{package}' is not installed or not found in the environment"
            else:
                return False, f"Package '{package}' found but could not be imported properly. Check for conflicts or installation issues."
        except Exception as e:
            return False, f"Error while checking package '{package}': {str(e)}"

def main():
    import importlib.util

    required_packages = ['yaml', 'markdown']
    optional_packages = ['numpy', 'pandas']
    missing_packages = []
    errors = []

    print("Checking required packages...")
    for package in required_packages:
        is_installed, error = check_package(package)
        if not is_installed:
            missing_packages.append(package)
            errors.append(error)

    print("\nChecking optional packages...")
    for package in optional_packages:
        is_installed, error = check_package(package)
        if not is_installed:
            print(f"Optional package '{package}' is not installed. You may want to install it.")

    print("\nSummary:")
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"- {package}")
    else:
        print("All required packages are installed.")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"- {error}")

    print("\nPython Environment Info:")
    print(f"Python Version: {sys.version}")
    print(f"Executable: {sys.executable}")

if __name__ == "__main__":
    main()
                # Removed redundant and misaligned code block.
