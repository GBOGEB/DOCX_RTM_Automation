"""
Comprehensive debugging test script.

This script provides multiple functions and features to test
various aspects of the debugging configuration.
"""
import os
import sys
import time
import json
import logging
import random
import threading
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import debugpy
try:
    import debugpy
    DEBUGPY_AVAILABLE = True
except ImportError:
    DEBUGPY_AVAILABLE = False
    logger.warning("debugpy not installed. Run 'pip install debugpy' to enable debugging.")

class DebugTester:
    """Class to test various debugging scenarios."""

    def __init__(self, debug_port=5678, enable_debug=None):
        """Initialize the debug tester."""
        self.debug_port = debug_port
        # Enable debugging based on environment variable or parameter
        self.enable_debug = enable_debug if enable_debug is not None else \
            os.environ.get('ENABLE_DEBUGGER', 'False').lower() == 'true'

        # Internal attributes for testing
        self._counter = 0
        self._data = {"values": [], "errors": []}

        # Initialize debugger if requested
        if self.enable_debug and DEBUGPY_AVAILABLE:
            self._setup_debugger()

    def _setup_debugger(self):
        """Setup the debugger on the specified port."""
        try:
            logger.info(f"Enabling debugger on port {self.debug_port}")
            debugpy.listen(("0.0.0.0", self.debug_port))
            logger.info(f"Debugger is now listening on port {self.debug_port}")

            # Uncomment to wait for debugger to attach before continuing
            # debugpy.wait_for_client()
            # logger.info("Debugger attached. Continuing execution.")

        except Exception as e:
            logger.error(f"Failed to set up debugger: {e}")
            logger.error(traceback.format_exc())

    def test_variables_and_scope(self):
        """Test debugging variables and scope."""
        logger.info("Testing variables and scope...")

        # Local variables to inspect
        local_var = "I'm a local variable"
        complex_var = {
            "name": "Complex Object",
            "nested": {"value": 42, "items": [1, 2, 3]},
            "active": True
        }

        # Loop with changing variables
        for i in range(5):
            # Good place for a breakpoint
            temp = i * 10
            self._counter += 1

            # Add some data to inspect
            self._data["values"].append(temp)

            # Random sleep to make debugging easier
            time.sleep(random.uniform(0.1, 0.3))

        logger.info(f"Counted to {self._counter}")

        # Return complex data to inspect in debugger
        return complex_var

    def test_exception_handling(self):
        """Test debugging with exceptions."""
        logger.info("Testing exception handling...")

        try:
            # This will cause a ZeroDivisionError
            value = 100 / 0
        except ZeroDivisionError as e:
            # Good place for a breakpoint
            self._data["errors"].append(str(e))
            logger.warning(f"Caught exception: {e}")

        try:
            # This will cause an IndexError
            items = [1, 2, 3]
            value = items[10]
        except IndexError as e:
            # Another good place for a breakpoint
            self._data["errors"].append(str(e))
            logger.warning(f"Caught exception: {e}")

        logger.info(f"Recorded {len(self._data['errors'])} errors")

    def test_conditional_breakpoints(self):
        """Test conditional breakpoints and calculations."""
        logger.info("Testing conditional breakpoints...")

        # Processing a range of numbers
        results = []
        for i in range(20):
            # Good for conditional breakpoint (e.g., when i > 15)
            value = i * i

            if i % 3 == 0:
                value += 1

            if i % 5 == 0:
                value *= 2

            results.append(value)

        # Complex list comprehension (good for step-through debugging)
        filtered = [x for x in results if x > 50 and x % 2 == 0]

        logger.info(f"Generated {len(results)} results, {len(filtered)} matched filter")
        return filtered

    def test_multithreading(self):
        """Test debugging with multiple threads."""
        logger.info("Testing multi-threading...")

        # Results container for threads
        results = {"thread_data": {}}

        def worker_function(worker_id):
            """Worker function that runs in a thread."""
            thread_name = f"Worker-{worker_id}"
            logger.info(f"Thread {thread_name} starting")

            # Good breakpoint location to examine thread
            local_data = []

            for i in range(5):
                # Another good breakpoint location
                value = (worker_id * 100) + i
                local_data.append(value)
                time.sleep(random.uniform(0.1, 0.2))

            # Update shared results (potential race condition to debug)
            results["thread_data"][worker_id] = local_data
            logger.info(f"Thread {thread_name} finished")

        # Create and start threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=worker_function, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        logger.info("All threads completed")
        return results

    def save_report(self, output_path=None):
        """Generate and save a debugging report."""
        if not output_path:
            output_dir = Path("debug_output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"debug_report_{int(time.time())}.json"

        report = {
            "timestamp": time.time(),
            "counter": self._counter,
            "data_points": len(self._data["values"]),
            "errors": self._data["errors"],
            "debugger_enabled": self.enable_debug,
            "debugpy_available": DEBUGPY_AVAILABLE,
            "debug_port": self.debug_port,
            "python_version": sys.version,
            "platform": sys.platform,
        }

        # Good breakpoint location
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Saved debug report to {output_path}")
        return output_path


def run_full_test_suite():
    """Run the full suite of debugging tests."""
    logger.info("Starting comprehensive debugging test")

    tester = DebugTester()

    # Run various tests
    result1 = tester.test_variables_and_scope()
    tester.test_exception_handling()
    result2 = tester.test_conditional_breakpoints()
    result3 = tester.test_multithreading()

    # Create a report
    report_path = tester.save_report()

    # Final summary
    logger.info("Comprehensive debugging test completed")
    logger.info(f"Report saved to {report_path}")

    return {
        "scopes_test_result": result1,
        "conditional_test_result": result2,
        "threading_test_result": result3,
        "report_path": report_path
    }


if __name__ == "__main__":
    # Parse command line arguments
    if '--wait-for-debugger' in sys.argv:
        os.environ['ENABLE_DEBUGGER'] = 'true'
        if DEBUGPY_AVAILABLE:
            logger.info("Waiting for debugger to attach...")
            debugpy.listen(("0.0.0.0", 5678))
            debugpy.wait_for_client()
            logger.info("Debugger attached! Continuing...")
        else:
            logger.error("Cannot wait for debugger - debugpy not installed.")

    # Run the tests
    run_full_test_suite()

    # Wait for user input before exiting
    input("Press Enter to exit...")
