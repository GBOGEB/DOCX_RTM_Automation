import yaml
import sys
import os
import logging
from pathlib import Path

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(Path("logs") / "process.log", mode="a")
        ]
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()
    logger.info("Starting document processing workflow")
    
    # Ensure configuration directory exists
    config_path = Path('config') / 'paths.yaml'
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    
    # Load configuration
    try:
        with open(config_path) as file:
            paths = yaml.safe_load(file)
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        sys.exit(1)
    
    # Import modules (using a relative import strategy)
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    try:
        from word_to_md import convert_word_to_md
        from extract_outline import extract_outline
        from extract_rtm import extract_rtm
        from sync_outline_files import sync_outline_files
        logger.info("All modules imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import required modules: {str(e)}")
        sys.exit(1)
    
    # Process workflow
    try:
        convert_word_to_md()
        extract_outline()
        extract_rtm()
        sync_outline_files()
        logger.info("Document processing workflow completed successfully")
    except Exception as e:
        logger.error(f"Error during workflow execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
