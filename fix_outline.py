#!/usr/bin/env python3
"""
Fix corrupted outline YAML/JSON files by properly structuring them
"""

import os
import sys
import yaml
import json
from pathlib import Path

def fix_outline_file(input_file, output_file=None):
    """
    Fix a corrupted outline YAML/JSON file
    
    Args:
        input_file: Path to the corrupted outline file
        output_file: Path to save the fixed file (defaults to overwriting input)
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # If output_file not specified, overwrite the input file
        if output_file is None:
            output_file = input_file
        
        print(f"Fixing outline file: {input_file}")
        print(f"Output will be saved to: {output_file}")
        
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract outline structure only (remove any embedded code)
        sections = []
        current_section = None
        in_yaml_section = True
        
        for line in content.split('\n'):
            # Skip lines that look like Python code
            if line.strip().startswith('import ') or line.strip().startswith('with '):
                in_yaml_section = False
                continue
                
            if line.strip().startswith('print(') or line.strip().startswith('for '):
                in_yaml_section = False
                continue
            
            # If we're in a yaml section and line starts with '- title:', parse it
            if in_yaml_section and line.strip().startswith('- title:'):
                title = line.split('- title:', 1)[1].strip()
                current_section = {'title': title, 'children': []}
                sections.append(current_section)
            
            # If it's a child section entry
            elif in_yaml_section and line.strip().startswith('- title:') and current_section:
                title = line.split('- title:', 1)[1].strip()
                current_section['children'].append({'title': title})
        
        # Create proper outline structure
        outline = {
            'title': 'Document Outline',
            'sections': []
        }
        
        # Process the extracted sections
        level = 1
        for i, section in enumerate(sections):
            # Create a properly formatted section
            formatted_section = {
                'level': level,
                'title': section['title'],
                'number': str(i + 1)
            }
            
            # Add children if they exist
            if section['children']:
                child_level = level + 1
                for j, child in enumerate(section['children']):
                    child_section = {
                        'level': child_level,
                        'title': child['title'],
                        'number': f"{i + 1}.{j + 1}"
                    }
                    outline['sections'].append(child_section)
            
            # Add the main section
            outline['sections'].append(formatted_section)
        
        # Write the fixed outline to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(outline, f, default_flow_style=False, sort_keys=False)
        
        print("Fixed outline file saved!")
        
        # If this is a YAML file and we want JSON too
        base, ext = os.path.splitext(output_file)
        if ext.lower() in ['.yaml', '.yml'] and os.path.exists(base + '.json'):
            json_output = base + '.json'
            print(f"Also updating JSON version: {json_output}")
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2)
            print("JSON version updated!")
        
        return True
        
    except Exception as e:
        print(f"Error fixing outline file: {e}")
        return False

def create_sample_outline(output_file):
    """Create a sample well-formatted outline file"""
    outline = {
        'title': 'MASTER Document Outline',
        'sections': [
            {
                'level': 1,
                'title': 'Introduction',
                'number': '1'
            },
            {
                'level': 2,
                'title': 'Purpose',
                'number': '1.1'
            },
            {
                'level': 2,
                'title': 'Scope',
                'number': '1.2'
            },
            {
                'level': 1,
                'title': 'System Requirements',
                'number': '2'
            },
            {
                'level': 2,
                'title': 'Functional Requirements',
                'number': '2.1'
            },
            {
                'level': 3,
                'title': 'User Management',
                'number': '2.1.1'
            }
        ]
    }
    
    # Determine file format from extension
    ext = os.path.splitext(output_file)[1].lower()
    
    try:
        if ext in ['.yaml', '.yml']:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(outline, f, default_flow_style=False, sort_keys=False)
        elif ext == '.json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2)
        else:
            print(f"Unsupported file extension: {ext}")
            return False
        
        print(f"Created sample outline file: {output_file}")
        return True
    except Exception as e:
        print(f"Error creating sample outline: {e}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python fix_outline.py <input_file> [output_file]")
        print("       python fix_outline.py --create <output_file>")
        return 1
    
    if sys.argv[1] == '--create':
        if len(sys.argv) < 3:
            print("Error: Please specify output file path for sample creation")
            return 1
        return 0 if create_sample_outline(sys.argv[2]) else 1
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    return 0 if fix_outline_file(input_file, output_file) else 1

if __name__ == "__main__":
    sys.exit(main())
