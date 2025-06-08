"""
Simple debugging test script to troubleshoot attachment issues.
"""

import sys
import time
import logging
import traceback

try:
    import debugpy
except ImportError:
    debugpy = None  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_debugging():
    """Run a simple test function to debug."""
    logger.info("Starting simple debug test")

    # Import debugpy here to avoid issues if it's not installed
    if debugpy is None:
        logger.error("debugpy module not found. Install with: pip install debugpy")
        return

    try:
        logger.info("debugpy successfully imported")

        # Configure debugpy to wait for the debugger
        logger.info("Enabling debugger on port 5678")
        debugpy.configure(python=sys.executable)  # Use the current Python interpreter
        debugpy.listen(("0.0.0.0", 5678))

        logger.info("Waiting for debugger to attach...")
        debugpy.wait_for_client()
        logger.info("Debugger attached!")

    except Exception as e:
        logger.error("Error setting up debugger: %s", e)
        traceback.print_exc()
        return

    # Once the debugger is attached, run some code to debug
    a = 10
    b = 5

    # Good place for a breakpoint
    result = a + b
    logger.info("Result: %s", result)

    # Loop for testing stepping through code
    for i in range(5):
        # Another good breakpoint location
        value = i * 10
        logger.info("Loop %s: value = %s", i, value)
        time.sleep(0.5)  # Slow down the loop for easier debugging

    logger.info("Debug test completed")


if __name__ == "__main__":
    print("\nSimple Debug Test")
    print("================\n")

    # Run the test
    test_debugging()

    print("\nTest completed. Press Enter to exit...")
    input()
