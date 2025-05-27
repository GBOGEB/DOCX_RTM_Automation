import os
from pathlib import Path
import logging


def resolve_relative_paths():
    """
    Ensure the script resolves paths relative to its own location.
    """
    # Determine the script directory and switch to it.
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    # Retrieve the logger for the current module.
    logger = logging.getLogger(__name__)
    logger.info(f"Working directory set to: {script_dir}")
    logger.debug(f"Debug: Current working directory is: {os.getcwd()}")


# ...existing code...
