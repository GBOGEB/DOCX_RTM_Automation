#!/usr/bin/env python3
"""
Requirements Traceability Matrix (RTM) Core Generator

This module provides the core functionality to extract requirements
from markdown files and generate a structured RTM.
"""

import os
import re
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RequirementExtractor:
    """Extract requirements from markdown content"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the requirement extractor
        
        Args:
            config: Configuration dictionary with extraction settings
        """
        self.config = config or {}
        self.patterns = self._compile_patterns()
        self.current_section = ""
        self.current_lcp_phase = "1"  # Default LCP phase
        self.req_counter = 0
    
    def _compile_patterns(self) -> List[re.Pattern]:
        """Compile regex patterns from config"""
        default_patterns = [
            r'[R|r]equirement',
            r'shall',
            r'must',
            r'[R|r]eq-\d+',
            r'[R|r]eq_\d+'
        ]
        
        patterns = []
        config_patterns = self.config.get('requirement_patterns', [])
        
        # Use config patterns if available, otherwise use defaults
        pattern_list = [p.get('pattern') for p in config_patterns] if config_patterns else default_patterns
        
        for pattern in pattern_list:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                patterns.append(compiled)
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        
        return patterns
    
    def extract_from_markdown(self, markdown_file: str) -> List[Dict[str, Any]]:
        """
        Extract requirements from a markdown file
        
        Args:
            markdown_file: Path to the markdown file
            
        Returns:
            List of requirement dictionaries
        """
        self.current_section = Path(markdown_file).stem
        self.req_counter = 0
        requirements = []
        
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process the content line by line
            lines = content.split('\n')
            current_heading = None
            
            for i, line in enumerate(lines):
                # Update current heading for context
                if line.startswith('#'):
                    heading_match = re.match(r'^(#+)\s+(.*?)(?:\s+\1)?$', line)
                    if heading_match:
                        level = len(heading_match.group(1))
                        heading_text = heading_match.group(2).strip()
                        current_heading = heading_text
                        
                        # Check if heading contains LCP phase marker [LCP:X]
                        lcp_match = re.search(r'\[LCP:(\d+)\]', heading_text)
                        if lcp_match:
                            phase = lcp_match.group(1)
                            self.current_lcp_phase = phase
                            logger.debug(f"Detected LCP phase {phase} in heading: {heading_text}")
                
                # Check if this line contains a requirement
                if self._is_requirement(line):
                    # Generate requirement ID
                    self.req_counter += 1
                    req_id = self._generate_id()
                    
                    # Extract requirement attributes
                    attributes = self._extract_attributes(line)
                    
                    # Clean the requirement text (remove attribute markers)
                    cleaned_text = self._clean_requirement_text(line)
                    
                    # Create the requirement
                    requirement = {
                        "id": req_id,
                        "text": cleaned_text,
                        "source": markdown_file,
                        "line": i + 1,
                        "section": current_heading or self.current_section,
                        "lcp_phase": self.current_lcp_phase
                    }
                    
                    # Add extracted attributes
                    requirement.update(attributes)
                    
                    # Ensure all expected attributes are present with defaults
                    self._add_default_attributes(requirement)
                    
                    requirements.append(requirement)
        
        except Exception as e:
            logger.error(f"Error extracting requirements from {markdown_file}: {e}")
        
        return requirements
    
    def _is_requirement(self, text: str) -> bool:
        """Check if text contains a requirement pattern"""
        return any(pattern.search(text) for pattern in self.patterns)
    
    def _generate_id(self) -> str:
        """Generate a requirement ID based on config"""
        id_format = self.config.get("id_format", {})
        prefix = id_format.get("prefix", "REQ-")
        digits = id_format.get("digits", 3)
        use_section = id_format.get("section_prefix", True)
        
        if use_section and self.current_section:
            # Use first 3 chars of section name as prefix
            section_prefix = re.sub(r'[^A-Za-z0-9]', '', self.current_section)[:3].upper()
            return f"{prefix}{section_prefix}-{str(self.req_counter).zfill(digits)}"
        else:
            return f"{prefix}{str(self.req_counter).zfill(digits)}"
    
    def _extract_attributes(self, text: str) -> Dict[str, str]:
        """Extract inline attributes like [priority:high]"""
        attributes = {}
        attr_pattern = re.compile(r'\[([a-zA-Z_]+):([^\]]+)\]')
        
        # Find all attribute matches
        for match in attr_pattern.finditer(text):
            attr_name = match.group(1).lower()
            attr_value = match.group(2).strip().lower()
            attributes[attr_name] = attr_value
        
        return attributes
    
    def _clean_requirement_text(self, text: str) -> str:
        """Remove attribute markers from requirement text"""
        attr_pattern = re.compile(r'\[([a-zA-Z_]+):([^\]]+)\]')
        return re.sub(attr_pattern, '', text).strip()
    
    def _add_default_attributes(self, requirement: Dict[str, Any]) -> None:
        """Add default attributes if missing"""
        default_attrs = {
            "priority": "medium",
            "status": "proposed"
        }
        
        for attr, default_value in default_attrs.items():
            if attr not in requirement:
                requirement[attr] = default_value


