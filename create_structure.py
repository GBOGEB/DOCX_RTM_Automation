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

import os

def create_directory_structure():
    # Define directories to create
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
        "tests"
    ]
    
    # Create each directory
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

if __name__ == "__main__":
    create_directory_structure()
    print("Directory structure created successfully!")