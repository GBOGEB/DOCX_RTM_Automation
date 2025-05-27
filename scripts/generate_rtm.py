#!/usr/bin/env python3
"""
Requirements Traceability Matrix (RTM) Generator

This script extracts requirements from Markdown files and generates
a structured RTM in various formats.
"""

import sys
import yaml
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

# Import the core RTM generator
try:
    from src.core.rtm_generator import RTMGenerator as CoreRTMGenerator
    from src.core.dependency_manager import validate_dependencies
except ImportError as e:
    print(f"Error: Could not import core modules: {e}")
    print("Make sure src/core directory exists and is in PYTHONPATH.")
    sys.exit(1)


def extract_document_outline(config: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
    """
    Extracts the document outline from configuration and builds a properly structured outline object.
    Returns a properly formatted outline object with hierarchical structure.
    """
    sections_data = config.get("sections", [])
    if not sections_data:
        logger.warning("No section data found in configuration for outline generation.")
        return {"sections": []}

    logger.info(f"Extracting document outline from {len(sections_data)} sections")

    # Create a clean list of sections with properly formatted properties
    formatted_sections = []
    for section in sections_data:
        if not isinstance(section, dict):
            logger.warning(f"Skipping invalid section entry (not a dict): {section}")
            continue

        # Essential properties: title and number
        section_title = section.get("title")
        section_number = section.get("number")
        section_level = section.get("level", 1)

        if not section_title:
            logger.warning(f"Skipping section without title: {section}")
            continue

        # Create a clean section object with consistent properties
        formatted_section = {
            "title": section_title,
            "level": section_level
        }

        # Add section number if available
        if section_number:
            formatted_section["number"] = str(section_number)

        # Add any other properties that exist in the original section
        for key, value in section.items():
            if key not in ["title", "level", "number"]:
                formatted_section[key] = value

        formatted_sections.append(formatted_section)

    # Sort sections by number (if available) and level
    try:
        formatted_sections.sort(key=lambda s: (
            s.get("number", "").split(".") if isinstance(s.get("number", ""), str) else [],
            s.get("level", 1)
        ))
    except Exception as e:
        logger.warning(f"Could not sort sections properly: {e}")

    # Build the hierarchical structure
    hierarchical_sections = []
    section_map = {}

    for section in formatted_sections:
        number = section.get("number", "")

        # For flat structure, just add all sections
        hierarchical_sections.append(section)

        # If section has a number, store it in the map for hierarchical relationship building
        if number:
            section_map[number] = section

    return {
        "sections": hierarchical_sections,
        "structure": "flat",  # Can be enhanced to support hierarchical in the future
        "total_sections": len(hierarchical_sections),
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "DOCX_RTM_Automation Outline Processor"
        }
    }


