import os
import sys
import json
import time
from pprint import pprint
from pathlib import Path

# Add the project root to path if needed
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from dmaic import DMAICHandler, DMAICPhase, rerun_dmaic_with_openai
from config.openai_integration import initialize_openai
from utils.paths_manager import PathsManager
from utils.output_handler import OutputHandler

class DMAICDebugger:
    """Helper class to debug and examine DMAIC outputs"""

    # ... rest of the code remains the same ...