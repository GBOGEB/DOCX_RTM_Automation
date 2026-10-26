#!/usr/bin/env python3
"""
ASCII Diagram Module

Generates ASCII diagrams for pipeline and RTM processes.
Also includes helper functions to draw basic ASCII shapes.
"""

import logging

# Configure logging more robustly
# Set default logging level; can be overridden by application using this module
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)  # Use __name__ for module-specific logger


def generate_ascii_diagram(diagram_type: str = "rtm") -> str:  # Added type hints
    """
    Generate an ASCII diagram based on the specified type.

    Args:
        diagram_type: Type of diagram to generate ("rtm" or "pipeline").

    Returns:
        ASCII string representation of the diagram.
    """
    logger.debug(f"Generating ASCII diagram of type: {diagram_type}")

    if diagram_type == "pipeline":
        # Using a raw string literal for multi-line strings is cleaner
        return r"""
        +----------------+       +----------------+
        |   DOCX Files   |------>|    Pandoc      |
        +----------------+       +----------------+
                                        |
                                        v
        +----------------+       +----------------+
        | RTM Generator  |<------|  Markdown      |
        +----------------+       +----------------+
               |                        |
               |                        v
               |                  +----------------+
               |                  |     Lint       |
               v                  +----------------+
        +----------------+              |
        | Output Formats |<-------------+
        +----------------+
        """
    elif diagram_type == "rtm":  # Explicitly check for "rtm"
        return r"""
        +----------------------+
        |   Markdown Files     |
        |   (Requirements)     |
        +----------------------+
                  |
                  v
        +----------------------+
        |   RTM Generator      |
        |                      |
        | - Extract Reqs       |
        | - Process Sections   |
        | - Create Matrix      |
        +----------------------+
                  |
                  v
        +----------------------+
        |   Output Formats     |
        |                      |
        | - JSON               |
        | - YAML               |
        | - Markdown           |
        +----------------------+
        """
    else:
        logger.warning(
            f"Unknown diagram type: '{diagram_type}'. Returning empty diagram."
        )
        return "Unknown diagram type specified."


def draw_rectangle(width: int, height: int):  # Added type hints
    """
    Draws an ASCII rectangle with the given width and height.
    Prints directly to console.
    """
    if not isinstance(width, int) or not isinstance(height, int):
        logger.error("Width and height must be integers.")
        raise TypeError("Width and height must be integers.")
    if width < 2 or height < 2:
        logger.error(f"Width ({width}) and height ({height}) must be at least 2.")
        raise ValueError("Width and height must be at least 2.")

    top_bottom = f"+{'-' * (width - 2)}+"
    middle = f"|{' ' * (width - 2)}|"

    print(top_bottom)
    for _ in range(height - 2):
        print(middle)
    print(top_bottom)


def draw_triangle(height: int):  # Added type hints
    """
    Draws an ASCII right-angled triangle with the given height.
    Prints directly to console.
    """
    if not isinstance(height, int):
        logger.error("Height must be an integer.")
        raise TypeError("Height must be an integer.")
    if height < 1:  # Allow height of 1 for a single '*'
        logger.error(f"Height ({height}) must be at least 1.")
        raise ValueError("Height must be at least 1.")

    for i in range(1, height + 1):
        print("*" * i)


if __name__ == "__main__":
    logger.info("Running ASCII Diagram module directly for demonstration.")

    print("\nRectangle (width=10, height=5):")
    try:
        draw_rectangle(10, 5)
    except (ValueError, TypeError) as e:
        logger.error(f"Error drawing rectangle: {e}")

    print("\nTriangle (height=5):")
    try:
        draw_triangle(5)
    except (ValueError, TypeError) as e:
        logger.error(f"Error drawing triangle: {e}")

    print("\nDefault RTM diagram:")
    print(generate_ascii_diagram())  # Default is "rtm"

    print("\nPipeline diagram:")
    print(generate_ascii_diagram("pipeline"))

    print("\nUnknown diagram type example:")
    print(generate_ascii_diagram("unknown_type"))
