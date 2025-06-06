#!/usr/bin/env python3
"""
Markdown enhancement utilities.
Provides functions to improve markdown formatting and structure.
"""

import os
import re
import sys
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)


def fix_markdown_headers(file_path):
    """
    Fix markdown headers to ensure proper spacing and formatting.

    Args:
        file_path: Path to the markdown file to fix

    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find headers with incorrect spacing after hash marks
        pattern = re.compile(r'^(#+)([^ \n])', re.MULTILINE)
        fixed_content = pattern.sub(r'\1 \2', content)

        # Check if changes were made
        if fixed_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            logger.info(f"Fixed header spacing in {file_path}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error fixing markdown headers in {file_path}: {e}")
        return False


def enhance_markdown_file(markdown_file, output_file=None):
    """
    Enhance a markdown file with various formatting improvements.

    Args:
        markdown_file: Path to the markdown file
        output_file: Path to save enhanced markdown (default: overwrite input)

    Returns:
        Path to the enhanced file
    """
    if not os.path.exists(markdown_file):
        logger.error(f"File not found: {markdown_file}")
        return None

    if output_file is None:
        output_file = markdown_file

    # Add parent directories to path to find enhance_document_parsing
    sys.path.append(str(Path(__file__).resolve().parent.parent))

    try:
        from enhance_document_parsing import post_process_markdown
        enhanced_file = post_process_markdown(markdown_file, output_file)
        logger.info(f"Enhanced markdown file: {enhanced_file}")
        return enhanced_file
    except ImportError:
        logger.warning("Could not import enhance_document_parsing module. Using basic enhancements only.")
        # Perform basic fixes
        fix_markdown_headers(markdown_file)

        # If output file is different from input, make a copy
        if output_file != markdown_file:
            import shutil
            shutil.copy2(markdown_file, output_file)

        return output_file


def process_all_markdown_files(directory, recursive=True):
    """
    Process all markdown files in a directory.

    Args:
        directory: Directory containing markdown files
        recursive: Whether to process subdirectories

    Returns:
        Number of files processed
    """
    directory = Path(directory)
    if not directory.is_dir():
        logger.error(f"Not a directory: {directory}")
        return 0

    processed = 0
    pattern = '**/*.md' if recursive else '*.md'

    for md_file in directory.glob(pattern):
        if fix_markdown_headers(md_file):
            processed += 1

    logger.info(f"Processed {processed} markdown files in {directory}")
    return processed


def run_test():
    """Run a quick test for the markdown fixer."""
    print("Running test for fix_markdown_headers...")

    # Create a test file with incorrect headers
    test_content = """#Title without space
## Subtitle with space
###Another header without space
#### This one has space
"""

    test_file = "test_markdown_fixer_temp_file.md"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)

    # Fix the headers
    fix_markdown_headers(test_file)

    # Verify the fix
    with open(test_file, "r", encoding="utf-8") as f:
        fixed_content = f.read()

    expected = """# Title without space
## Subtitle with space
### Another header without space
#### This one has space
"""

    if fixed_content == expected:
        print(f"✓ Test passed: Markdown headers in '{test_file}' fixed correctly.")
    else:
        print(f"✗ Test failed: Headers not fixed correctly.")
        print("Expected:")
        print(expected)
        print("Got:")
        print(fixed_content)

    # Clean up
    os.unlink(test_file)
    print("Test finished.")


def main():
    """Main entry point for command line usage."""
    parser = argparse.ArgumentParser(description="Fix and enhance markdown files")
    parser.add_argument("input", nargs='?', help="Markdown file or directory to process")
    parser.add_argument("-o", "--output", help="Output file (for single file processing)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Process directories recursively")
    parser.add_argument("--test", action="store_true", help="Run a test")

    # Only parse args when run directly
    if __name__ == "__main__":
        args = parser.parse_args()
    else:
        return 0

    # Run test if requested
    if args.test:
        run_test()
        return 0

    # Process input
    if not args.input:
        parser.print_help()
        return 1

    input_path = Path(args.input)
    if input_path.is_dir():
        processed = process_all_markdown_files(input_path, args.recursive)
        print(f"Processed {processed} markdown files")
    else:
        result = enhance_markdown_file(input_path, args.output)
        if result:
            print(f"Enhanced markdown saved to: {result}")
        else:
            print(f"Failed to process {input_path}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

