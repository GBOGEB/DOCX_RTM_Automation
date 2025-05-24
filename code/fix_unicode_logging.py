import logging
import sys

def setup_logger():
    logger = logging.getLogger("document_processor")
    logger.setLevel(logging.INFO)

    # Create a StreamHandler with UTF-8 encoding
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Set UTF-8 encoding for the handler
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    handler.stream = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

    logger.addHandler(handler)
    return logger

# Example usage
if __name__ == "__main__":
    logger = setup_logger()
    logger.info("✅ Conversion successful")
    logger.info("🎉 Document processing workflow completed successfully!")