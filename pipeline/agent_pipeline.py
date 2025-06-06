import logging

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s"
)

try:
    # Code that might raise a ConnectionAbortedError
    pass
except ConnectionAbortedError as e:
    logging.error(f"Connection was aborted: {e}")
