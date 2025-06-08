#!/usr/bin/env python3
"""
DOCX to Markdown converter utilities.
Provides integration with different conversion methods.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

import subprocess
import re
from typing import Dict, Optional

# Add the project root to path if needed
project_root_path = Path(__file__).resolve().parent.parent
if str(project_root_path) not in sys.path:
    sys.path.append(str(project_root_path))

from utils.paths_manager import PathsManager
from utils.output_handler import OutputHandler
from utils.markdown_fixer import fix_markdown_headers  # Added import


class DocxConverter:
    """
    Utility class for converting DOCX files to other formats,
    primarily to Markdown using Pandoc.
    """

    def __init__(self, output_handler: Optional[OutputHandler] = None):
        """Initialize the DOCX converter"""
        self.paths = PathsManager()
        self.output_handler = output_handler or OutputHandler(
            self.paths.get_output_dir()
        )
        self.pandoc_available = self._check_pandoc()

    def _check_pandoc(self) -> bool:
        """Check if pandoc is available in the system"""
        try:
            result = subprocess.run(
                ["pandoc", "--version"], capture_output=True, check=True, text=True
            )
            version = re.search(r"pandoc ([\d\.]+)", result.stdout)
            if version:
                self.output_handler.log_info(f"Pandoc {version.group(1)} found")
                return True
            return False
        except (subprocess.SubprocessError, FileNotFoundError):
            self.output_handler.log_error(
                "Pandoc not found. DOCX to MD conversion will be limited."
            )
            return False

    def convert_to_markdown(
        self,
        input_file: str,
        output_file: Optional[str] = None,
        extract_images: bool = True,
    ) -> Optional[str]:
        """
        Convert a DOCX file to Markdown using pandoc

        Args:
            input_file: Path to the input DOCX file
            output_file: Path to the output Markdown file (optional)
            extract_images: Whether to extract images from the DOCX file

        Returns:
            Path to the output file if successful, None otherwise
        """
        if not os.path.isfile(input_file):
            self.output_handler.log_error(f"Input file not found: {input_file}")
            return None

        # If no output file specified, create one in the output directory
        if not output_file:
            output_file = os.path.join(
                self.paths.get_output_dir(),
                f"{os.path.splitext(os.path.basename(input_file))[0]}.md",
            )

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        self.output_handler.log_info(f"Converting {input_file} to Markdown")

        # If pandoc is available, use it
        if self.pandoc_available:
            try:
                # Determine output directory for images
                output_dir = os.path.dirname(output_file)
                media_dir = os.path.join(output_dir, "media")

                # Create media directory if extracting images
                if extract_images:
                    os.makedirs(media_dir, exist_ok=True)

                    # Use pandoc to extract images
                    extract_cmd = [
                        "pandoc",
                        input_file,
                        "--extract-media",
                        media_dir,
                        "-f",
                        "docx",
                        "-t",
                        "markdown",
                        "-o",
                        output_file,
                    ]

                    result = subprocess.run(
                        extract_cmd, check=True, capture_output=True, text=True
                    )
                    self.output_handler.log_info(
                        f"Converted {input_file} to {output_file} with images"
                    )
                else:
                    # Convert without extracting images
                    convert_cmd = [
                        "pandoc",
                        input_file,
                        "-f",
                        "docx",
                        "-t",
                        "markdown",
                        "-o",
                        output_file,
                    ]

                    result = subprocess.run(
                        convert_cmd, check=True, capture_output=True, text=True
                    )
                    self.output_handler.log_info(
                        f"Converted {input_file} to {output_file}"
                    )

                # Fix markdown headers after conversion
                if os.path.exists(output_file):
                    fix_markdown_headers(output_file)
                    self.output_handler.log_info(
                        f"Applied markdown header fixes to {output_file}"
                    )

                return output_file
            except subprocess.SubprocessError as e:
                self.output_handler.log_error(
                    f"Error converting {input_file} to Markdown: {e}"
                )
                return None
        else:
            # Fallback for when pandoc is not available
            self._fallback_conversion(input_file, output_file)
            return output_file

    def _fallback_conversion(self, input_file: str, output_file: str) -> bool:
        """
        Fallback conversion method when pandoc is not available
        This produces a very basic conversion with limited features
        """
        try:
            # Print warning about limitations
            self.output_handler.log_info(
                "Using fallback conversion (limited functionality)"
            )

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Extracted from {os.path.basename(input_file)}\n\n")
                f.write(
                    "*Note: This is a basic extraction without pandoc. Install pandoc for better results.*\n\n"
                )
                f.write("## Content\n\n")

                # Try to extract text using alternative methods if available
                try:
                    import docx

                    doc = docx.Document(input_file)
                    for para in doc.paragraphs:
                        f.write(f"{para.text}\n\n")
                except ImportError:
                    f.write(
                        "*Could not extract content. Please install python-docx or pandoc.*\n"
                    )

            self.output_handler.log_info(
                f"Created basic markdown conversion at {output_file}"
            )
            return True
        except Exception as e:
            self.output_handler.log_error(f"Error in fallback conversion: {e}")
            return False

    def batch_convert_directory(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        file_pattern: str = "*.docx",
    ) -> Dict[str, str]:
        """
        Convert all DOCX files in a directory to Markdown

        Args:
            input_dir: Directory containing DOCX files
            output_dir: Directory to save Markdown files (defaults to output_dir/converted)
            file_pattern: File pattern to match DOCX files

        Returns:
            Dictionary mapping input files to output files
        """
        if not os.path.isdir(input_dir):
            self.output_handler.log_error(f"Input directory not found: {input_dir}")
            return {}

        # If no output directory specified, create one in the output directory
        if not output_dir:
            output_dir = os.path.join(self.paths.get_output_dir(), "converted")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Find all DOCX files in the input directory
        input_files = list(Path(input_dir).glob(file_pattern))

        if not input_files:
            self.output_handler.log_info(
                f"No {file_pattern} files found in {input_dir}"
            )
            return {}

        self.output_handler.log_info(
            f"Converting {len(input_files)} files from {input_dir} to {output_dir}"
        )

        # Convert each file
        results = {}
        for input_file in input_files:
            output_file = os.path.join(output_dir, f"{input_file.stem}.md")

            result = self.convert_to_markdown(str(input_file), output_file)
            if result:
                results[str(input_file)] = result

        self.output_handler.log_info(
            f"Converted {len(results)} of {len(input_files)} files successfully"
        )
        return results


# Utility integration modules
def convert_basic(docx_file, output_file=None):
    """Simple conversion using python-docx."""
    try:
        # Import from local module
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from try_word_to_md import convert_docx_to_markdown

        result = convert_docx_to_markdown(docx_file, output_file)
        logging.info(f"Basic conversion completed: {result}")
        return result
    except Exception as e:
        logging.error(f"Basic conversion failed: {e}")
        raise

def convert_with_pandoc(docx_file, output_file=None):
    """Convert using pandoc for better formatting."""
    try:
        # Import from local module
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from pandoc_converter import convert_with_pandoc

        result = convert_with_pandoc(docx_file, output_file)
        logging.info(f"Pandoc conversion completed: {result}")
        return result
    except Exception as e:
        logging.error(f"Pandoc conversion failed: {e}")
        raise

def convert_with_metadata(docx_file, output_file=None, extract_outline=True):
    """Convert with metadata extraction."""
    try:
        # Import from local module
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from enhanced_word_to_md import convert_docx_to_markdown_with_metadata

        result = convert_docx_to_markdown_with_metadata(docx_file, output_file, extract_outline)
        logging.info(f"Enhanced conversion completed: {result[0]}")
        return result
    except Exception as e:
        logging.error(f"Enhanced conversion failed: {e}")
        raise

def convert_exact(docx_file, output_file=None):
    """Convert with exact detail preservation."""
    try:
        # Import from local module
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from exact_docx_to_md import convert_docx_to_markdown_exact

        result = convert_docx_to_markdown_exact(docx_file, output_file)
        logging.info(f"Exact conversion completed: {result}")
        return result
    except Exception as e:
        logging.error(f"Exact conversion failed: {e}")
        raise

def main():
    """Command-line interface for the converter."""
    parser = argparse.ArgumentParser(description="Convert DOCX to Markdown")
    parser.add_argument("input", nargs='?', help="Input DOCX file")
    parser.add_argument("-o", "--output", help="Output markdown file")
    parser.add_argument(
        "--method",
        choices=["basic", "pandoc", "enhanced", "exact"],
        default="enhanced",
        help="Conversion method to use"
    )
    parser.add_argument("--list", action="store_true", help="List available documents")

    # Only parse args if running as main script, not when imported
    if __name__ == "__main__":
        args = parser.parse_args()
    else:
        # When imported, don't parse args (avoid SystemExit on missing args)
        args = parser.parse_args([]) if len(sys.argv) <= 1 else None
        return 0  # Return early when imported

    if args.list or not args.input:
        # List available files
        input_dir = Path("input")
        print("Available DOCX files:")
        if input_dir.exists():
            for idx, file in enumerate(input_dir.glob("*.docx"), 1):
                print(f"  {idx}. {file}")
        else:
            print("  No input directory found")
        return 0

    # Convert using selected method
    try:
        if args.method == "basic":
            result = convert_basic(args.input, args.output)
        elif args.method == "pandoc":
            result = convert_with_pandoc(args.input, args.output)
        elif args.method == "enhanced":
            result, _, _ = convert_with_metadata(args.input, args.output)
        elif args.method == "exact":
            result = convert_exact(args.input, args.output)
        else:
            print(f"Unknown method: {args.method}")
            return 1

        print(f"Conversion successful: {result}")
        return 0
    except Exception as e:
        print(f"Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
