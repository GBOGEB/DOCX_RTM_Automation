#!/usr/bin/env python3
"""
Pandoc Integration Module

This module provides functions to convert between different document formats
using Pandoc, with RTM-specific filters and processing.
"""

import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union

# Set up logging
logger = logging.getLogger(__name__)


def _validate_pandoc_installation() -> bool:
    """Check if pandoc is installed and available in PATH."""
    try:
        subprocess.run(
            ["pandoc", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("Pandoc is not installed or not available in PATH.")
        return False


def _find_lua_filter(
    filter_name: str = "rtm_filter.lua", config_dir: Optional[str] = None
) -> Optional[Path]:
    """Find the Lua filter file in standard locations."""
    search_paths = [
        Path("config/filters"),
        Path("filters"),
    ]

    if config_dir:
        search_paths.insert(0, Path(config_dir) / "filters")

    for search_path in search_paths:
        filter_path = search_path / filter_name
        if filter_path.exists():
            logger.debug(f"Found Lua filter: {filter_path}")
            return filter_path

    logger.warning(
        f"Lua filter '{filter_name}' not found in search paths: {search_paths}"
    )
    return None


def convert_document(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    from_format: str = "markdown",
    to_format: str = "html",
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Convert a document using Pandoc with RTM-specific processing.

    Args:
        input_file: Path to the input file
        output_file: Path to the output file (defaults to input file with new extension)
        from_format: Source format
        to_format: Target format
        config: Configuration dictionary with Pandoc options

    Returns:
        True if conversion was successful, False otherwise
    """
    if not _validate_pandoc_installation():
        logger.error("Pandoc installation validation failed. Aborting conversion.")
        return False

    input_path = Path(input_file)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_file}")
        return False

    # Default output file if not provided
    if output_file is None:
        output_file = input_path.with_suffix(f".{to_format}")
    output_path = Path(output_file)

    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Build Pandoc command
    cmd = [
        "pandoc",
        str(input_path),
        "-o",
        str(output_path),
        f"--from={from_format}",
        f"--to={to_format}",
    ]

    # Apply configuration options
    if config:
        # Add TOC if requested
        if config.get("pandoc_options", {}).get("toc", False):
            cmd.append("--toc")
            toc_depth = config.get("pandoc_options", {}).get("toc_depth")
            if toc_depth:
                cmd.append(f"--toc-depth={toc_depth}")

        # Add number sections if requested
        if config.get("pandoc_options", {}).get("number_sections", False):
            cmd.append("--number-sections")

        # Add standalone if requested
        if config.get("pandoc_options", {}).get("standalone", False):
            cmd.append("--standalone")

        # Add Lua filter if requested or available
        lua_filter_path = None
        lua_filter_config = config.get("pandoc_options", {}).get("lua_filter")

        if lua_filter_config:
            # First check the exact path specified in config
            lua_filter_path = Path(lua_filter_config)
            if not lua_filter_path.exists():
                logger.warning(
                    f"Lua filter specified in config not found: {lua_filter_config}"
                )
                lua_filter_path = None

        if lua_filter_path is None:
            # Try finding the default filter
            config_dir = config.get("paths", {}).get("config_dir")
            lua_filter_path = _find_lua_filter(config_dir=config_dir)

        if lua_filter_path:
            cmd.extend(["--lua-filter", str(lua_filter_path)])
            logger.info(f"Using Lua filter: {lua_filter_path}")

    # Execute pandoc command
    logger.info(f"Executing Pandoc command: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,  # Don't raise exception, we'll handle errors
        )

        if result.returncode != 0:
            logger.error(f"Pandoc conversion failed: {result.stderr}")
            return False

        logger.info(f"Successfully converted {input_path} to {output_path}")
        return True

    except subprocess.SubprocessError as e:
        logger.error(f"Error executing Pandoc: {str(e)}")
        return False


def extract_md_from_docx(
    docx_file: Union[str, Path],
    output_md_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """Extract markdown from a DOCX file."""
    return convert_document(
        input_file=docx_file,
        output_file=output_md_file,
        from_format="docx",
        to_format="markdown",
        config=config,
    )


def convert_md_to_html(
    md_file: Union[str, Path],
    output_html_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """Convert markdown to HTML."""
    return convert_document(
        input_file=md_file,
        output_file=output_html_file,
        from_format="markdown",
        to_format="html",
        config=config,
    )


def convert_md_to_docx(
    md_file: Union[str, Path],
    output_docx_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """Convert markdown to DOCX."""
    return convert_document(
        input_file=md_file,
        output_file=output_docx_file,
        from_format="markdown",
        to_format="docx",
        config=config,
    )


def convert_md_to_pdf(
    md_file: Union[str, Path],
    output_pdf_file: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> bool:
    """Convert markdown to PDF."""
    return convert_document(
        input_file=md_file,
        output_file=output_pdf_file,
        from_format="markdown",
        to_format="pdf",
        config=config,
    )


# Main function for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: pandoc_integration.py <input_file> [output_file] [format]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    to_format = sys.argv[3] if len(sys.argv) > 3 else "html"

    # Simple test configuration
    test_config = {
        "pandoc_options": {
            "toc": True,
            "toc_depth": 3,
            "number_sections": True,
            "standalone": True,
        }
    }

    # Try the conversion
    result = convert_document(
        input_file=input_file,
        output_file=output_file,
        to_format=to_format,
        config=test_config,
    )

    sys.exit(0 if result else 1)
