#!/usr/bin/env python
# Test runner for DOCX RTM Automation

import os
import sys
import unittest

if __name__ == "__main__":
    # Change working directory to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Discover and run tests
    test_suite = unittest.defaultTestLoader.discover("tests", pattern="test_*.py")
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