def save_rtm_formats(
    rtm_data: Dict[str, Any],
    output_dir_str: str,
    formats_list: List[str],
    config: Dict[str, Any],
    logger: logging.Logger
):
    """Saves the RTM data to specified formats."""
    output_dir = Path(output_dir_str)
    output_dir.mkdir(parents=True, exist_ok=True)
    base_filename = config.get("output_file", "requirements_traceability_matrix")

    # Process section outline data if available
    sections_data = config.get("sections", [])
    section_lookup = {}
    for section in sections_data:
        if "number" in section and "title" in section:
            section_lookup[section["title"]] = section["number"]

    # Get properly formatted outline data
    outline_data = extract_document_outline(config, logger)

    # Check if we have outline data in the RTM
    rtm_has_outline = len(outline_data["sections"]) > 0
    if rtm_has_outline:
        rtm_data["outline"] = outline_data["sections"]
        logger.info(f"Added outline data with {len(outline_data['sections'])} sections")

    for fmt in formats_list:
        output_file = output_dir / f"{base_filename}.{fmt}"
        logger.info(f"Saving RTM to {output_file} in {fmt} format.")
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                if fmt == "json":
                    json.dump(rtm_data, f, indent=2)
                elif fmt == "yaml":
                    yaml.dump(rtm_data, f, default_flow_style=False, sort_keys=False)
                elif fmt == "markdown":
                    f.write(f"# {base_filename.replace('_', ' ').title()}\n\n")
                    # Add metadata if available
                    metadata = rtm_data.get("metadata", {})
                    if metadata:
                        f.write("## Metadata\n")
                        for key, value in metadata.items():
                            if isinstance(value, list):
                                f.write(f"- {key.replace('_', ' ').title()}: {', '.join(map(str, value))}\n")
                            else:
                                f.write(f"- {key.replace('_', ' ').title()}: {value}\n")
                        f.write("\n")

                    # Add outline if available
                    if rtm_has_outline:
                        f.write("## Document Outline\n\n")
                        for section in sections_data:
                            section_number = section.get("number", "")
                            section_title = section.get("title", "")
                            section_level = section.get("level", 1)
                            indent = "  " * (max(0, section_level - 1))
                            f.write(f"{indent}- {section_number} {section_title}\n")
                        f.write("\n")

                    f.write("## Requirements\n")
                    for req in rtm_data.get("requirements", []):
                        f.write(f"### {req.get('id', 'N/A')}\n")
                        f.write(f"- **Text:** {req.get('text', 'No text provided.')}\n")
                        f.write(f"- **Source:** {req.get('source', 'N/A')}\n")

                        # If section info is available, include it with proper numbering
                        section = req.get("section", None)
                        if section and section in section_lookup:
                            f.write(f"- **Section:** {section_lookup[section]} {section}\n")
                        elif section:
                            f.write(f"- **Section:** {section}\n")

                        # Dynamically write other attributes
                        for key, value in req.items():
                            if key not in ['id', 'text', 'source', 'section']:
                                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")
                        f.write("\n")
                else:
                    logger.warning(f"Unsupported format: {fmt}. Skipping.")

            # Create separate outline files with enhanced structure
            if fmt in ["json", "yaml"] and rtm_has_outline:
                outline_file = output_dir / f"{base_filename}_outline.{fmt}"
                with open(outline_file, "w", encoding="utf-8") as f:
                    if fmt == "json":
                        json.dump(outline_data, f, indent=2)
                    elif fmt == "yaml":
                        yaml.dump(outline_data, f, default_flow_style=False, sort_keys=False)
                logger.info(f"Saved enhanced outline data to {outline_file}")

                # Save numbered outline to external path if configured
                numbered_outline_external = None
                if fmt == "json":
                    numbered_outline_external = config.get("numbered_outline_json_external")
                elif fmt == "yaml":
                    numbered_outline_external = config.get("numbered_outline_yaml_external")

                if numbered_outline_external:
                    try:
                        with open(numbered_outline_external, "w", encoding="utf-8") as f:
                            if fmt == "json":
                                json.dump(outline_data, f, indent=2)
                            elif fmt == "yaml":
                                yaml.dump(outline_data, f, default_flow_style=False, sort_keys=False)
                        logger.info(f"Saved numbered outline to external path: {numbered_outline_external}")
                    except Exception as e:
                        logger.error(f"Failed to save numbered outline to {numbered_outline_external}: {e}")

        except Exception as e:
            logger.error(f"Failed to save RTM in {fmt} format to {output_file}: {e}")


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    rtm_default_config_path = Path("config/rtm_config.yaml")
    paths_default_config_path = Path("config/paths.yaml")

    config_path_to_load = Path(config_file) if config_file else rtm_default_config_path

    merged_config = {
        # Defaults from rtm_config.yaml structure
        "export_formats": ["markdown", "json", "yaml"],
        "requirement_patterns": [
            {"pattern": "[R|r]equirement"}, {"pattern": "shall"}, {"pattern": "must"},
            {"pattern": "[R|r]eq-\\d+"}, {"pattern": "[R|r]eq_\\d+"},
        ],
        "id_format": {"prefix": "REQ-", "digits": 3, "section_prefix": True},
        "location_hooks": {
            "section": {"enabled": False, "prefix": "LH1_", "use_section_titles": True},
            "lcp_phase": {
                "enabled": False, "prefix": "LH2_", "default_phase": "1",
                "phases": {
                    "0": "Procurement", "1": "Concept", "2": "Detailed Design (FEED)",
                    "3": "Construction & Factory Acceptance", "4": "Installation & Hook-up",
                    "5": "Commissioning & RCM Start", "6": "SAT & RCM Training",
                    "7": "Operational & User Commissioning", "8": "Integrated Commissioning"
                }
            }
        },
        "attributes": [
            {"name": "priority", "values": ["high", "medium", "low"], "default": "medium"},
            {"name": "status", "values": ["proposed", "approved", "implemented", "verified"], "default": "proposed"},
        ],
        "relationship_types": [
            {"name": "derives", "description": "Requirement derives from parent requirement"},
            {"name": "depends_on", "description": "Requirement depends on another requirement"},
            {"name": "verifies", "description": "Test verifies requirement"}
        ],
        "reports": {
            "include_statistics": False, "include_coverage_metrics": False,
            "hierarchical_view": False, "lcp_phase_summary": False,
            "filters": {"include_rejected": False, "priority_threshold": "low"}
        },
        "visualization": {
            "graph_layout": "hierarchical",
            "node_color": {
                "functional": "#6495ED", "non-functional": "#FFA500",
                "security": "#FF6347", "performance": "#32CD32"
            },
            "edge_colors": {
                "derives": "#000000", "depends_on": "#0000FF", "verifies": "#00FF00"
            }
        },
        "excel_output": {
            "enabled": False,
            "tabs": [
                {"name": "Requirements", "columns": ["ID", "Description", "Location (LH1)", "LCP Phase (LH2)", "Type", "Priority", "Status"]},
                {"name": "LCP Phases", "include_phase_definitions": True},
                {"name": "Metrics", "include_statistics": True}
            ]
        },
        "output_file": "requirements_traceability_matrix",
        "enable_traceability": True,

        # Defaults from paths.yaml structure
        "external_md_input": None,
        "github": {
            "branch": "main", "commit_message": "Update from RTM automation pipeline",
            "enabled": False, "local_path": "", "repo_url": "",
            "user_email": "", "user_name": ""
        },
        "json_output": "output/default.json", # Generic default
        "lcp_phases": { # This seems to duplicate location_hooks.lcp_phase.phases. Consolidate if possible in YAML.
            "0": "Procurement", "1": "Concept", "2": "Detailed Design (FEED)",
            "3": "Construction & Factory Acceptance", "4": "Installation & Hook-up",
            "5": "Commissioning & RCM Start", "6": "SAT & RCM Training",
            "7": "Operational & User Commissioning", "8": "Integrated Commissioning"
        },
        "md_output": "output/default.md", # Generic default
        "metadata": { # RTM metadata, distinct from document metadata
            "generated_date": None, "generator": "DOCX RTM Automation", "version": "1.0"
        },
        "numbered_outline_json_external": None,
        "numbered_outline_yaml_external": None,
        "outline_json": "output/default_outline.json",
        "outline_json_external": None,
        "outline_yaml": "output/default_outline.yaml",
        "outline_yaml_external": None,
        "pandoc_options": {
            "toc": False, "toc_depth": 3, "number_sections": False,
            "standalone": False, "lua_filter": None
        },
        "requirements": [], # Default to an empty list
        "rtm_yaml": "output/default_rtm.yaml", # Generic default
        "secrets": {"openai_key_path": None},
        "sections": [], # Default to an empty list
        "title": "Default Document Title",
        "yaml_output": "output/default.yaml", # Generic default
        "project": {
            "name": "Default Project", "version": "0.0.0",
            "description": "Default project description"
        },
        "paths": {
            "input_dir": "input", "output_dir": "output",
            "logs_dir": "logs", "config_dir": "config",
            "default_markdown_input_dir": "docs/requirements"
        },
        "pandoc_modules": {"init": None, "main": None, "runner": None},
        # Old pipeline structure defaults (from previous iteration)
        "python_path": None,
        "pandoc_path": None,
        "word_master_document": None,
        "markdown_output_from_word": None,
        "pipeline_steps": [] # For the 'pipeline_steps' key from your paths.yaml example
    }

    # Load rtm_config.yaml
    if config_path_to_load.exists():
        try:
            with open(config_path_to_load, "r", encoding="utf-8") as f:
                rtm_config_content = yaml.safe_load(f)
            if rtm_config_content: # Ensure content is not None or empty
                merged_config.update(rtm_config_content) # Merge loaded config over defaults
            logging.info(f"Loaded RTM configuration from {config_path_to_load}")
        except Exception as e:
            logging.error(f"Error loading RTM configuration from {config_path_to_load}: {e}")
            logging.warning("Using default RTM configuration values.")
    else:
        logging.warning(f"RTM configuration file {config_path_to_load} not found.")
        logging.warning("Using default RTM configuration values.")

    # Load paths.yaml
    if paths_default_config_path.exists():
        try:
            with open(paths_default_config_path, "r", encoding="utf-8") as f:
                paths_config_content = yaml.safe_load(f)
            if paths_config_content: # Ensure content is not None or empty
                merged_config.update(paths_config_content) # Merge paths config
            logging.info(f"Loaded paths configuration from {paths_default_config_path}")
        except Exception as e:
            logging.error(f"Error loading paths configuration from {paths_default_config_path}: {e}")
            logging.warning("Proceeding without paths configuration or using defaults if applicable.")
    else:
        logging.info(f"Paths configuration file {paths_default_config_path} not found. Proceeding without it.")

    return merged_config


