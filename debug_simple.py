"""
Simple debugging test script to troubleshoot attachment issues.
"""
import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_debugging():
    """Run a simple test function to debug."""
    logger.info("Starting simple debug test")

    # Import debugpy here to avoid issues if it's not installed
    try:
        import debugpy
        logger.info("debugpy successfully imported")

        # Configure debugpy to wait for the debugger
        logger.info("Enabling debugger on port 5678")
        debugpy.configure(python=sys.executable)  # Use the current Python interpreter
        debugpy.listen(("0.0.0.0", 5678))

        logger.info("Waiting for debugger to attach...")
        debugpy.wait_for_client()
        logger.info("Debugger attached!")

    except ImportError:
        logger.error("debugpy module not found. Install with: pip install debugpy")
        return
    except Exception as e:
        logger.error(f"Error setting up debugger: {e}")
        import traceback
        traceback.print_exc()
        return

    # Once the debugger is attached, run some code to debug
    a = 10
    b = 5

    # Good place for a breakpoint
    result = a + b
    logger.info(f"Result: {result}")

    # Loop for testing stepping through code
    for i in range(5):
        # Another good breakpoint location
        value = i * 10
        logger.info(f"Loop {i}: value = {value}")
        time.sleep(0.5)  # Slow down the loop for easier debugging

    logger.info("Debug test completed")

if __name__ == "__main__":
    print("\nSimple Debug Test")
    print("================\n")

    # Run the test
    test_debugging()

    print("\nTest completed. Press Enter to exit...")
    input()
