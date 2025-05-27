import os
import sys
import logging
from pathlib import Path

# setup_imports.py
# This script sets up and verifies the required imports for the DOCX RTM Automation project.


# Add project-specific paths to the Python path if necessary
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Setup imports completed successfully.")

# Batch file content for ensuring Python modules can be found correctly
BATCH_FILE_CONTENT = """
@echo off
:: filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/run_script.bat
:: This batch file ensures that the Python modules can be found correctly

set PROJECT_ROOT=%~dp0
set PYTHONPATH=%PROJECT_ROOT%;%PYTHONPATH%

python %*
"""