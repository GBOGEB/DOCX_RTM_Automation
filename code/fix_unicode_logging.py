import sys
import logging
from pathlib import Path

# Determine project root (assuming this script is in code/ subdirectory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def setup_unicode_logging(log_file_path_str: str = None, log_level=logging.INFO):
    """Set up logging that properly handles Unicode characters and emojis"""

    # Create formatters and handlers
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = []

    # Console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)

    # File handler if requested
    if log_file_path_str:
        log_file_path = Path(log_file_path_str)
        # If log_file_path is relative, make it relative to project root for consistency
        if not log_file_path.is_absolute():
            log_file_path = PROJECT_ROOT / "logs" / log_file_path

        log_dir = log_file_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        force=True,  # Override existing configuration
    )

    logger = logging.getLogger(__name__)
    logger.info("Unicode logging configured successfully")

    return logger


# Example usage
if __name__ == "__main__":
    # Example: log to a file in the project's logs directory
    log_file = "unicode_test_log.log"  # Will be placed in PROJECT_ROOT/logs/
    logger = setup_unicode_logging(log_file_path_str=log_file)
    logger.info("✅ Conversion successful")
    logger.info("🎉 Document processing workflow completed successfully!")
    logger.info(f"Log file should be at: {PROJECT_ROOT / 'logs' / log_file}")
