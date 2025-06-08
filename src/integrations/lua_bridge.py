#!/usr/bin/env python3
"""
Lua-Python Bridge for RTM Automation

Connects Lua scripts used by Pandoc with the Python-based RTM pipeline.
Supports bidirectional conversion between DOCX and Markdown with structure preservation.
"""

import os
import sys
import json
import yaml
import subprocess
import logging
import glob
import argparse
import re  # Add the missing import for regular expressions
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("lua_bridge")


def find_input_document(input_path):
    """
    Find the input document, handling file path issues and providing fallbacks.

    Args:
        input_path: Path or filename of the input document

    Returns:
        Path to the found document or None
    """
    input_path = str(input_path)  # Convert to string if it's a Path object

    # Check if the path exists directly
    if os.path.exists(input_path):
        return os.path.abspath(input_path)

    # Check for common path separator issues
    normalized_path = input_path.replace("\\", "/")
    if os.path.exists(normalized_path):
        return os.path.abspath(normalized_path)

    # Try to find the file by filename in common directories
    filename = os.path.basename(input_path)
    search_dirs = [".", "input", "docs", "documents", "output"]

    for directory in search_dirs:
        if os.path.exists(directory):
            # Direct match
            test_path = os.path.join(directory, filename)
            if os.path.exists(test_path):
                logger.info(f"Found document at: {test_path}")
                return os.path.abspath(test_path)

            # Try with different extensions
            base_name = os.path.splitext(filename)[0]
            for ext in [".docx", ".doc", ".md", ".markdown"]:
                test_path = os.path.join(directory, f"{base_name}{ext}")
                if os.path.exists(test_path):
                    logger.info(f"Found document with alternate extension: {test_path}")
                    return os.path.abspath(test_path)

            # Try glob pattern matching
            pattern = os.path.join(directory, f"*{base_name}*.*")
            matches = glob.glob(pattern)
            if matches:
                logger.info(f"Found similar document: {matches[0]}")
                return os.path.abspath(matches[0])

    logger.error(f"Document not found: {input_path}")
    logger.info("Available documents:")

    for directory in search_dirs:
        if os.path.exists(directory):
            docs = glob.glob(os.path.join(directory, "*.docx")) + glob.glob(
                os.path.join(directory, "*.md")
            )
            if docs:
                logger.info(f"In {directory}/ directory:")
                for doc in docs:
                    logger.info(f"  - {os.path.basename(doc)}")

    return None


