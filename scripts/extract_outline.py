#!/usr/bin/env python3
"""
Document Outline Extraction Tool

This tool extracts the document outline (section structure) from a configuration file
and outputs it in various formats (JSON, YAML).
"""

import sys
import yaml
import json
import argparse
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import the outline extraction function from the main RTM generator
from generate_rtm import extract_document_outline, load_config


def main():
    parser = argparse.ArgumentParser(
        description="Extract and save document outline from configuration"
    )
    parser.add_argument("--config", help="Path to configuration file (e.g., config/paths.yaml)")
    parser.add_argument(
        "--output-dir", default="output", help="Output directory (default: output)"
    )
    parser.add_argument(
        "--format",
        nargs="+",
        choices=["json", "yaml"],
        default=["json", "yaml"],
        help="Output formats (default: json yaml)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Load configuration
    config_data = load_config(args.config)
    
    # Extract document outline
    outline_data = extract_document_outline(config_data, logger)
    
    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save outline in requested formats
    base_filename = config_data.get("output_file", "document_outline")
    
    for fmt in args.format:
        output_file = output_dir / f"{base_filename}_outline.{fmt}"
        logger.info(f"Saving outline to {output_file}")
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                if fmt == "json":
                    json.dump(outline_data, f, indent=2)
                elif fmt == "yaml":
                    yaml.dump(outline_data, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            logger.error(f"Failed to save outline in {fmt} format: {e}")
            
    # If external paths are specified in config, save there too
    if "numbered_outline_json_external" in config_data and "json" in args.format:
        try:
            external_path = config_data["numbered_outline_json_external"]
            with open(external_path, "w", encoding="utf-8") as f:
                json.dump(outline_data, f, indent=2)
            logger.info(f"Saved JSON outline to external path: {external_path}")
        except Exception as e:
            logger.error(f"Failed to save to external JSON path: {e}")
            
    if "numbered_outline_yaml_external" in config_data and "yaml" in args.format:
        try:
            external_path = config_data["numbered_outline_yaml_external"]
            with open(external_path, "w", encoding="utf-8") as f:
                yaml.dump(outline_data, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved YAML outline to external path: {external_path}")
        except Exception as e:
            logger.error(f"Failed to save to external YAML path: {e}")
    
    logger.info(f"Successfully extracted outline with {len(outline_data['sections'])} sections")
    return 0


if __name__ == "__main__":
    sys.exit(main())
