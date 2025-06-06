#!/usr/bin/env python3
"""
Enhanced Pandoc Integration Module

This module provides advanced integration with Pandoc for document conversion,
with special support for Lua filters, structured data extraction, and RTM generation.
"""

import os
import sys
import subprocess
import logging
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Union

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PandocError(Exception):
    """Exception raised for Pandoc-related errors."""

    pass


class PandocConverter:
    """Advanced Pandoc document converter with support for Lua filters and RTM."""

    def __init__(self, config_path: str = None):
        """
        Initialize the Pandoc converter.

        Args:
            config_path: Path to YAML configuration file (optional)
        """
        self.pandoc_path = "pandoc"  # Default path
        self.config = {}

        if config_path:
            self.load_config(config_path)
        else:
            # Try default config path
            default_config = Path("config/paths.yaml")
            if default_config.exists():
                self.load_config(str(default_config))

        # Check if Pandoc is available
        if not self._check_pandoc_available():
            logger.warning("Pandoc not found in PATH. Some features may be limited.")

    def load_config(self, config_path: Union[str, Path]):
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}

            # Extract Pandoc path from config
            if "pandoc_path" in self.config:
                self.pandoc_path = self.config["pandoc_path"]

            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")

    def _check_pandoc_available(self) -> bool:
        """Check if Pandoc is available on the system."""
        try:
            result = subprocess.run(
                [self.pandoc_path, "--version"], capture_output=True, check=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def convert_document(
        self,
        input_file: str,
        output_file: str,
        from_format: str = None,
        to_format: str = None,
        lua_filter: str = None,
        extract_metadata: bool = True,
        toc: bool = True,
        toc_depth: int = 6,
        number_sections: bool = True,
        additional_args: List[str] = None,
    ) -> bool:
        """
        Convert document using Pandoc with advanced options.

        Args:
            input_file: Path to input file
            output_file: Path to output file
            from_format: Source format (auto-detected if None)
            to_format: Target format (auto-detected from output extension if None)
            lua_filter: Path to Lua filter script
            extract_metadata: Whether to extract metadata
            toc: Whether to include table of contents
            toc_depth: Depth of table of contents
            number_sections: Whether to number sections
            additional_args: Additional arguments for Pandoc

        Returns:
            True if conversion was successful
        """
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return False

        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

        # Determine formats if not specified
        if not from_format:
            from_format = self._detect_format(input_file)

        if not to_format:
            to_format = self._detect_format(output_file)

        # Build command
        cmd = [self.pandoc_path, input_file, "-o", output_file]

        # Add format specifications if available
        if from_format:
            cmd.extend(["-f", from_format])
        if to_format:
            cmd.extend(["-t", to_format])

        # Add common options
        cmd.extend(["--wrap=none"])  # No line wrapping

        # Add TOC if requested
        if toc:
            cmd.extend(["--toc", f"--toc-depth={min(toc_depth, 6)}"])

        # Add section numbering if requested
        if number_sections:
            cmd.append("--number-sections")

        # Add Lua filter if specified or use from config
        if not lua_filter and "pandoc_options" in self.config:
            lua_filter = self.config["pandoc_options"].get("lua_filter")

        if lua_filter and os.path.exists(lua_filter):
            cmd.extend(["--lua-filter", lua_filter])

        # Add extract-metadata option if requested
        if extract_metadata:
            cmd.append("--standalone")

        # Add any additional arguments
        if additional_args:
            cmd.extend(additional_args)

        # Log the command
        logger.info(f"Converting {input_file} to {output_file}")
        logger.debug(f"Command: {' '.join(cmd)}")

        # Run the conversion
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Conversion successful: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Pandoc conversion failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return False

    def _detect_format(self, file_path: str) -> str:
        """Detect format from file extension"""
        ext = Path(file_path).suffix.lower()
        format_map = {
            ".docx": "docx",
            ".md": "markdown",
            ".markdown": "markdown",
            ".html": "html",
            ".htm": "html",
            ".tex": "latex",
            ".txt": "plain",
        }
        return format_map.get(ext, "markdown")

    def batch_convert(self, batch_config: Dict[str, Any]) -> Dict[str, bool]:
        """
        Perform batch conversion of multiple documents.

        Args:
            batch_config: Dictionary with batch conversion parameters

        Returns:
            Dictionary mapping output files to success status
        """
        results = {}

        if "files" not in batch_config:
            logger.error("Batch config missing 'files' key")
            return results

        for file_config in batch_config["files"]:
            input_file = file_config.get("input")
            output_file = file_config.get("output")

            if not input_file or not output_file:
                logger.error(f"Invalid file config: {file_config}")
                results[output_file or "unknown"] = False
                continue

            success = self.convert_document(
                input_file, output_file, **file_config.get("options", {})
            )
            results[output_file] = success

        return results

    def extract_rtm_data(
        self, markdown_file: str, output_json: str = None
    ) -> Dict[str, Any]:
        """
        Extract RTM data from processed markdown using a special Lua filter.

        Args:
            markdown_file: Path to markdown file
            output_json: Path to output JSON file (optional)

        Returns:
            Dictionary containing extracted RTM data
        """
        # Create temp output file if none provided
        if not output_json:
            output_json = f"{markdown_file}.rtm.json"

        # Get the path to the RTM extraction Lua filter
        rtm_filter = os.path.join(
            os.path.dirname(__file__), "..", "..", "config", "extract_rtm.lua"
        )

        if not os.path.exists(rtm_filter):
            logger.warning(f"RTM extraction filter not found: {rtm_filter}")
            return {}

        # Run pandoc with the RTM extraction filter
        try:
            cmd = [
                self.pandoc_path,
                markdown_file,
                "-o",
                "/dev/null",
                "--lua-filter",
                rtm_filter,
            ]
            subprocess.run(cmd, check=True, capture_output=True)

            # Load extracted data
            if os.path.exists(output_json):
                with open(output_json, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.warning("No RTM data was extracted")
                return {}

        except Exception as e:
            logger.error(f"RTM extraction failed: {e}")
            return {}


def convert_document(
    input_file: str, output_file: str = None, config_file: str = None, **kwargs
) -> bool:
    """
    Simplified interface to convert documents using the PandocConverter.

    Args:
        input_file: Path to input file
        output_file: Path to output file (derived from input if None)
        config_file: Path to configuration file
        **kwargs: Additional parameters for convert_document

    Returns:
        True if conversion was successful
    """
    # Derive output file if not provided
    if not output_file:
        input_path = Path(input_file)
        output_file = str(input_path.with_suffix(".md"))

    converter = PandocConverter(config_file)
    return converter.convert_document(input_file, output_file, **kwargs)


def batch_convert(
    batch_config: Dict[str, Any], config_file: str = None
) -> Dict[str, bool]:
    """
    Simplified interface for batch document conversion.

    Args:
        batch_config: Dictionary with batch conversion parameters
        config_file: Path to configuration file

    Returns:
        Dictionary mapping output files to success status
    """
    converter = PandocConverter(config_file)
    return converter.batch_convert(batch_config)


def extract_rtm(
    markdown_file: str, output_json: str = None, config_file: str = None
) -> Dict[str, Any]:
    """
    Extract RTM data from a markdown file.

    Args:
        markdown_file: Path to markdown file
        output_json: Path for extracted RTM data JSON
        config_file: Path to configuration file

    Returns:
        Dictionary containing RTM data
    """
    converter = PandocConverter(config_file)
    return converter.extract_rtm_data(markdown_file, output_json)


if __name__ == "__main__":
    # Command line interface
    import argparse

    parser = argparse.ArgumentParser(
        description="Pandoc document conversion with RTM support"
    )
    parser.add_argument("input", help="Input file path")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-c", "--config", help="Configuration file path")
    parser.add_argument("--from", dest="from_format", help="Source format")
    parser.add_argument("--to", dest="to_format", help="Target format")
    parser.add_argument("--lua-filter", help="Path to Lua filter")
    parser.add_argument("--extract-rtm", action="store_true", help="Extract RTM data")
    parser.add_argument("--rtm-output", help="RTM data output file")

    args = parser.parse_args()

    if args.extract_rtm:
        # Extract RTM data
        rtm_data = extract_rtm(args.input, args.rtm_output, args.config)
        print(f"Extracted {len(rtm_data.get('requirements', []))} requirements")
    else:
        # Convert document
        success = convert_document(
            args.input,
            args.output,
            args.config,
            from_format=args.from_format,
            to_format=args.to_format,
            lua_filter=args.lua_filter,
        )

        if success:
            print("Conversion successful")
        else:
            print("Conversion failed")
            sys.exit(1)
