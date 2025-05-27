import logging
import asciimatics

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    logging.debug("Successfully imported 'asciimatics'.")
except ImportError:
    asciimatics = None
    logging.warning("'asciimatics' is not installed. Some features may not work.")

def check_dependencies():
    """
    Check if optional dependencies are available.
    """
    if asciimatics is None:
        logging.error("Optional dependency 'asciimatics' is missing. Install it using 'pip install asciimatics'.")
        return False
    return True

def create_ascii_diagram(data):
    """
    Create an ASCII diagram based on the provided data.
    """
    if not check_dependencies():
        raise RuntimeError("Missing optional dependencies required for ASCII diagram generation.")

    logging.info("Starting ASCII diagram generation.")
    # Example placeholder logic for ASCII diagram generation
    try:
        diagram = f"ASCII Diagram for: {data}"
        logging.debug(f"Generated diagram: {diagram}")
        return diagram
    except Exception as e:
        logging.error(f"Error while generating ASCII diagram: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    sample_data = {"pipeline_step": "example_step", "status": "success"}
    try:
        ascii_diagram = create_ascii_diagram(sample_data)
        print(ascii_diagram)
    except RuntimeError as e:
        logging.critical(f"Pipeline failed: {e}")