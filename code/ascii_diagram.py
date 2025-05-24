#!/usr/bin/env python3
"""
ASCII Diagram Generator
Generate text-based structure diagrams from documents
"""

import re
from pathlib import Path

def generate_structure_diagram(md_file, output_file="output/document_structure.txt"):
    """Generate ASCII structure diagram from markdown file"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        structure_lines = []
        structure_lines.append("Document Structure")
        structure_lines.append("==================")
        structure_lines.append("")
        
        # Extract headers
        header_pattern = r'^(#{1,6})\s+(.*?)$'
        prev_level = 0
        
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()
            
            # Create indentation
            indent = "  " * (level - 1)
            
            # Create tree structure
            if level > prev_level:
                prefix = "├── " if level > 1 else ""
            else:
                prefix = "├── " if level > 1 else ""
            
            # Clean title
            clean_title = re.sub(r'^\d+(?:\.\d+)*\s*', '', title)
            
            structure_lines.append(f"{indent}{prefix}{clean_title}")
            prev_level = level
        
        structure_lines.append("")
        structure_lines.append("Requirements Summary")
        structure_lines.append("==================")
        
        # Count requirements
        req_count = len(re.findall(r'shall|must|will', content, re.IGNORECASE))
        structure_lines.append(f"Estimated requirements: {req_count}")
        
        # Save structure
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(structure_lines))
        
        return True
        
    except Exception as e:
        print(f"Error generating structure diagram: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        generate_structure_diagram(sys.argv[1])
    else:
        generate_structure_diagram("output/MASTER_1805_1144.md")
