#!/usr/bin/env python3
"""
ASCII Diagram Generator for RTM documentation and visualization.
Helps visualize requirement relationships and project structure.
"""

import sys
import json
import logging
import traceback
from pathlib import Path
import yaml  # Moved from inside function to top level

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Determine project root (assuming this script is in code/ subdirectory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config(config_path=None):
    """Load configuration from YAML file."""
    default_config = {
        "width": 80,
        "height": 25,
        "theme": "default",
        "use_color": True,
        "output_format": ["ascii", "svg"],
        "include_header": True,
        "symbols": {
            "horizontal_line": "-",
            "vertical_line": "|",
            "corner_tl": "+",
            "corner_tr": "+",
            "corner_bl": "+",
            "corner_br": "+",
        },
    }

    if not config_path or not Path(config_path).exists():
        logger.info("No config file found, using default settings")
        return default_config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f)

        # Merge configs, with user settings taking precedence
        for key, value in user_config.items():
            if (
                isinstance(value, dict)
                and key in default_config
                and isinstance(default_config[key], dict)
            ):
                default_config[key].update(value)
            else:
                default_config[key] = value

        logger.info("Loaded configuration from %s", config_path)
        return default_config
    except (yaml.YAMLError, IOError) as e:
        logger.error("Failed to load config from %s: %s", config_path, e)
        traceback.print_exc()
        return default_config
    except Exception as e_config:
        logger.error("Unexpected error loading config: %s", e_config)
        traceback.print_exc()
        return default_config


def parse_diagram_data(data_source):
    """Parse diagram data from JSON file or dictionary."""
    if isinstance(data_source, str):
        try:
            with open(data_source, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info("Loaded diagram data from %s", data_source)
            return data
        except json.JSONDecodeError as e_json:
            logger.error("Invalid JSON in %s: %s", data_source, e_json)
            return None
        except IOError as e_io:
            logger.error("Could not read file %s: %s", data_source, e_io)
            return None
        except Exception as e_parse:
            logger.error("Error parsing diagram data: %s", e_parse)
            traceback.print_exc()
            return None
    elif isinstance(data_source, dict):
        return data_source
    else:
        logger.error("Invalid data source type: %s", type(data_source).__name__)
        return None


def generate_diagram(data, config=None):
    """Generate ASCII diagram from data."""
    if config is None:
        config = load_config()

    width = config.get("width", 80)
    height = config.get("height", 25)

    canvas = [[" " for _ in range(width)] for _ in range(height)]

    try:
        for node_id, node_data in data.get("nodes", {}).items():
            x = node_data.get("x", 0)
            y = node_data.get("y", 0)
            label = node_data.get("label", node_id)
            shape = node_data.get("shape", "box")

            if shape == "box":
                draw_box(canvas, x, y, label)
            elif shape == "circle":
                draw_circle(canvas, x, y, label)
            else:
                logger.warning("Unknown shape: %s", shape)

        return render_canvas(canvas)
    except Exception as e_generate:
        logger.error("Error generating diagram: %s", e_generate)
        traceback.print_exc()
        return None


def draw_box(canvas, x, y, label, width=20, height=5):
    """Draw a box with a label."""
    y + height // 2
    # Draw label in the middle of the box
    # Existing code for drawing box


def add_color_codes(diagram_text):
    """Add ANSI color codes to the diagram."""
    color_map = {
        "-": "\033[34m",  # Blue
        "|": "\033[34m",  # Blue
        "+": "\033[32m",  # Green
    }

    colored_text = ""
    reset_code = "\033[0m"

    for char in diagram_text:
        if char in color_map:
            colored_text += color_map[char] + char + reset_code
        else:
            colored_text += char

    return colored_text


def create_diagram_legend():
    """Create a legend for diagram symbols."""
    legend = [
        "Legend:",
        "---------------------",
        "⬛ = Node/Component",
        "→ = Flow/Dependency",
        "◆ = Decision Point",
        "⭘ = Start/End",
        "📄 = Document",
        "🔄 = Process",
    ]
    return "\n".join(legend)


def export_diagram(diagram_text, output_path, format_type="txt"):
    """Export diagram to file."""
    if not output_path:
        logger.warning("No output path provided")
        return False

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(diagram_text)

        logger.info("Diagram exported to %s", output_path)
        return True
    except IOError as e_io:
        logger.error("Failed to write diagram to %s: %s", output_path, e_io)
        return False
    except Exception as e_export:
        logger.error("Error exporting diagram: %s", e_export)
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except SystemExit:
        pass
    except Exception as e:
        logger.critical("Unhandled exception: %s", e)
        traceback.print_exc()
        sys.exit(1)
