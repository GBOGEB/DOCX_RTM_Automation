#!/usr/bin/env python3
"""
Use pandoc to convert DOCX to Markdown, then process the Markdown to extract requirements.
This provides a more robust and standard-compliant Markdown conversion.
"""
import os
import sys
import subprocess
import tempfile
from pathlib import Path
import argparse
import re
import traceback  # Moved import to top level


def check_pandoc_installed():
    """Check if pandoc is installed."""
    try:
        subprocess.run(
            ["pandoc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
        )
        return True
    except FileNotFoundError:
        return False


def install_pandoc():
    """Provide instructions for installing pandoc."""
    print("Pandoc is not installed on your system.")
    print("\nInstallation instructions:")
    print("  - Windows: Download installer from https://pandoc.org/installing.html")
    print("  - macOS: Run 'brew install pandoc'")
    print("  - Linux (Ubuntu/Debian): Run 'sudo apt-get install pandoc'")
    print("  - Linux (Fedora): Run 'sudo dnf install pandoc'")
    print("\nAfter installing, run this script again.")
    return False


def convert_with_pandoc(input_file, output_file=None):
    """
    Convert a document to Markdown using pandoc.

    Args:
        input_file: Path to the input file
        output_file: Path where the output Markdown will be saved

    Returns:
        Path to the output file
    """
    if not check_pandoc_installed():
        if not install_pandoc():
            return None

    # If no output file is specified, create one in the output directory
    if output_file is None:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / Path(input_file).with_suffix(".md").name

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"Converting {input_file} to Markdown using pandoc...")

    # Run pandoc with appropriate options
    try:
        # Use a temporary file to avoid permission issues
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as temp_file:
            temp_path = temp_file.name

        # Command for pandoc conversion with enhanced options for better list handling
        cmd = [
            "pandoc",
            str(input_file),
            "-o",
            temp_path,
            "--wrap=none",  # Don't wrap lines
            "--standalone",  # Produce a standalone document
            "--extract-media=media",  # Extract images to 'media' folder
            "--markdown-headings=atx",  # Use # style headings
            "--columns=120",  # Width for wrapping
            "--from=docx",  # Specify input format
            "--to=markdown_github+lists_without_preceding_blankline",  # GitHub flavored markdown with better list handling
            "--shift-heading-level-by=0",  # Preserve heading levels
            "--atx-headers",  # Use ATX-style headers
            "--markdown-extensions=+task_lists+definition_lists+footnotes+lists_without_preceding_blankline",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # Keep check=False for initial attempt, will check returncode

        if result.returncode != 0:
            print(f"Error during conversion: {result.stderr}")
            # Try a simplified command if the first one fails
            cmd = [
                "pandoc",
                str(input_file),
                "-o",
                temp_path,
                "--from=docx",
                "--to=markdown",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # Keep check=False, will check returncode
            if result.returncode != 0:
                print(f"Simplified conversion also failed: {result.stderr}")
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return None
            else:
                print("Used simplified pandoc conversion.")

        # Read the temporary file and do any post-processing
        with open(temp_path, "r", encoding="utf-8") as f:
            markdown_content = f.read()

        # Post-processing for better requirement recognition and formatting
        # 1. Fix heading formatting to ensure proper structure
        markdown_content = re.sub(
            r"^(\s*#+)([A-Za-z0-9])", r"\1 \2", markdown_content, flags=re.MULTILINE
        )

        # 2. Ensure proper spacing after heading markers
        markdown_content = re.sub(
            r"^(\s*#+\s*)([A-Za-z0-9])", r"\1\2", markdown_content, flags=re.MULTILINE
        )

        # 3. Fix multi-level list indentation (useful for requirement nesting)
        markdown_content = re.sub(
            r"^(\s+)[-*]", r"\1- ", markdown_content, flags=re.MULTILINE
        )

        # 4. Fix numbered lists - ensure proper spacing
        markdown_content = re.sub(
            r"^(\s*)(\d+)\.(?!\s)", r"\1\2. ", markdown_content, flags=re.MULTILINE
        )

        # 5. Ensure blank lines around lists for proper rendering
        markdown_content = re.sub(
            r"([^\n])\n([-*]|\d+\.)", r"\1\n\n\2", markdown_content, flags=re.MULTILINE
        )

        # 6. Add document title based on filename
        title = Path(input_file).stem
        markdown_content = (
            f"# {title}\n\n*Converted from {Path(input_file).name}*\n\n"
            + markdown_content
        )

        # Write the final output
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

        print(f"Conversion complete! Output saved to {output_file}")
        return output_file

    except Exception as e:  # Specify Exception as e
        print(f"Error during conversion: {e}")
        traceback.print_exc()
        return None


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert DOCX to Markdown using pandoc and extract requirements."
    )
    parser.add_argument("input_file", nargs="?", help="Path to the input DOCX file")
    parser.add_argument("-o", "--output", help="Path to save the output Markdown file")
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze requirements after conversion"
    )

    args = parser.parse_args()

    # If no input file specified, look for docx files in input directory
    if args.input_file is None:
        input_dir = Path("input")
        if input_dir.exists():
            docx_files = list(input_dir.glob("*.docx"))
            if docx_files:
                args.input_file = str(docx_files[0])
                print(f"Using found document: {args.input_file}")
            else:
                print("No DOCX files found in input directory.")
                return 1
        else:
            print("No input file specified and no 'input' directory found.")
            return 1

    # Convert the document
    output_file = convert_with_pandoc(args.input_file, args.output)

    if output_file is None:
        print("Conversion failed.")
        return 1

    # If --analyze flag is set, run requirement analysis
    if args.analyze:
        print("\nAnalyzing requirements in the converted document...")
        try:
            # Import the enhanced requirement parser
            from enhanced_requirement_parser import main as analyze_requirements

            # Temporarily replace sys.argv to pass the output file to the analyzer
            original_argv = sys.argv
            sys.argv = [sys.argv[0], str(output_file)]

            # Run the analysis
            analyze_requirements()

            # Restore original argv
            sys.argv = original_argv

        except ImportError:
            print("Enhanced requirement parser not found. Please run:")
            print("  python enhanced_requirement_parser.py", str(output_file))

    return 0


if __name__ == "__main__":
    sys.exit(main())
