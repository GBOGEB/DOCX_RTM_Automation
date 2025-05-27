import unittest
import os
import sys

# This ensures that modules from the project's root (e.g., 'src') can be imported
# by adding the parent directory of 'tests' (which is the project root) to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class TestBasicSetup(unittest.TestCase):
    """Basic tests to ensure the testing framework is operational."""

    def test_truth(self):
        """A simple test that should always pass."""
        self.assertTrue(True, "Basic assertion failed, True should be True.")

    def test_project_directories_exist(self):
        """Check if essential project directories exist."""
        expected_dirs = ["src", "config", "input", "output", "scripts", "docs"]
        for dir_name in expected_dirs:
            dir_path = os.path.join(project_root, dir_name)
            self.assertTrue(os.path.isdir(dir_path), f"Directory '{dir_name}' should exist at '{dir_path}'.")

if __name__ == '__main__':
    unittest.main()
