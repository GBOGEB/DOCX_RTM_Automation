# filepath: tests/test_all.py

import unittest
from pathlib import Path


class TestAll(unittest.TestCase):
    def test_sample(self):
        """A sample test to verify the setup."""
        self.assertTrue(True, "This test always passes.")

    def test_file_existence(self):
        """Check if important files exist in the project."""
        important_files = [
            "config/openai_integration.py",
            "scripts/clean_outline.py",
            "README.md",
        ]
        for file in important_files:
            with self.subTest(file=file):
                self.assertTrue(Path(file).exists(), f"{file} does not exist.")


if __name__ == "__main__":
    unittest.main()