def ensure_lua_filters_exist():
    """
    Ensure Lua filters exist, create default ones if needed.

    Returns:
        Dictionary with paths to Lua filters
    """
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    lua_filters = {
        "structure": config_dir / "structure_extraction.lua",
        "rtm": config_dir / "extract_rtm.lua",
        "outline": config_dir / "extend_headings.lua",
    }

    # Create basic structure_extraction.lua if it doesn't exist
    if not lua_filters["structure"].exists():
        with open(lua_filters["structure"], "w", encoding="utf-8") as f:
            f.write(
                """-- Document Structure Extraction Lua filter for Pandoc
-- This filter extracts the document structure during conversion

-- Configuration
local config = {
    output_file = "output/document_structure_raw.json",
    debug = false
}

-- State variables
local document_title = ""
local headings = {}

-- Process headers to extract structure
function Header(el)
    local level = el.level
    local title = pandoc.utils.stringify(el)

    -- Check for section number at the beginning
    local section_num, clean_title = string.match(title, "^(%d+[%d%.%s]*)%s*(.*)")

    if not section_num then
        clean_title = title
    end

    -- Store heading
    table.insert(headings, {
        level = level,
        section = section_num or "",
        title = clean_title,
    })

    -- If this is the first level 1 heading, assume it's the document title
    if level == 1 and #headings == 1 then
        document_title = clean_title
    end

    return el
end

-- Process the entire document at the end
function Pandoc(doc)
    -- Save the extracted structure
    local structure = {
        title = document_title,
        headings = headings
    }

    -- Ensure existence of output directory
    os.execute("mkdir -p output")

    -- Write to JSON file
    local json = pandoc.json.encode(structure)
    local file = io.open(config.output_file, "w")
    if file then
        file:write(json)
        file:close()
    end

    return doc
end

-- Return the filter
return {
    { Header = Header },
    { Pandoc = Pandoc }
}
"""
            )
        logger.info(
            f"Created basic structure_extraction.lua filter at {lua_filters['structure']}"
        )

    # Create basic extract_rtm.lua if it doesn't exist
    if not lua_filters["rtm"].exists():
        with open(lua_filters["rtm"], "w", encoding="utf-8") as f:
            f.write(
                """-- RTM Extraction Lua filter for Pandoc
-- This filter extracts requirements and their relationships

-- Configuration
local config = {
    output_file = "output/requirements_extracted.json",
    debug = false
}

-- State variables
local requirements = {}
local current_section = ""

-- Process headers to track current section
function Header(el)
    current_section = pandoc.utils.stringify(el)
    return el
end

-- Extract requirements from paragraphs
function Para(el)
    local text = pandoc.utils.stringify(el)

    -- Look for requirement IDs (e.g., REQ-001, FR-1.2)
    for req_id in string.gmatch(text, "([A-Z]+-[0-9]+(?:[.][0-9]+)*)") do
        requirements[req_id] = {
            id = req_id,
            text = text,
            section = current_section
        }
    end

    return el
end

-- Process the entire document at the end
function Pandoc(doc)
    -- Convert requirements table to array for JSON
    local req_array = {}
    for id, req in pairs(requirements) do
        table.insert(req_array, req)
    end

    -- Save the extracted requirements
    local structure = {
        requirements = req_array
    }

    -- Ensure existence of output directory
    os.execute("mkdir -p output")

    -- Write to JSON file
    local json = pandoc.json.encode(structure)
    local file = io.open(config.output_file, "w")
    if file then
        file:write(json)
        file:close()
    end

    return doc
end

-- Return the filter
return {
    { Header = Header },
    { Para = Para },
    { Pandoc = Pandoc }
}
"""
            )
        logger.info(f"Created basic extract_rtm.lua filter at {lua_filters['rtm']}")

    # Create basic outline extension filter
    if not lua_filters["outline"].exists():
        with open(lua_filters["outline"], "w", encoding="utf-8") as f:
            f.write(
                """-- Heading Extension Lua filter for Pandoc
-- This filter adds enhanced heading IDs and attributes

function Header(el)
    -- Generate an ID based on header text
    local base_id = pandoc.utils.stringify(el)
                     :gsub("[^%w]+", "-")
                     :gsub("^-+", "")
                     :gsub("-+$", "")
                     :lower()

    -- Add unique ID as attribute
    el.identifier = base_id

    -- Add section-level class
    el.classes:insert("section-level-" .. el.level)

    return el
end

return {
    { Header = Header }
}
"""
            )
        logger.info(
            f"Created basic extend_headings.lua filter at {lua_filters['outline']}"
        )

    return lua_filters


def run_pandoc_with_lua_filter(input_file, output_file, lua_filter):
    """
    Run pandoc with a specific Lua filter.

    Args:
        input_file: Path to input document
        output_file: Path to output markdown file
        lua_filter: Path to Lua filter script

    Returns:
        True if conversion succeeded, False otherwise
    """
    if not os.path.exists(lua_filter):
        logger.error(f"Lua filter not found: {lua_filter}")
        return False

    # Create output directory if needed
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Determine input and output formats
    input_ext = Path(input_file).suffix.lower()
    output_ext = Path(output_file).suffix.lower()

    if input_ext == ".docx" and output_ext == ".md":
        from_format = "docx"
        to_format = "markdown"
    elif input_ext == ".md" and output_ext == ".docx":
        from_format = "markdown"
        to_format = "docx"
    else:
        from_format = None  # Let pandoc auto-detect
        to_format = None  # Let pandoc auto-detect

    # Define command with appropriate options
    cmd = [
        "pandoc",
        str(input_file),
        "-o",
        str(output_file),
        "--lua-filter=" + str(lua_filter),
        "--wrap=none",
        "--standalone",
    ]

    # Add format specifications if determined
    if from_format:
        cmd.extend(["--from", from_format])
    if to_format:
        cmd.extend(["--to", to_format])

    logger.info(f"Running pandoc with filter: {lua_filter}")
    logger.debug(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Pandoc conversion successful")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Pandoc conversion failed: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error(
            "Pandoc not found. Please install pandoc: https://pandoc.org/installing.html"
        )
        return False


