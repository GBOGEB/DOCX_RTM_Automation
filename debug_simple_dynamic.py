"""
Simple debugging test script with dynamic port selection.

This version automatically finds an available port if the default port is in use.
"""
import os
import sys
import time
import socket
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_available_port(start_port=5678, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port  # Port is available
            except OSError:
                continue  # Port is in use, try the next one
    return None  # No available ports found

def test_debugging(port=None):
    """Run a simple test function to debug."""
    logger.info("Starting simple debug test")

    # Find available port if none specified
    if port is None:
        port = find_available_port()
        if port is None:
            logger.error("No available ports found. Try running port_manager.py --release 5678")
            return

    # Import debugpy here to avoid issues if it's not installed
    try:
        import debugpy
        logger.info("debugpy successfully imported")

        # Configure debugpy to wait for the debugger
        logger.info(f"Enabling debugger on port {port}")
        debugpy.configure(python=sys.executable)  # Use the current Python interpreter

        try:
            debugpy.listen(("0.0.0.0", port))
            logger.info(f"Debugger is now listening on port {port}")
        except Exception as e:
            # If this port fails, try another one
            logger.error(f"Failed to listen on port {port}: {e}")
            new_port = find_available_port(port + 1)
            if new_port is None:
                logger.error("No available ports found after retry")
                return

            logger.info(f"Retrying with port {new_port}")
            debugpy.listen(("0.0.0.0", new_port))
            port = new_port

        logger.info(f"Waiting for debugger to attach on port {port}...")
        logger.info(f"In VS Code, update launch.json to use port {port}, then start debugging")
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
    print("\nSimple Debug Test (Dynamic Port)")
    print("===========================\n")

    # Parse command line arguments for custom port
    custom_port = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        custom_port = int(sys.argv[1])
        print(f"Using specified port: {custom_port}")

    # Run the test
    test_debugging(port=custom_port)

    print("\nTest completed. Press Enter to exit...")
    input()