def main():
    parser = argparse.ArgumentParser(
        description="Generate Requirements Traceability Matrix (RTM)"
    )
    parser.add_argument("--input", nargs="+", help="Input Markdown file(s)", required=False)
    parser.add_argument(
        "--output-dir", default="output", help="Output directory (default: output)"
    )
    parser.add_argument("--config", help="Path to configuration file (e.g., config/rtm_config.yaml)")

    # Define format choices here to be reused
    format_choices = ["json", "yaml", "markdown"]
    default_formats = ["json", "yaml", "markdown"]

    parser.add_argument(
        "--format",
        nargs="+",
        choices=format_choices,
        default=list(default_formats), # Use a copy for the default
        help=f"Output formats (default: {', '.join(default_formats)})",
    )
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies and exit")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    config_data = load_config(args.config)

    # Check dependencies if requested
    if args.check_deps:
        logger.info("Checking dependencies...")
        deps_ok, errors, warnings = validate_dependencies(config_data)

        if errors:
            for error in errors:
                logger.error(error)

        if warnings:
            for warning in warnings:
                logger.warning(warning)

        if deps_ok:
            logger.info("All critical dependencies are available.")
            return 0
        else:
            logger.error("Some dependencies are missing or misconfigured.")
            return 1

    if not args.input:
        # Default to a configurable path (e.g., 'docs/requirements'), or use a hardcoded default.
        # Example: Get from config_data or use 'docs/requirements'
        default_input_dir_str = config_data.get("paths", {}).get("default_markdown_input_dir", "docs/requirements")
        requirements_dir = Path(default_input_dir_str)

        logger.info(f"No input files specified. Looking for Markdown files in {requirements_dir}")

        md_files_found = []
        if requirements_dir.exists() and requirements_dir.is_dir():
            md_files_found = [
                str(f.resolve()) for f in requirements_dir.glob("*.md") if f.is_file()
            ]

        if md_files_found:
            args.input = md_files_found
            logger.info(f"Found {len(md_files_found)} Markdown files in {requirements_dir}")
        else:
            if not requirements_dir.exists():
                logger.warning(f"Directory {requirements_dir} does not exist. Creating it.")
            else:
                logger.warning(f"No Markdown files found in {requirements_dir}.")

            try: # Ensure directory exists before writing
                requirements_dir.mkdir(parents=True, exist_ok=True)
                test_md_content = (
                    "# Test Requirements\n\n"
                    "## Functional Requirements\n\n"
                    "The system shall provide user authentication.\n\n"
                    "The system must support multiple user roles.\n\n"
                    "## Performance Requirements\n\n"
                    "The system shall respond within 2 seconds.\n\n"
                )
                test_md_path = requirements_dir / "test_requirements.md"
                with open(test_md_path, "w", encoding="utf-8") as f:
                    f.write(test_md_content)
                args.input = [str(test_md_path)]
                logger.info(f"Created default test file: {test_md_path}")
            except IOError as e:
                logger.error(f"Failed to create test file {test_md_path}: {e}")
                args.input = []  # Ensure args.input is an empty list if file creation fails

    if not args.input:  # Check again in case file creation failed and args.input became empty
        logger.error("No input files provided or could be created. Exiting.")
        return 1

    logger.info(f"Generating RTM from {len(args.input)} files...")
    logger.info(f"Output formats: {', '.join(args.format)}")

    try:
        generator = CoreRTMGenerator(config_data)
        rtm = generator.generate_rtm(args.input)

        # Call the new standalone save function
        save_rtm_formats(rtm, args.output_dir, args.format, config_data, logger)

        # Save the specific pipeline YAML file
        base_filename_for_pipeline = config_data.get("output_file", "requirements_traceability_matrix")
        rtm_pipeline_yaml_path = Path(args.output_dir) / f"{base_filename_for_pipeline}_pipeline.yaml"
        try:
            with open(rtm_pipeline_yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(rtm, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Pipeline RTM file saved: {rtm_pipeline_yaml_path}")
        except Exception as e:
            logger.error(f"Failed to save pipeline RTM YAML file to {rtm_pipeline_yaml_path}: {e}")

    except Exception as e:
        logger.error(f"Error generating or saving RTM: {e}", exc_info=args.debug)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
