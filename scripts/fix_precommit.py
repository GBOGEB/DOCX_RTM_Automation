import os
import shutil
import subprocess
import time


def print_status(status, message):
    """Print formatted status messages"""
    status_colors = {
        "INFO": "\033[94m",  # Blue
        "SUCCESS": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "RESET": "\033[0m",  # Reset
    }

    # Windows CMD doesn't support ANSI color codes by default
    if os.name == "nt":
        print(f"[{status}] {message}")
    else:
        print(
            f"{status_colors.get(status, '')}{status}{status_colors['RESET']}: {message}"
        )


def clean_precommit_cache():
    """Clean pre-commit cache directories"""
    print_status("INFO", "Starting pre-commit cache cleanup...")

    # Paths to check
    cache_paths = [
        os.path.expanduser("~/.cache/pre-commit"),
        os.path.expanduser("~/new-pre-commit-cache"),
        os.path.expanduser("~/.cache/pre-commit-cache"),
    ]

    # List all repo directories in each cache location
    problematic_dirs = []

    for cache_path in cache_paths:
        if os.path.exists(cache_path):
            print_status("INFO", f"Found cache directory: {cache_path}")

            # Try to find repo* directories
            try:
                for item in os.listdir(cache_path):
                    if item.startswith("repo") and os.path.isdir(
                        os.path.join(cache_path, item)
                    ):
                        full_path = os.path.join(cache_path, item)
                        problematic_dirs.append(full_path)
                        print_status("INFO", f"Found repo directory: {full_path}")
            except Exception as e:
                print_status("WARNING", f"Error reading {cache_path}: {str(e)}")

    # Try to remove each problematic directory
    for dir_path in problematic_dirs:
        try:
            print_status("INFO", f"Removing directory: {dir_path}")
            shutil.rmtree(dir_path, ignore_errors=True)
            time.sleep(0.5)  # Small delay to ensure filesystem catches up

            # Check if removal was successful
            if not os.path.exists(dir_path):
                print_status("SUCCESS", f"Successfully removed {dir_path}")
            else:
                print_status("WARNING", f"Directory still exists: {dir_path}")
        except Exception as e:
            print_status("ERROR", f"Failed to remove {dir_path}: {str(e)}")

    # Run pre-commit clean
    try:
        print_status("INFO", "Running pre-commit clean...")
        result = subprocess.run(["pre-commit", "clean"], capture_output=True, text=True)
        print_status("INFO", f"pre-commit clean output: {result.stdout}")
    except Exception as e:
        print_status("ERROR", f"Error running pre-commit clean: {str(e)}")

    print_status("SUCCESS", "Pre-commit cache cleanup completed")
    print("\nNow try running your git commit command again:")
    print('git commit -m "Your commit message"')


if __name__ == "__main__":
    clean_precommit_cache()
