#!/usr/bin/env python3
"""
Sample script for testing debugging configuration.

Implements:
- FR-2: Data Management - Demonstrates data processing
- IR-3: External System Interfaces - Shows debugpy as external interface
"""

import os
import debugpy


def setup_debugger(port=5678):
    """
    Set up the debugger to listen on a specific port.
    Implements IR-3: External System Interface requirement

    Args:
        port: Port to listen on (default: 5678)
    """
    # Enable debugging based on environment variable or direct call
    should_debug = os.environ.get("ENABLE_DEBUGGER", "False").lower() == "true"

    if should_debug:
        print(f"Enabling debugger on port {port}")
        # IR-3: External System Interface - Connects to VS Code
        debugpy.listen(("0.0.0.0", port))
        print(f"Debugger is now listening on port {port}")

        # Uncomment to pause execution until a debugger attaches
