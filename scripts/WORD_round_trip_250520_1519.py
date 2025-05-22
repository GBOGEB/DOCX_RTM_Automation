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
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )
    return logging.getLogger(__name__)

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Process Word documents in a round-trip workflow."
    )
    parser.add_argument(
        "--input", "-i", 
        help="Path to the input Word document",
        default=None
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to custom config file",
        default=None
    )
    return parser.parse_args()

def main():
    """Main execution function."""
    args = parse_arguments()
    logger = setup_logging()
    
    try:
        # Import main processing module
        from main import main as process_main
        
        # Run the main processing function
        logger.info("Starting Word document round-trip processing")
        process_main()
        logger.info("Processing completed successfully")
        
    except Exception as e:
        logger.error(f"Processing failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
