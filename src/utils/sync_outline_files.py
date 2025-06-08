#!/usr/bin/env python3
"""
Synchronize document outline files across multiple formats (YAML, JSON, etc.)
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import yaml
import glob
import argparse
import logging
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def sync_outline_files(source_file, output_formats=None, output_dir=None):
    """
    Sync document outline across multiple formats.

    Args:
        source_file: Path to source outline file (YAML or JSON)
        output_formats: List of output formats ('yaml', 'json', etc.)
        output_dir: Directory for output files (default is same dir as source)

    Returns:
        Dictionary with paths to generated files
    """
    source_path = Path(source_file)

    if not source_path.exists():
        logger.error(f"Source file not found: {source_file}")
        return None

    # Determine source format
    source_format = source_path.suffix.lower().replace(".", "")

    # Set defaults
    if output_formats is None:
        output_formats = ["yaml", "json"]

    if output_dir is None:
        output_dir = source_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Load source data
    try:
        outline_data = load_outline(source_path)
    except Exception as e:
        logger.error(f"Failed to load source file: {e}")
        return None

    # Generate output files
    output_files = {}
    stem = source_path.stem

    # If stem ends with _outline or _json, remove that part
    stem = stem.replace("_outline", "").replace("_json", "")

    for output_format in output_formats:
        if output_format.lower() == source_format.lower():
            # Skip if same as source format
            output_files[output_format] = str(source_path)
            continue

        try:
            output_file = output_dir / f"{stem}_outline.{output_format.lower()}"
            save_outline(outline_data, output_file)
            output_files[output_format] = str(output_file)
        except Exception as e:
            logger.error(f"Failed to save {output_format} file: {e}")

    logger.info(f"Synchronized outline to formats: {', '.join(output_files.keys())}")
    return output_files


def load_outline(file_path):
    """Load outline data from file."""
    suffix = file_path.suffix.lower()

    with open(file_path, "r", encoding="utf-8") as f:
        if suffix == ".json":
            return json.load(f)
        elif suffix in (".yaml", ".yml"):
            return yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")


def save_outline(data, file_path):
    """Save outline data to file."""
    suffix = file_path.suffix.lower()

    with open(file_path, "w", encoding="utf-8") as f:
        if suffix == ".json":
            json.dump(data, f, indent=2, ensure_ascii=False)
        elif suffix in (".yaml", ".yml"):
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")


def process_outline_files(input_dir, output_dir=None, output_formats=None):
    """
    Process all outline files in a directory.

    Args:
        input_dir: Directory containing outline files
        output_dir: Directory for output files
        output_formats: List of output formats

    Returns:
        List of paths to output files
    """
    # Set defaults
    if output_formats is None:
        output_formats = ["yaml", "json"]

    if output_dir is None:
        output_dir = os.path.join(PROJECT_ROOT, "output", "outlines")

    os.makedirs(output_dir, exist_ok=True)

    # Find all outline files
    outline_files = []
    for fmt in ("json", "yaml", "yml"):
        pattern = os.path.join(input_dir, f"*_outline.{fmt}")
        outline_files.extend(glob.glob(pattern))

    if not outline_files:
        logger.warning(f"No outline files found in {input_dir}")
        return []

    logger.info(f"Found {len(outline_files)} outline files to process")

    output_files = []
    for outline_file in outline_files:
        results = sync_outline_files(outline_file, output_formats, output_dir)
        if results:
            output_files.extend(results.values())

    return output_files


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Synchronize document outline across formats"
    )
    parser.add_argument("--source", help="Source outline file (YAML or JSON)")
    parser.add_argument(
        "-f",
        "--formats",
        nargs="+",
        choices=["yaml", "json", "yml"],
        help="Output formats (default: all formats)",
    )
    parser.add_argument(
        "-o", "--output-dir", help="Output directory (default: source file directory)"
    )
    parser.add_argument("--input-dir", help="Directory containing input files")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()

    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Standardize format names
    if args.formats:
        for i, fmt in enumerate(args.formats):
            if fmt == "yml":
                args.formats[i] = "yaml"

    # Process a single file
    if args.source:
        output_files = sync_outline_files(args.source, args.formats, args.output_dir)

        if output_files:
            logger.info("Outline synchronized to formats:")
            for fmt, path in output_files.items():
                logger.info(f"  - {fmt}: {path}")
            return 0
        else:
            logger.error("Outline synchronization failed.")
            return 1

    # Process directory if specified
    if args.input_dir:
        input_dir = args.input_dir
    else:
        input_dir = os.path.join(PROJECT_ROOT, "output")

    results = process_outline_files(input_dir, args.output_dir, args.formats)

    if results:
        logger.info(f"Successfully processed {len(results)} files")
        return 0
    else:
        logger.warning("No files were processed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
