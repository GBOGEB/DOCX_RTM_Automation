"""
Comprehensive debugging test script.

This script provides multiple functions and features to test
various aspects of the debugging configuration.

Implements:
- FR-1.1: Login functionality test
- FR-1.2: Logout functionality test
- NFR-1: Performance measurement
- IR-1: User interface simulation
"""

import sys
import logging
import time
import re
from pathlib import Path
import importlib.util  # Added for checking debugpy

# --- Start of standard boilerplate for root scripts ---
_project_root_debug_comp = Path(__file__).resolve().parent
if str(_project_root_debug_comp) not in sys.path:
    sys.path.insert(0, str(_project_root_debug_comp))
# --- End of standard boilerplate ---

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Check for debugpy availability using importlib.util.find_spec
DEBUGPY_AVAILABLE = importlib.util.find_spec("debugpy") is not None
if not DEBUGPY_AVAILABLE:
    logger.warning(
        "debugpy not installed. Run 'pip install debugpy' to enable debugging."
    )


class DebugTester:
    """Debug testing class for various features."""

    def __init__(self):
        self.test_results = {}
        self.logged_in = False
        self.start_time = time.time()

    # Implementation of FR-1.1: Login functionality
    def test_login(self, username, password):
        """Test login functionality (FR-1.1)"""
        logger.info("Testing login functionality (FR-1.1)")

        # Simulate login validation
        if username == "admin" and password == "password":
            self.logged_in = True
            logger.info("Login successful")
            return True
        else:
            logger.error("Login failed: Invalid credentials")
            return False

    # Implementation of FR-1.2: Logout functionality
    def test_logout(self):
        """Test logout functionality (FR-1.2)"""
        logger.info("Testing logout functionality (FR-1.2)")

        if self.logged_in:
            self.logged_in = False
            logger.info("Logout successful")
            return True
        else:
            logger.warning("Logout failed: Not logged in")
            return False

    # Implementation of NFR-1: Performance measurement
    def measure_performance(self, operation_name, func, *args, **kwargs):
        """Measure performance of an operation (NFR-1)"""
        logger.info("Measuring performance for: %s (NFR-1)", operation_name)

        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        logger.info("Operation '%s' completed in %.4f seconds", operation_name, duration)

        # Check if performance meets the requirement (2 seconds)
        if duration <= 2.0:
            logger.info("✅ Performance requirement met (under 2 seconds)")
        else:
            logger.warning("⚠️ Performance requirement not met (over 2 seconds)")

        return result, duration

    # Implementation of IR-1: User interface simulation
    def simulate_ui_interaction(self, action, target):
        """Simulate user interface interaction (IR-1)"""
        logger.info("UI Action: %s on %s (IR-1)", action, target)

        # Simulate UI response time
        time.sleep(0.5)

        return f"Completed {action} on {target}"

    def check_requirements_references(self):
        """Check if this file correctly references requirements"""
        logger.info("Checking requirements references in code")

        with open(__file__, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for requirement references in comments or docstrings
        req_pattern = re.compile(r"([A-Z]+-\d+(?:\.\d+)*)")
        matches = req_pattern.findall(content)

        if matches:
            unique_reqs = set(matches)
            logger.info(
                "Found references to %s requirements: %s", len(unique_reqs), ', '.join(unique_reqs)
            )
            return True
        else:
            logger.warning("No requirement references found in this file")
            return False


def run_debug_tests():
    """Run a series of debug tests that implement requirements"""
    debug_tester_instance = DebugTester()

    # Check if file references requirements
    debug_tester_instance.check_requirements_references()

    # Test login (FR-1.1)
    debug_tester_instance.test_login("admin", "password")

    # Test some UI interactions (IR-1)
    debug_tester_instance.simulate_ui_interaction("click", "submit button")
    debug_tester_instance.simulate_ui_interaction("input", "search field")

    # Measure performance of a function (NFR-1)
    def complex_operation():
        # Simulate complex work
        time.sleep(1.5)
        return "Operation completed"

    debug_tester_instance.measure_performance("complex_operation", complex_operation)

    # Test logout (FR-1.2)
    debug_tester_instance.test_logout()

    return debug_tester_instance


if __name__ == "__main__":
    print("\nComprehensive Debug Test With Requirements Implementation")
    print("====================================================\n")

    tester = run_debug_tests()

    print("\nAll tests completed. Press Enter to exit...")
    input()