def import_structure_extraction_data(json_output_path):
    """
    Import structure data extracted by Lua filter.

    Args:
        json_output_path: Path to the JSON file generated by Lua filter

    Returns:
        Parsed structure data or None if import failed
    """
    if not os.path.exists(json_output_path):
        logger.error(f"Structure data file not found: {json_output_path}")
        return None

    try:
        with open(json_output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(
                f"Loaded structure data with {len(data.get('headings', []))} headings"
            )
            return data
    except Exception as e:
        logger.error(f"Error loading structure data: {e}")
        return None


def integrate_with_rtm_pipeline(structure_data, markdown_file):
    """
    Integrate structure data with the RTM pipeline.

    Args:
        structure_data: Document structure data
        markdown_file: Path to the markdown file

    Returns:
        True if integration succeeded, False otherwise
    """
    try:
        # Save structure data in various formats for the pipeline
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        # Create output paths
        base_name = Path(markdown_file).stem
        outline_json = output_dir / f"{base_name}_outline.json"
        outline_yaml = output_dir / f"{base_name}_outline.yaml"

        # Format data for RTM pipeline
        rtm_data = {
            "document_name": base_name,
            "source_file": str(markdown_file),
            "sections": [],
            "metadata": {
                "title": structure_data.get("title", base_name),
                "total_headings": len(structure_data.get("headings", [])),
            },
        }

        # Process headings into hierarchical sections
        sections = []
        section_stack = []
        current_level = 0

        for heading in structure_data.get("headings", []):
            level = heading.get("level", 1)
            title = heading.get("title", "")
            section_number = heading.get("section", "")

            # Create section object
            section = {
                "title": title,
                "level": level,
                "number": section_number,
                "content": [],
                "subsections": [],
            }

            # Handle hierarchy
            while section_stack and current_level >= level:
                section_stack.pop()
                current_level -= 1

            if section_stack:
                # Add as subsection to parent
                section_stack[-1]["subsections"].append(section)
            else:
                # Top-level section
                sections.append(section)

            # Update stack
            section_stack.append(section)
            current_level = level

        rtm_data["sections"] = sections

        # Save as JSON
        with open(outline_json, "w", encoding="utf-8") as f:
            json.dump(rtm_data, f, indent=2)
        logger.info(f"Saved outline JSON: {outline_json}")

        # Save as YAML
        with open(outline_yaml, "w", encoding="utf-8") as f:
            yaml.dump(rtm_data, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Saved outline YAML: {outline_yaml}")

        return True
    except Exception as e:
        logger.error(f"Error integrating with RTM pipeline: {e}")
        import traceback

        traceback.print_exc()
        return False


def detect_pandoc():
    """
    Detect if pandoc is installed and get version.

    Returns:
        Tuple of (installed, version_string)
    """
    try:
        result = subprocess.run(
            ["pandoc", "--version"], capture_output=True, check=True, text=True
        )
        version_match = re.search(r"pandoc (\d+\.\d+(?:\.\d+)?)", result.stdout)
        if version_match:
            return True, version_match.group(1)
        return True, "unknown version"
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Pandoc with Lua filters for RTM automation"
    )
    parser.add_argument(
        "input_file", nargs="?", help="Input document file (DOCX or MD)"
    )
    parser.add_argument("-o", "--output", help="Output file (MD or DOCX)")
    parser.add_argument(
        "--filter",
        choices=["structure", "rtm", "outline", "all"],
        default="structure",
        help="Lua filter to use",
    )
    parser.add_argument(
        "--roundtrip",
        action="store_true",
        help="Enable roundtrip conversion (DOCX → MD → DOCX)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--list", action="store_true", help="List available documents")

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # Import regex for version detection

    # Check if pandoc is installed
    pandoc_installed, pandoc_version = detect_pandoc()
    if not pandoc_installed:
        logger.error(
            "Pandoc is not installed. Please install it from https://pandoc.org/installing.html"
        )
        return 1
    else:
        logger.info(f"Using Pandoc {pandoc_version}")

    # List available documents if requested or if no input file is provided
    if args.list or not args.input_file:
        logger.info("Available documents:")
        search_dirs = [".", "input", "docs"]
        doc_found = False

        for directory in search_dirs:
            if os.path.exists(directory):
                docx_files = list(Path(directory).glob("*.docx"))
                md_files = list(Path(directory).glob("*.md"))

                if docx_files:
                    doc_found = True
                    logger.info(f"DOCX files in {directory}/:")
                    for i, f in enumerate(docx_files, 1):
                        logger.info(f"  {i}. {f.name}")

                if md_files:
                    doc_found = True
                    logger.info(f"Markdown files in {directory}/:")
                    for i, f in enumerate(md_files, 1):
                        logger.info(f"  {i}. {f.name}")

        if not doc_found:
            logger.warning("No DOCX or MD files found in search directories.")

        if args.list:  # If explicitly asked to list only, exit here
            return 0

        # If no input file provided, prompt user to choose from list
        if not args.input_file:
            if doc_found:
                logger.info("\nTo process a specific file, use:")
                logger.info("  python lua_bridge.py path/to/file.docx")
                logger.info("\nExiting.")
            else:
                logger.error("No input file specified and no documents found.")
            return 0

    # Find input file
    input_path = find_input_document(args.input_file)
    if not input_path:
        return 1

    # Determine input and output types
    input_ext = Path(input_path).suffix.lower()

    # Default output file if not provided
    if args.output:
        output_path = Path(args.output)
    else:
        # Auto-determine output path and type
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        if input_ext == ".docx":
            output_path = output_dir / Path(input_path).with_suffix(".md").name
        else:
            output_path = output_dir / Path(input_path).with_suffix(".docx").name

    # Check that input and output are different formats for normal operation
    if not args.roundtrip and input_ext == output_path.suffix.lower():
        logger.warning(
            f"Input and output have same type ({input_ext}). Use --roundtrip for same-type conversion."
        )

    # Ensure Lua filters exist, create if needed
    lua_filters = ensure_lua_filters_exist()

    # Determine which filters to run
    filters_to_run = []
    if args.filter == "structure" or args.filter == "all":
        filters_to_run.append(("Structure extraction", lua_filters["structure"]))
    if args.filter == "rtm" or args.filter == "all":
        filters_to_run.append(("RTM extraction", lua_filters["rtm"]))
    if args.filter == "outline" or args.filter == "all":
        filters_to_run.append(("Heading extension", lua_filters["outline"]))

    # Run each selected filter
    success = True
    for filter_name, filter_path in filters_to_run:
        logger.info(f"Running {filter_name} filter...")
        result = run_pandoc_with_lua_filter(input_path, output_path, filter_path)
        if not result:
            logger.error(f"{filter_name} filter failed")
            success = False

    if success:
        logger.info(f"All filters completed. Output saved to {output_path}")

        # If structure extraction was done, import the data
        if args.filter in ["structure", "all"]:
            struct_data_path = Path("output/document_structure_raw.json")
            if struct_data_path.exists():
                structure_data = import_structure_extraction_data(struct_data_path)
                if structure_data:
                    logger.info("Structure data imported successfully")
                    # Integrate with RTM pipeline
                    if (
                        output_path.suffix.lower() == ".md"
                    ):  # Only when output is markdown
                        if integrate_with_rtm_pipeline(structure_data, output_path):
                            logger.info("Successfully integrated with RTM pipeline")
                        else:
                            logger.warning("Could not integrate with RTM pipeline")

        # Handle roundtrip conversion if requested
        if args.roundtrip:
            logger.info("Performing roundtrip conversion...")

            # Determine roundtrip output file
            if input_ext == ".docx":
                # DOCX → MD → DOCX
                roundtrip_path = output_path.with_name(
                    f"{output_path.stem}_roundtrip.docx"
                )
                logger.info(f"Converting back to DOCX: {roundtrip_path}")

                # Use outline filter for roundtrip to preserve structure
                result = run_pandoc_with_lua_filter(
                    output_path, roundtrip_path, lua_filters["outline"]
                )
                if result:
                    logger.info(f"Roundtrip conversion complete: {roundtrip_path}")
                else:
                    logger.error("Roundtrip conversion failed")
            else:
                # MD → DOCX → MD
                roundtrip_path = output_path.with_name(
                    f"{output_path.stem}_roundtrip.md"
                )
                logger.info(f"Converting back to Markdown: {roundtrip_path}")

                # Use structure filter for roundtrip to extract structure again
                result = run_pandoc_with_lua_filter(
                    output_path, roundtrip_path, lua_filters["structure"]
                )
                if result:
                    logger.info(f"Roundtrip conversion complete: {roundtrip_path}")
                else:
                    logger.error("Roundtrip conversion failed")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
