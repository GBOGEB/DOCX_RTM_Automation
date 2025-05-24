#!/usr/bin/env python3
"""
Clean and format the outline file from corrupted outline.yaml
Supports nested headings up to level 6
"""

import os
import yaml
import json
import sys
from pathlib import Path
import re

def clean_outline(filename='input/MASTER_outline.yaml'):
    """Clean and format the outline file"""
    print(f"Processing outline file: {filename}")
    
    try:
        # Read the input file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract just the outline structure (sections with titles)
        sections = []
        parent_stack = []
        
        # First pass: extract all title entries
        for line in content.split('\n'):
            line = line.strip()
            
            # Skip lines that look like Python code
            if line.startswith('import ') or line.startswith('with ') or \
               line.startswith('print(') or line.startswith('for '):
                continue
            
            # Check if this is a section title line
            if line.startswith('- title:'):
                # Extract the title
                title = line.split('- title:', 1)[1].strip()
                
                # Determine level based on indentation
                indent_level = len(line) - len(line.lstrip())
                # Default to level 1 for top-level items
                level = 1
                
                # If there's indentation, calculate the heading level
                if indent_level > 0:
                    # Calculate level based on indentation (2 spaces per level)
                    level = (indent_level // 2) + 1
                    # Cap at level 6 (HTML supports h1-h6)
                    level = min(level, 6)
                
                # Create a section with title and level
                section = {
                    'title': title,
                    'level': level
                }
                
                # Determine if this is a child section based on children property
                if 'children:' in line:
                    section['has_children'] = True
                
                sections.append(section)
        
        # Create well-structured outline
        outline = {
            'title': 'MASTER Document Outline',
            'sections': []
        }
        
        # Add section numbers
        current_numbering = [0] * 10  # Support up to 10 levels of depth
        
        for i, section in enumerate(sections):
            level = section['level']
            
            # Update numbering for this level
            current_numbering[level-1] += 1
            # Reset all deeper levels
            for j in range(level, len(current_numbering)):
                current_numbering[j] = 0
                
            # Generate section number
            section_number = '.'.join(str(n) for n in current_numbering[:level] if n > 0)
            
            # Create formatted section
            formatted_section = {
                'level': level,
                'title': section['title'],
                'number': section_number
            }
            
            # Add to outline
            outline['sections'].append(formatted_section)
        
        # Save as YAML
        yaml_output = Path('output/MASTER_outline.yaml')
        yaml_output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(yaml_output, 'w', encoding='utf-8') as f:
            yaml.dump(outline, f, default_flow_style=False, sort_keys=False)
        print(f"Cleaned outline saved to: {yaml_output}")
        
        # Save as JSON
        json_output = Path('output/MASTER_outline.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(outline, f, indent=2)
        print(f"JSON version saved to: {json_output}")
        
        return True
        
    except Exception as e:
        print(f"Error cleaning outline: {e}")
        return False

def extract_hierarchical_structure(filename='input/MASTER_outline.yaml'):
    """Extract hierarchical structure from YAML with children"""
    try:
        # Read the input file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Attempt to parse as YAML directly first
        try:
            data = yaml.safe_load(content)
            
            # If it's a list of dictionaries with title and children
            if isinstance(data, list) and all(isinstance(item, dict) and 'title' in item for item in data):
                sections = []
                
                def process_item(item, level=1):
                    section = {
                        'title': item.get('title', ''),
                        'level': level
                    }
                    sections.append(section)
                    
                    # Process children if present
                    children = item.get('children', [])
                    if isinstance(children, list):
                        for child in children:
                            if isinstance(child, dict) and 'title' in child:
                                process_item(child, level + 1)
                
                for item in data:
                    process_item(item)
                
                # Create well-structured outline
                outline = {
                    'title': 'MASTER Document Outline',
                    'sections': []
                }
                
                # Add section numbers
                current_numbering = [0] * 10  # Support up to 10 levels of depth
                
                for section in sections:
                    level = section['level']
                    
                    # Update numbering for this level
                    current_numbering[level-1] += 1
                    # Reset all deeper levels
                    for j in range(level, len(current_numbering)):
                        current_numbering[j] = 0
                        
                    # Generate section number
                    section_number = '.'.join(str(n) for n in current_numbering[:level] if n > 0)
                    
                    # Add number to section
                    formatted_section = {
                        'level': level,
                        'title': section['title'],
                        'number': section_number
                    }
                    
                    outline['sections'].append(formatted_section)
                
                return outline
        except yaml.YAMLError:
            pass
        
        # If direct YAML parsing failed, try manual extraction
        sections = []
        indentation_stack = [0]  # Keep track of indentation levels
        title_stack = []         # Keep track of parent titles
        level_stack = [0]        # Keep track of heading levels
        
        # Regular expression to match - title: entries with possible children
        title_regex = re.compile(r'^(\s*)- title:\s*(.*?)(?:\s+children:.*)?$')
        
        for line in content.split('\n'):
            if 'import yaml' in line or 'with open' in line:
                continue  # Skip Python code
                
            match = title_regex.match(line)
            if match:
                indent = len(match.group(1))
                title = match.group(2).strip()
                
                # Determine level based on indentation
                while indent <= indentation_stack[-1]:
                    indentation_stack.pop()
                    title_stack.pop()
                    level_stack.pop()
                
                indentation_stack.append(indent)
                title_stack.append(title)
                
                # Calculate level based on parent levels
                parent_level = level_stack[-1]
                current_level = parent_level + 1
                level_stack.append(current_level)
                
                # Cap at level 6
                current_level = min(current_level, 6)
                
                sections.append({
                    'title': title,
                    'level': current_level
                })
        
        # Create well-structured outline
        outline = {
            'title': 'MASTER Document Outline',
            'sections': sections
        }
        
        return outline
    
    except Exception as e:
        print(f"Error extracting hierarchical structure: {e}")
        return None

def main():
    """Main function"""
    # Get filename from command line if provided
    filename = sys.argv[1] if len(sys.argv) > 1 else 'input/MASTER_outline.yaml'
    
    # Try hierarchical extraction first
    outline = extract_hierarchical_structure(filename)
    
    if outline and outline['sections']:
        # Save as YAML
        yaml_output = Path('output/MASTER_outline.yaml')
        yaml_output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(yaml_output, 'w', encoding='utf-8') as f:
            yaml.dump(outline, f, default_flow_style=False, sort_keys=False)
        print(f"Hierarchical outline saved to: {yaml_output}")
        
        # Save as JSON
        json_output = Path('output/MASTER_outline.json')
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump(outline, f, indent=2)
        print(f"JSON version saved to: {json_output}")
        
        return 0
    else:
        # Fall back to basic cleaning
        success = clean_outline(filename)
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
