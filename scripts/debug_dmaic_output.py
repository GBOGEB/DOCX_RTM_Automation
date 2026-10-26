import sys
from pathlib import Path

# Add the project root to path if needed
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))


class DMAICDebugger:
    """Helper class to debug and examine DMAIC outputs"""

    # ... rest of the code remains the same ...
