import os
import sys
import argparse
import logging
from datetime import datetime
from docx_parser import parse_docx_files
from requirements_extractor import extract_requirements
from rtm_generator import generate_rtm
from report_generator import generate_report

#!/usr/bin/env python3
"""
DOCX RTM Automation Tool - Main Runner
This script executes all components of the RTM automation process.
"""


# Import local modules (assuming these exist in the project)
try:
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running from the correct directory.")
    sys.exit(1)

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
        
        logger.info(f"RTM automation completed successfully. Report saved to: {report_path}")
        return 0
        
    except Exception as e:
        logger.exception(f"Error during RTM automation: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())