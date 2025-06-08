#!/usr/bin/env python3
"""
RTM Pipeline - Main execution script (FIXED VERSION)
"""

import logging
from pathlib import Path
from datetime import datetime
import sys

# Import the document conversion function
from document_converter import run_document_conversion

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger('rtm_pipeline')

def find_input_document(input_dir="input"):
    """Find the first DOCX document in the input directory"""
    input_path = Path(input_dir)

    if not input_path.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return None

    # Look for DOCX files
    docx_files = list(input_path.glob("*.docx"))

    if not docx_files:
        logger.error(f"No DOCX files found in {input_dir}")
        return None

    # Return the first DOCX file found
    selected_doc = docx_files[0]
    logger.info(f"Using found document: {selected_doc}")
    return str(selected_doc)

def run_rtm_pipeline():
    """Run the complete RTM processing pipeline"""
    logger.info("Starting RTM Pipeline")
    logger.info("=" * 50)

    try:
        # Step 1: Find input document
        logger.info("Step 1: Finding input document...")
        input_document = find_input_document()

        if not input_document:
            logger.error("No input document found - pipeline cannot continue")
            return False

        # Step 2: Run document conversion (FIXED - single parameter only)
        logger.info("Step 2: Converting document...")
        conversion_result = run_document_conversion(input_document)

        if conversion_result["status"] != "success":
            logger.error(f"Document conversion failed: {conversion_result.get('error', 'Unknown error')}")
            return False

        logger.info(f"Document conversion successful!")
        logger.info(f"Generated {len(conversion_result['converted_files'])} output files")

        # Step 3: Additional processing could go here
        logger.info("Step 3: Pipeline processing complete")

        # Summary
        logger.info("=" * 50)
        logger.info("RTM Pipeline completed successfully!")
        logger.info(f"Input: {input_document}")
        logger.info(f"Output directory: {conversion_result['output_directory']}")
        logger.info(f"Files generated: {len(conversion_result['converted_files'])}")

        return True

    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return False

def main():
    """Main function"""
    print("🚀 RTM Automation Pipeline")
    print("=" * 30)
    print("Starting automated RTM processing...\n")

    # Initialize OpenAI integration if available
    try:
        print("Initializing OpenAI integration...")
        # Add your OpenAI initialization here if needed
        print("OpenAI integration ready")
    except Exception as e:
        print(f"OpenAI integration not available: {e}")

    # Run the pipeline
    success = run_rtm_pipeline()

    if success:
        print("\n✅ Pipeline completed successfully!")
        print("\nNext steps:")
        print("1. Check the output directory for generated files")
        print("2. Run: python find_output_files.py")
        print("3. Review the conversion results")
    else:
        print("\n❌ Pipeline failed!")
        print("\nTroubleshooting:")
        print("1. Check that input DOCX files exist in the 'input' directory")
        print("2. Ensure you have the required dependencies installed")
        print("3. Check the error messages above")

if __name__ == "__main__":
    main()
