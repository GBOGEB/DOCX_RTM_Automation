#!/usr/bin/env python3
"""
Word Document Round Trip Processing Script
-----------------------------------------
This script facilitates the round-trip processing of Word documents,
converting them to markdown, extracting information, and then
regenerating Word documents from the processed data.
"""

import os
import sys
import logging
from pathlib import Path
import argparse
from datetime import datetime

# Adjust path to find modules in the code directory
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(SCRIPT_DIR.parent / "code"))


def setup_logging(log_dir=None):
    """Set up logging for the script."""
    if log_dir is None:
        log_dir = SCRIPT_DIR.parent / "logs"

    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"round_trip_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
    )
    return logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process Word documents in a round-trip workflow."
    )
    parser.add_argument(
        "--input", "-i", help="Path to the input Word document", default=None
    )
    parser.add_argument(
        "--output", "-o", help="Path to the output directory", default=None
    )
    parser.add_argument(
        "--config", "-c", help="Path to custom config file", default=None
    )
    parser.add_argument(
        "--generate-structure",
        "-s",
        action="store_true",
        help="Generate document structure visualization",
    )
    parser.add_argument(
        "--structure-output",
        help="Path to output the structure visualization",
        default=None,
    )
    parser.add_argument(
        "--lua-filter",
        "-f",
        help="Path to Lua filter for structure extraction",
        default="config/structure_extraction.lua",
    )
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    logger = setup_logging()

    try:
        input_file = args.input
        if not input_file:
            logger.error("No input file specified")
            sys.exit(1)

        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            sys.exit(1)

        # Determine output path
        output_dir = args.output
        if not output_dir:
            output_dir = "output"

        os.makedirs(output_dir, exist_ok=True)

        # Generate output filename based on input filename
        input_path = Path(input_file)
        output_file = os.path.join(output_dir, f"{input_path.stem}.md")

        # Import modules for conversion and structure generation
        try:
            # First try to import from dedicated module
            from scripts.docx_to_md_with_structure import convert_docx_to_md
        except ImportError:
            # Fall back to pandoc_integration if the specific module isn't available
            logger.warning(
                "Specialized converter not found, falling back to standard converter"
            )
            from src.modules.pandoc_integration import (
                convert_document as convert_docx_to_md,
            )

        # Structure output path
        structure_output = args.structure_output
        if not structure_output and args.generate_structure:
            structure_output = os.path.join(
                output_dir, f"{input_path.stem}_structure.txt"
            )

        # Perform conversion
        logger.info("Starting Word document conversion")

        # If using specialized converter
        if "docx_to_md_with_structure" in sys.modules:
            success = convert_docx_to_md(
                input_file,
                output_file,
                structure_output=structure_output if args.generate_structure else None,
                lua_filter=args.lua_filter,
            )
        else:
            # If using fallback converter
            success = convert_docx_to_md(
                input_file,
                output_file,
                config_file=args.config,
                lua_filter=args.lua_filter,
            )

            # If structure extraction is requested and we're using the fallback,
            # we need to do it separately
            if args.generate_structure and success:
                try:
                    from src.modules.structure_generator import (
                        extract_structure_from_md,
                    )

                    logger.info(
                        f"Generating document structure to {structure_output}")
                    extract_structure_from_md(output_file, structure_output)
                except ImportError:
                    logger.warning(
                        "Structure generator module not available, skipping structure extraction"
                    )

        if success:
            logger.info(
                f"Conversion completed successfully. Output saved to {output_file}"
            )
            if args.generate_structure and structure_output:
                logger.info(f"Document structure saved to {structure_output}")
        else:
            logger.error("Conversion failed")
            sys.exit(1)

        # Future steps for RTM extraction or word regeneration would go here

        logger.info("Processing completed successfully")

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
