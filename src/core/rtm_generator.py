#!/usr/bin/env python3
"""
Requirements Traceability Matrix (RTM) Core Generator

This module provides the core functionality to extract requirements
from markdown files and generate a structured RTM.
"""

import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

import sys
from pathlib import Path

# Add project root to path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


class RTMGenerator:
    """
    Core RTM Generator.
    This is a placeholder implementation.
    It should be expanded to parse Markdown files and extract actual requirements.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.logger.info("CoreRTMGenerator initialized.")

        # Log presence of some new configuration sections for awareness
        if self.config.get("location_hooks"):
            self.logger.debug("Location hooks configuration found.")
        if self.config.get("reports"):
            self.logger.debug("Reports configuration found.")
        if self.config.get("visualization"):
            self.logger.debug("Visualization configuration found.")
        if self.config.get("excel_output"):
            self.logger.debug("Excel output configuration found.")
        if self.config.get("requirement_patterns"):
            self.logger.debug(
                f"Loaded {len(self.config['requirement_patterns'])} requirement patterns."
            )

        project_config = self.config.get("project", {})
        if project_config:
            project_name = project_config.get("name", "N/A")
            project_version = project_config.get("version", "N/A")
            self.logger.info(f"Project: {project_name}, Version: {project_version}")

        paths_config = self.config.get("paths", {})
        if paths_config:
            input_dir = paths_config.get("input_dir", "N/A")
            output_dir = paths_config.get("output_dir", "N/A")  # Already logged
            logs_dir = paths_config.get("logs_dir", "N/A")
            config_dir = paths_config.get("config_dir", "N/A")
            self.logger.debug(
                f"Paths config: input_dir='{input_dir}', output_dir='{output_dir}', logs_dir='{logs_dir}', config_dir='{config_dir}'"
            )

        if self.config.get("external_md_input"):
            self.logger.debug(
                f"External MD input path found: {self.config['external_md_input']}"
            )

        if self.config.get("rtm_yaml"):
            self.logger.debug(
                f"RTM YAML output path configured: {self.config['rtm_yaml']}"
            )

        pandoc_opts = self.config.get("pandoc_options")
        if pandoc_opts:
            self.logger.debug(
                f"Pandoc options found: TOC enabled: {pandoc_opts.get('toc', 'N/A')}, Lua filter: {pandoc_opts.get('lua_filter', 'N/A')}"
            )

        github_config = self.config.get("github")
        if github_config:
            self.logger.debug(
                f"GitHub configuration found: Enabled: {github_config.get('enabled', 'N/A')}, Repo URL: {github_config.get('repo_url', 'N/A')}"
            )

        if self.config.get("secrets"):
            self.logger.debug("Secrets configuration found.")

        pipeline_steps_config = self.config.get("pipeline_steps")
        if isinstance(pipeline_steps_config, list):
            self.logger.debug(
                f"Pipeline steps configuration found with {len(pipeline_steps_config)} steps."
            )
        elif (
            pipeline_steps_config
        ):  # If it exists but is not a list (e.g. misconfigured)
            self.logger.warning("Pipeline steps configuration found but is not a list.")

        pandoc_modules_config = self.config.get("pandoc_modules")
        if pandoc_modules_config and isinstance(pandoc_modules_config, dict):
            self.logger.debug(
                f"Pandoc modules configuration found: "
                f"init='{pandoc_modules_config.get('init', 'N/A')}', "
                f"main='{pandoc_modules_config.get('main', 'N/A')}', "
                f"runner='{pandoc_modules_config.get('runner', 'N/A')}'"
            )
        elif pandoc_modules_config:
            self.logger.warning(
                "Pandoc modules configuration found but is not a dictionary."
            )

        requirements_list_config = self.config.get("requirements")
        if isinstance(requirements_list_config, list):
            self.logger.debug(
                f"Requirements list configuration found with {len(requirements_list_config)} items."
            )
        elif requirements_list_config:
            self.logger.warning(
                "Requirements list configuration found but is not a list."
            )

        sections_list_config = self.config.get("sections")
        if isinstance(sections_list_config, list):
            self.logger.debug(
                f"Sections list configuration found with {len(sections_list_config)} items."
            )
        elif sections_list_config:
            self.logger.warning("Sections list configuration found but is not a list.")

        doc_title = self.config.get("title")
        if doc_title:
            self.logger.debug(f"Document title found in config: '{doc_title}'")

        doc_metadata_config = self.config.get(
            "metadata"
        )  # This is the document metadata from paths.yaml
        if doc_metadata_config and isinstance(doc_metadata_config, dict):
            self.logger.debug(
                f"Document metadata found: "
                f"Generator='{doc_metadata_config.get('generator', 'N/A')}', "
                f"Version='{doc_metadata_config.get('version', 'N/A')}', "
                f"Generated Date='{doc_metadata_config.get('generated_date', 'N/A')}'"
            )
        elif doc_metadata_config:
            self.logger.warning(
                "Document metadata configuration found but is not a dictionary."
            )

    def generate_rtm(self, input_files: List[str]) -> Dict[str, Any]:
        """
        Generates the Requirements Traceability Matrix data from input Markdown files.
        Currently, this method returns dummy data.
        """
        self.logger.info(f"CoreRTMGenerator generating RTM from files: {input_files}")

        current_timestamp = datetime.now(timezone.utc).isoformat()

        # Use project version from config for generator_version if available
        project_version = self.config.get("project", {}).get(
            "version", "0.1.0-core-placeholder"
        )
        generator_name = self.config.get("project", {}).get("name", "CoreRTMGenerator")

        rtm_data: Dict[str, Any] = {
            "metadata": {
                "timestamp": current_timestamp,
                "source_files": [str(Path(f).name) for f in input_files],
                "generator_name": generator_name,
                "generator_version": project_version,
            },
            "requirements": [],
        }

        # Include full document structure (outline) directly in RTM
        sections_data = self.config.get("sections", [])
        if sections_data:
            # Build a clean, consistent structure for the document outline
            clean_sections = []
            for section in sections_data:
                if isinstance(section, dict):
                    clean_section = {
                        k: v for k, v in section.items()
                    }  # Copy all properties
                    # Ensure required properties exist
                    if "title" not in clean_section:
                        continue  # Skip sections without title
                    if "number" not in clean_section:
                        clean_section["number"] = ""
                    if "level" not in clean_section:
                        clean_section["level"] = 1
                    clean_sections.append(clean_section)

            rtm_data["outline"] = clean_sections
            self.logger.info(
                f"Including {len(clean_sections)} sections in outline data"
            )

        # Build a section map for matching headings to requirements
        # The format is {"Section Title": {"number": "1.2.3", "level": 3}}
        section_map = {}
        section_number_map = {}  # Maps section numbers to section titles

        for section in sections_data:
            if isinstance(section, dict):
                section_title = section.get("title")
                section_number = section.get("number")
                section_level = section.get("level", 1)

                if section_title:
                    section_map[section_title] = {
                        "number": section_number,
                        "level": section_level,
                    }

                    # Also map section number to title for reverse lookup
                    if section_number:
                        section_number_map[section_number] = section_title

        req_id_counter = 1
        id_prefix = self.config.get("id_format", {}).get("prefix", "REQ-")
        id_digits = self.config.get("id_format", {}).get("digits", 3)

        default_priority = "medium"
        default_status = "proposed"

        attributes_config = self.config.get("attributes", [])
        for attr_conf in attributes_config:
            if attr_conf.get("name") == "priority":
                default_priority = attr_conf.get("default", default_priority)
            elif attr_conf.get("name") == "status":
                default_status = attr_conf.get("default", default_status)

        requirement_patterns_config = self.config.get("requirement_patterns", [])
        num_patterns = len(requirement_patterns_config)

        # Compile patterns for more efficient matching
        import re

        compiled_patterns = []
        for pattern_config in requirement_patterns_config:
            try:
                pattern = pattern_config.get("pattern", "")
                if pattern:
                    compiled_patterns.append(re.compile(pattern))
            except re.error as e:
                self.logger.warning(f"Invalid regex pattern '{pattern}': {e}")

        for md_file_path_str in input_files:
            md_file_path = Path(md_file_path_str)
            self.logger.debug(f"Processing file: {md_file_path.name}")

            # Simple implementation: read the file and look for pattern matches
            try:
                with open(md_file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Split content by lines for basic processing
                lines = content.split("\n")
                current_section = None
                current_section_number = None

                for i, line in enumerate(lines):
                    # Check for headings - possible sections
                    stripped_line = line.strip()
                    if stripped_line.startswith("#"):
                        heading_text = stripped_line.lstrip("#").strip()

                        # Check for exact section title match
                        if heading_text in section_map:
                            current_section = heading_text
                            current_section_number = section_map[current_section][
                                "number"
                            ]
                            self.logger.debug(
                                f"Found section: {current_section} - {current_section_number}"
                            )
                        # Check for section number match
                        else:
                            # Try to extract section number at the start of heading
                            section_match = re.match(
                                r"^\s*(\d+(\.\d+)*)\s+(.+)$", heading_text
                            )
                            if section_match:
                                extracted_number = section_match.group(1)
                                # If this section number is in our map, use it
                                if extracted_number in section_number_map:
                                    current_section = section_number_map[
                                        extracted_number
                                    ]
                                    current_section_number = extracted_number
                                    self.logger.debug(
                                        f"Found section by number: {current_section} - {current_section_number}"
                                    )

                    # Check for requirement patterns
                    is_requirement = False
                    for pattern in compiled_patterns:
                        if pattern.search(line):
                            is_requirement = True
                            break

                    if is_requirement:
                        req_text = line.strip()
                        self.logger.debug(
                            f"Found requirement in {md_file_path.name}, line {i + 1}: {req_text[:50]}..."
                        )

                        requirement_entry = {
                            "id": f"{id_prefix}{req_id_counter:0{id_digits}d}",
                            "text": req_text,
                            "source": str(md_file_path.name),
                            "line": i + 1,
                            "priority": default_priority,
                            "status": default_status,
                            "type": "functional",
                            "verified_by": "TBD",
                        }

                        # Include section information if available
                        if current_section:
                            requirement_entry["section"] = current_section
                            requirement_entry["section_number"] = current_section_number
                            requirement_entry["section_level"] = section_map[
                                current_section
                            ]["level"]

                        rtm_data["requirements"].append(requirement_entry)
                        req_id_counter += 1
            except Exception as e:
                self.logger.error(f"Error processing {md_file_path}: {e}")
                # Add a placeholder requirement to show the file was processed but with errors
                rtm_data["requirements"].append(
                    {
                        "id": f"{id_prefix}{req_id_counter:0{id_digits}d}",
                        "text": f"Error processing file: {e}",
                        "source": str(md_file_path.name),
                        "priority": default_priority,
                        "status": "error",
                        "type": "error",
                        "verified_by": "N/A",
                    }
                )
                req_id_counter += 1

        # Add a placeholder requirement if no requirements were found
        if len(rtm_data["requirements"]) == 0:
            self.logger.warning("No requirements found in any input files.")
            rtm_data["requirements"].append(
                {
                    "id": f"{id_prefix}{req_id_counter:0{id_digits}d}",
                    "text": "No requirements found in the provided files.",
                    "source": "N/A",
                    "priority": default_priority,
                    "status": default_status,
                    "type": "placeholder",
                    "verified_by": "N/A",
                }
            )

        self.logger.info(
            f"CoreRTMGenerator found {len(rtm_data['requirements'])} requirements."
        )
        return rtm_data

    # Note: The save_rtm method is intentionally NOT part of this core generator.
    # Saving is handled by the main script (generate_rtm.py) to keep concerns separate.


if __name__ == "__main__":
    # Example usage for testing this module directly (optional)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
    )

    # Mock configuration similar to what generate_rtm.py would provide
    mock_config = {
        "export_formats": ["markdown", "json"],
        "requirement_patterns": [
            {"pattern": "[R|r]equirement"},
            {"pattern": "shall"},
            {"pattern": "must"},
        ],
        "id_format": {"prefix": "CORE-", "digits": 4, "section_prefix": False},
        "location_hooks": {
            "section": {
                "enabled": True,
                "prefix": "LH1S_",
                "use_section_titles": False,
            },
            "lcp_phase": {"enabled": True, "prefix": "LH2P_", "default_phase": "2"},
        },
        "attributes": [
            {
                "name": "priority",
                "values": ["high", "medium", "low"],
                "default": "high",
            },
            {
                "name": "status",
                "values": ["proposed", "approved"],
                "default": "proposed",
            },
        ],
        "output_file": "core_rtm_test",  # Used by generate_rtm.py for saving, not directly by CoreRTMGenerator
        "project": {
            "name": "CoreRTM Test Project",
            "version": "0.0.1-test",
            "description": "Test project for CoreRTMGenerator direct execution",
        },
    }

    # Create dummy input files for testing
    test_dir = Path("test_input")
    test_dir.mkdir(exist_ok=True)

    test_file_path = test_dir / "test_requirements.md"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write("# Test Requirements\n\n")
        f.write("The system shall provide feature A.\n\n")
        f.write("Requirement 123: The system must support feature B.\n\n")

    # Create a generator instance and test it
    test_generator = RTMGenerator(mock_config)
    test_rtm = test_generator.generate_rtm([str(test_file_path)])

    # Print the result as JSON for visual verification
    import json

    print(json.dumps(test_rtm, indent=2))
