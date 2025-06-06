import unittest
import os
import sys

# Add project root to sys.path to allow imports from src, config etc.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class ExampleTests(unittest.TestCase):
    def test_truth(self):
        """This is a simple test that should always pass."""
