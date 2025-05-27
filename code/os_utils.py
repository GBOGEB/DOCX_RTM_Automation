import os
from pathlib import Path
import logging

# Initialize logger for this module
logger = logging.getLogger(__name__)

# The function `resolve_relative_paths` that previously existed in this file
# (originally named import os.py) used `os.chdir()`.
# Using `os.chdir()` in scripts, especially those part of a pipeline, is
# generally discouraged because it changes the global Current Working Directory (CWD).
# This can lead to unpredictable behavior and make path management fragile,
# as other scripts or parts of the code might rely on a stable CWD.

# **Best Practice for Path Management in Pipeline Scripts:**
# 1. Determine a clear Project Root:
#    PROJECT_ROOT = Path(__file__).resolve().parent.parent  # (Adjust .parent calls as needed)
#
# 2. Construct all paths relative to this PROJECT_ROOT:
#    config_file = PROJECT_ROOT / "config" / "settings.yaml"
#    input_data_file = PROJECT_ROOT / "input" / "data.csv"
#    output_location = PROJECT_ROOT / "output" / "results"
#
# 3. Use `pathlib.Path` for robust and OS-agnostic path manipulations.
#
# 4. If a script needs to operate on files in its own directory, use:
#    SCRIPT_DIR = Path(__file__).resolve().parent
#    local_resource = SCRIPT_DIR / "resource.txt"

# As other scripts in the `code/` directory and the main pipeline runner
# have been updated to use this robust path management strategy,
# the `resolve_relative_paths` function is no longer necessary and has been removed
# to improve pipeline stability and predictability.

# This file (`os_utils.py`) can be used for other OS-related utility functions
# in the future, provided they do not rely on or cause CWD changes.

def get_project_root() -> Path:
    """
    Determines the project root directory.
    Assumes this script (`os_utils.py`) is in a subdirectory (e.g., 'code')
    of the main project directory.
    Adjust the number of .parent calls if the script's location changes.
    """
    # Example: If os_utils.py is in /project_root/code/
    project_root = Path(__file__).resolve().parent.parent
    return project_root

def ensure_dir_exists(dir_path: Path) -> bool:
    """
    Ensures a directory exists, creating it if necessary.
    Logs the action.
    Returns True if directory exists or was created, False otherwise.
    """
    try:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
        elif not dir_path.is_dir():
            logger.error(f"Path exists but is not a directory: {dir_path}")
            return False
        return True
    except OSError as e:
        logger.error(f"Error creating or accessing directory {dir_path}: {e}")
        return False

if __name__ == "__main__":
    # Configure basic logging for standalone execution/testing of this module
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("Testing os_utils.py...")

    root = get_project_root()
    logger.info(f"Determined Project Root: {root}")

    # Test ensure_dir_exists
    test_output_dir = root / "output" / "os_utils_test_dir"
    logger.info(f"Attempting to ensure directory exists: {test_output_dir}")
    if ensure_dir_exists(test_output_dir):
        logger.info(f"Successfully ensured directory exists: {test_output_dir}")
        # Example: Clean up the test directory
        # try:
        #     import shutil
        #     shutil.rmtree(test_output_dir)
        #     logger.info(f"Cleaned up test directory: {test_output_dir}")
        # except Exception as e:
        #     logger.error(f"Could not clean up test directory {test_output_dir}: {e}")
    else:
        logger.error(f"Failed to ensure directory exists: {test_output_dir}")

    logger.info("os_utils.py test finished.")

