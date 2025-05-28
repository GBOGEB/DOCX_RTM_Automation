#!/usr/bin/env python3
"""
Sample script for testing debugging configuration.
"""
import os
import sys
import debugpy


def setup_debugger(port=5678):
    """
    Set up the debugger to listen on a specific port.

    Args:
        port: Port to listen on (default: 5678)
    """
    # Enable debugging based on environment variable or direct call
    should_debug = os.environ.get('ENABLE_DEBUGGER', 'False').lower() == 'true'

    if should_debug:
        print(f"Enabling debugger on port {port}")
        debugpy.listen(("0.0.0.0", port))
        print(f"Debugger is now listening on port {port}")

        # Uncomment to pause execution until a debugger attaches
        # debugpy.wait_for_client()
        # print("Debugger attached. Continuing execution.")


def main():
    """Main function with debugging example."""
    # Set up debugger
    setup_debugger()

    # Simple debugging demonstration
    a = 10
    b = 5

    # Good place to set a breakpoint
    result = a + b
    print(f"Result: {result}")

    # More complex calculation (step through this in debugger)
    values = [1, 2, 3, 4, 5]
    sum_result = 0

    for i, val in enumerate(values):
        # Another good place for a breakpoint
        sum_result += val * i

    print(f"Sum result: {sum_result}")

    # Wait for user input before exiting
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
