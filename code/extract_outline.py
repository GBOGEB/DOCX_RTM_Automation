#!/usr/bin/env python3
"""
Extract Document Outline
Extract hierarchical structure from markdown files
"""

import re
import yaml
from pathlib import Path

def extract_outline_from_md(md_file, output_file="output/document_outline.yaml"):
    """Extract document outline from markdown file"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        outline = []
        
        # Extract headers
        header_pattern = r'^(#{1,6})\s+(.*?)$'
        
        for match in re.finditer(header_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            title = match.group(2).strip()
            
            # Extract section number if present
            section_match = re.match(r'^(\d+(?:\.\d+)*)\s+(.*)', title)
            if section_match:
                section_num = section_match.group(1)
                clean_title = section_match.group(2)
            else:
                section_num = ""
                clean_title = title
            
            outline.append({
                'level': level,
                'section': section_num,
                'title': clean_title,
                'raw_title': title
            })
        
        # Save outline
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump({
                'document_outline': outline,
                'total_sections': len(outline)
            }, f, default_flow_style=False, allow_unicode=True)
        
        return True
        
    except Exception as e:
        print(f"Error extracting outline: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        extract_outline_from_md(sys.argv[1])
    else:
        extract_outline_from_md("output/MASTER_1805_1144.md")
