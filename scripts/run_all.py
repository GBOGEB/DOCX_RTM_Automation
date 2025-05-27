import os
import sys
import argparse
import logging
from datetime import datetime

# Attempt to import parse_docx_files
try:
    from docx_parser import parse_docx_files
except ImportError as e:
    print(f"ImportError: {e}")
    print("Failed to import 'parse_docx_files' from 'docx_parser'.")
    print("Please ensure that:")
    print("1. If you are using a library (e.g., 'docx-parser' from PyPI), it is correctly installed in your virtual environment.")
    print("2. The installed 'docx_parser' library actually provides a function named 'parse_docx_files' at its top level.")
    print("   (Check the library's documentation for the correct import statement and function name. For 'docx-parser' on PyPI, the function might be just 'parse' or located in a submodule).")
    print("3. If 'docx_parser' is a local module/package in your project, ensure it is in the Python path and correctly defines 'parse_docx_files'.")
    print(f"Python is attempting to load 'docx_parser' from: {e.path if hasattr(e, 'path') else 'unknown location'}")
    sys.exit(1)

try:
    try:
        try:
            try:
                from requirements_extractor import extract_requirements
            except ImportError:
                print("Error: 'requirements_extractor' module not found. Please ensure it is installed or provide a fallback implementation.")
                sys.exit(1)
        except ImportError:
            print("Error: 'requirements_extractor' module not found. Ensure it's installed or available in the Python path.")
            sys.exit(1)
    except ImportError as e:
        print(f"ImportError: {e}")
        print("Failed to import 'extract_requirements' from 'requirements_extractor'.")
        print("Please ensure that:")
        print("1. The 'requirements_extractor' module is installed or available in the Python path.")
        print("2. If it's a local module, ensure it is in the same directory or a discoverable package.")
        sys.exit(1)
except ImportError:
    print("Error: 'requirements_extractor' module not found. Ensure it's in the Python path (e.g., same directory as run_all.py or in a discoverable package).")
    sys.exit(1)

try:
    try:
        try:
            from rtm_generator import generate_rtm
        except ImportError:
            print("Error: 'rtm_generator' module not found. Please ensure it is installed or provide a fallback implementation.")
            sys.exit(1)
    except ImportError as e:
        print(f"ImportError: {e}")
        print("Failed to import 'generate_rtm' from 'rtm_generator'.")
        print("Please ensure that:")
        print("1. The 'rtm_generator' module is installed or available in the Python path.")
        print("2. If it's a local module, ensure it is in the same directory or a discoverable package.")
        sys.exit(1)
except ImportError:
    print("Error: 'rtm_generator' module not found. Ensure it's in the Python path.")
    sys.exit(1)

try:
    try:
        try:
            try:
                try:
                    from report_generator import generate_report
                except ImportError:
                    print("Error: 'report_generator' module not found. Please ensure it is installed or provide a fallback implementation.")
                    sys.exit(1)
            except ImportError:
                print("Error: 'report_generator' module not found. Please ensure it is installed or provide a fallback implementation.")
                sys.exit(1)
        except ImportError:
            print("Error: 'report_generator' module not found. Please ensure it is installed or provide a fallback implementation.")
            sys.exit(1)
    except ImportError as e:
        print(f"ImportError: {e}")
        print("Failed to import 'generate_report' from 'report_generator'.")
        print("Please ensure that:")
        print("1. The 'report_generator' module is installed or available in the Python path.")
        print("2. If it's a local module, ensure it is in the same directory or a discoverable package.")
        sys.exit(1)
except ImportError:
    print("Error: 'report_generator' module not found. Ensure it's in the Python path.")
    sys.exit(1)

#!/usr/bin/env python3
"""
DOCX RTM Automation Tool - Main Runner
This script executes all components of the RTM automation process.
"""

def setup_logger():
    """Configure logging for the application."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"rtm_automation_{timestamp}.log")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DOCX RTM Automation Tool")
    parser.add_argument(
        "--input-dir", "-i",
        default="input",
        help="Directory containing input DOCX files"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="output",
        help="Directory for output files"
    )
    parser.add_argument(
        "--config", "-c",
        default="config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    return parser.parse_args()


def main():
    """Main entry point for the RTM automation tool."""
    args = parse_arguments()
    logger = setup_logger()

    try:
        logger.info("Starting DOCX RTM Automation")

        # Ensure directories exist
        if not os.path.exists(args.input_dir):
            logger.error(f"Input directory not found: {args.input_dir}")
            return 1

        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)

        # Process steps
        logger.info("Parsing DOCX files...")
        parsed_docs = parse_docx_files(args.input_dir, args.config)

        logger.info("Extracting requirements...")
        requirements = extract_requirements(parsed_docs, args.config)

        logger.info("Generating RTM...")
        rtm = generate_rtm(requirements, args.config)

        logger.info("Generating report...")
        report_path = generate_report(rtm, args.output_dir, args.config)

        logger.info(
            f"RTM automation completed successfully. Report saved to: {report_path}")
        return 0

    except Exception as e:
        logger.exception(f"Error during RTM automation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
