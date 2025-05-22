import yaml, re, os, shutil, json
import argparse
from pathlib import Path

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract outline from markdown file')
    parser.add_argument('--external', action='store_true', help='Use external markdown file defined in configuration')
    args = parser.parse_args()

    # Load configuration
    config = yaml.safe_load(open('config/paths.yaml'))
    
    # Determine which markdown file to process
    if args.external and 'external_md_input' in config and os.path.exists(config['external_md_input']):
        md_file = config['external_md_input']
        print(f"Using external markdown file: {md_file}")
    else:
        md_file = config['md_output']
        print(f"Using default markdown output file: {md_file}")
    
    # Check if the file exists
    if not os.path.exists(md_file):
        print(f"Error: Markdown file not found: {md_file}")
        return
    
    # Read the file
    lines = open(md_file, encoding="utf-8").readlines()

    # Extract outline
    outline = [
        {'level': len(m.group(1)), 'title': m.group(2).strip()}
        for l in lines if (m := re.match(r'^(#{1,7})\s(.*)', l))
    ]

    # Generate numbered outline
    numbered_outline = []
    counter = [0, 0, 0, 0, 0, 0, 0]  # For up to 7 levels
    last_level = 0

    for item in outline:
        level = item['level']
        
        # Reset lower level counters
        for i in range(level, len(counter)):
            counter[i] = 0
        
        # Increment current level counter
        counter[level-1] += 1
        
        # Create section number
        section_number = ".".join([str(counter[i]) for i in range(level)])
        
        # Add to numbered outline
        numbered_outline.append({
            'level': level,
            'title': item['title'],
            'section': section_number
        })

    # Save outline files
    yaml.dump(outline, open(config['outline_yaml'], "w"), allow_unicode=True)
    print(f"✅ Outline YAML created with {len(outline)} entries.")

    # Save JSON version of outline
    outline_json_path = os.path.splitext(config['outline_yaml'])[0] + '.json'
    json.dump(outline, open(outline_json_path, "w"), indent=2)
    print(f"✅ Outline JSON created with {len(outline)} entries.")

    # Save numbered outline files
    numbered_outline_yaml = os.path.join(os.path.dirname(config['outline_yaml']), 'MASTER_numbered_outline.yaml')
    yaml.dump(numbered_outline, open(numbered_outline_yaml, "w"), allow_unicode=True)

    numbered_outline_json = os.path.join(os.path.dirname(config['outline_yaml']), 'MASTER_numbered_outline.json')
    json.dump(numbered_outline, open(numbered_outline_json, "w"), indent=2)
    print(f"✅ Numbered outline files created.")

    # Also save to external locations if configured
    if 'outline_yaml_external' in config and config['outline_yaml_external']:
        os.makedirs(os.path.dirname(config['outline_yaml_external']), exist_ok=True)
        yaml.dump(outline, open(config['outline_yaml_external'], "w"), allow_unicode=True)
        print(f"✅ External Outline YAML updated.")

    if 'outline_json_external' in config and config['outline_json_external']:
        os.makedirs(os.path.dirname(config['outline_json_external']), exist_ok=True)
        json.dump(outline, open(config['outline_json_external'], "w"), indent=2)
        print(f"✅ External Outline JSON updated.")

    if 'numbered_outline_yaml_external' in config and config['numbered_outline_yaml_external']:
        os.makedirs(os.path.dirname(config['numbered_outline_yaml_external']), exist_ok=True)
        yaml.dump(numbered_outline, open(config['numbered_outline_yaml_external'], "w"), allow_unicode=True)
        print(f"✅ External Numbered Outline YAML updated.")

    if 'numbered_outline_json_external' in config and config['numbered_outline_json_external']:
        os.makedirs(os.path.dirname(config['numbered_outline_json_external']), exist_ok=True)
        json.dump(numbered_outline, open(config['numbered_outline_json_external'], "w"), indent=2)
        print(f"✅ External Numbered Outline JSON updated.")

    print(f"✅ All outline processing complete.")

if __name__ == "__main__":
    main()