class RTMGenerator:
    """Generate Requirements Traceability Matrix from requirements"""
    
    def __init__(self, config=None):
        """
        Initialize the RTM generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.extractor = RequirementExtractor(config)
    
    def generate_rtm(self, input_files: List[str], formats: List[str] = None) -> Dict[str, Any]:
        """
        Generate RTM from input files
        
        Args:
            input_files: List of markdown file paths
            formats: List of output formats (json, yaml, markdown)
            
        Returns:
            RTM data structure
        """
        # Extract requirements from each input file
        all_requirements = []
        for file_path in input_files:
            logger.info(f"Processing {file_path}...")
            requirements = self.extractor.extract_from_markdown(file_path)
            all_requirements.extend(requirements)
            logger.info(f"Found {len(requirements)} requirements in {file_path}")
        
        logger.info(f"Total requirements extracted: {len(all_requirements)}")
        
        # Create RTM structure
        rtm = {
            "metadata": {
                "generated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "generator": "DOCX RTM Automation",
                "version": "1.0",
                "input_files": input_files,
                "total_requirements": len(all_requirements)
            },
            "requirements": all_requirements
        }
        
        # Add traceability links if enabled
        if self.config.get("enable_traceability", False):
            self._add_traceability_links(rtm)
        
        return rtm
    
    def _add_traceability_links(self, rtm: Dict[str, Any]) -> None:
        """Add traceability links between requirements"""
        requirements = rtm["requirements"]
        req_ids = {req["id"]: req for req in requirements}
        
        # Look for references in requirement text
        for req in requirements:
            links = []
            for other_id in req_ids:
                if other_id != req["id"] and other_id in req["text"]:
                    # Found a reference to another requirement
                    links.append({
                        "target": other_id,
                        "relation": "references"
                    })
            
            if links:
                req["links"] = links
    
    def save_rtm(self, rtm: Dict[str, Any], output_dir: str, formats: List[str] = None) -> Dict[str, str]:
        """
        Save RTM in requested formats
        
        Args:
            rtm: RTM data structure
            output_dir: Output directory
            formats: List of output formats
            
        Returns:
            Dictionary of format -> output file path
        """
        formats = formats or ["json", "yaml", "markdown"]
        output_files = {}
        
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        base_filename = self.config.get("output_file", "requirements_traceability_matrix")
        
        if "json" in formats:
            json_file = os.path.join(output_dir, f"{base_filename}.json")
            self._export_json(rtm, json_file)
            output_files["json"] = json_file
        
        if "yaml" in formats:
            yaml_file = os.path.join(output_dir, f"{base_filename}.yaml")
            self._export_yaml(rtm, yaml_file)
            output_files["yaml"] = yaml_file
        
        if "markdown" in formats:
            md_file = os.path.join(output_dir, f"{base_filename}.md")
            self._export_markdown(rtm, md_file)
            output_files["markdown"] = md_file
            
        if "html" in formats:
            html_file = os.path.join(output_dir, f"{base_filename}.html")
            self._export_html(rtm, html_file)
            output_files["html"] = html_file
        
        logger.info("RTM generation complete")
        for fmt, file_path in output_files.items():
            logger.info(f"  {fmt}: {file_path}")
        
        return output_files
    
    def _export_json(self, rtm: Dict[str, Any], output_file: str) -> None:
        """Export RTM as JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(rtm, f, indent=2)
    
    def _export_yaml(self, rtm: Dict[str, Any], output_file: str) -> None:
        """Export RTM as YAML"""
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(rtm, f, default_flow_style=False)
    
    def _export_markdown(self, rtm: Dict[str, Any], output_file: str) -> None:
        """Export RTM as Markdown"""
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("# Requirements Traceability Matrix\n\n")
            
            # Write metadata
            f.write("## Metadata\n\n")
            meta = rtm["metadata"]
            f.write(f"- **Generated**: {meta['generated_date']}\n")
            f.write(f"- **Requirements Count**: {meta['total_requirements']}\n")
            f.write("\n## Requirements\n\n")
            
            # Write requirements table
            f.write("| ID | Description | Section | Priority | Status |\n")
            f.write("|---|---|---|---|---|\n")
            
            for req in rtm["requirements"]:
                req_id = req["id"]
                text = req["text"]
                section = req.get("section", "")
                priority = req.get("priority", "")
                status = req.get("status", "")
                
                f.write(f"| {req_id} | {text} | {section} | {priority} | {status} |\n")
            
            # Write traceability links if any
            has_links = any("links" in req for req in rtm["requirements"])
            if has_links:
                f.write("\n## Traceability Links\n\n")
                f.write("| Source | Relation | Target |\n")
                f.write("|---|---|---|\n")
                
                for req in rtm["requirements"]:
                    if "links" in req:
                        for link in req["links"]:
                            f.write(f"| {req['id']} | {link.get('relation', 'references')} | {link.get('target', '')} |\n")
    
    def _export_html(self, rtm: Dict[str, Any], output_file: str) -> None:
        """Export RTM as HTML"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Requirements Traceability Matrix</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .high { color: #d32f2f; }
        .medium { color: #f57c00; }
        .low { color: #388e3c; }
    </style>
</head>
<body>
    <h1>Requirements Traceability Matrix</h1>
    
    <h2>Metadata</h2>
    <p><strong>Generated:</strong> {0}</p>
    <p><strong>Requirements Count:</strong> {1}</p>
    
    <h2>Requirements</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Description</th>
                <th>Section</th>
                <th>Priority</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
""".format(rtm["metadata"]["generated_date"], rtm["metadata"]["total_requirements"]))
            
            for req in rtm["requirements"]:
                req_id = req["id"]
                text = req["text"]
                section = req.get("section", "")
                priority = req.get("priority", "")
                status = req.get("status", "")
                
                priority_class = f"class=\"{priority}\"" if priority in ["high", "medium", "low"] else ""
                
                f.write(f"            <tr>\n")
                f.write(f"                <td>{req_id}</td>\n")
                f.write(f"                <td>{text}</td>\n")
                f.write(f"                <td>{section}</td>\n")
                f.write(f"                <td {priority_class}>{priority}</td>\n")
                f.write(f"                <td>{status}</td>\n")
                f.write(f"            </tr>\n")
            
            f.write("""        </tbody>
    </table>
""")
            
            # Add traceability links if any
            has_links = any("links" in req for req in rtm["requirements"])
            if has_links:
                f.write("""
    <h2>Traceability Links</h2>
    <table>
        <thead>
            <tr>
                <th>Source</th>
                <th>Relation</th>
                <th>Target</th>
            </tr>
        </thead>
        <tbody>
""")
                
                for req in rtm["requirements"]:
                    if "links" in req:
                        for link in req["links"]:
                            f.write(f"            <tr>\n")
                            f.write(f"                <td>{req['id']}</td>\n")
                            f.write(f"                <td>{link.get('relation', 'references')}</td>\n")
                            f.write(f"                <td>{link.get('target', '')}</td>\n")
                            f.write(f"            </tr>\n")
                
                f.write("""        </tbody>
    </table>
""")
            
            f.write("""</body>
</html>
""")