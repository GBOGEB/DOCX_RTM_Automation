# filepath: /C:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/code/main.py
# ...existing code...
import os
import logging
from pathlib import Path


def resolve_relative_paths():
    """
    Ensure the script resolves paths relative to its own location.
    """
    try:
        script_dir = Path(__file__).parent.resolve()
    except NameError:
        # Fallback for environments where __file__ is not defined
        script_dir = Path(os.getcwd()).resolve()
    os.chdir(script_dir)
    logging.getLogger(__name__).info(f"Working directory set to: {script_dir}")
    logging.getLogger(__name__).debug(
        f"Current working directory: {os.getcwd()}")


# ...existing code...
