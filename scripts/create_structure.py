"""
Directory Structure Creation Script

Creates the following directory structure:
- src/: Source code
  - core/: Core functionality
  - modules/: Support modules
  - extractors/: Data extraction modules
  - utils/: Utility functions
- config/: Configuration files
- scripts/: Helper scripts
- input/: Input documents
- output/: Generated output files
- docs/: Documentation
- tests/: Test files

Requirements:
- Python 3.8+
- Pandoc (for DOCX to Markdown conversion)
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def create_directory_structure():
    # Define directories to create (relative to BASE_DIR)
    directories = [
        "src",
        "src/core",
        "src/modules",
        "src/extractors",
        "src/utils",
        "config",
        "scripts",
        "input",
        "output",
        "docs",
        "tests",
    ]

    # Create each directory
    for dir_name in directories:
        directory_path = BASE_DIR / dir_name
        directory_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory_path}")


if __name__ == "__main__":
    create_directory_structure()
    print("Directory structure created successfully!")
