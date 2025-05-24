#!/usr/bin/env python3
"""
Requirements Traceability Matrix (RTM) Generator

This script extracts requirements from Markdown files and generates
a structured RTM in various formats.
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src directory to path for module imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the core RTM generator
try:
    from src.core.rtm_generator import RTMGenerator
except ImportError:
    print("Error: Could not import RTM generator module.")
    print("Make sure src/core/rtm_generator.py exists.")
    sys.exit(1)


def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from file or use defaults"""
    default_config_path = "config/rtm_config.yaml"
    
    # Use specified config or default
    config_path = config_file or default_config_path
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            print(f"Loaded configuration from {config_path}")
            return config
        except Exception as e:
            print(f"Error loading configuration from {config_path}: {e}")
            print("Using default configuration instead.")
    else:
        print(f"Configuration file {config_path} not found.")
        print("Using default configuration.")
    
    # Default configuration
    return {
        "requirement_patterns": [
            {"pattern": "[R|r]equirement"},
            {"pattern": "shall"},
            {"pattern": "must"},
            {"pattern": "[R|r]eq-\\d+"},
            {"pattern": "[R|r]eq_\\d+"}
        ],
        "id_format": {
            "prefix": "REQ-",
            "digits": 3,
            "section_prefix": True
        },
        "attributes": [
            {"name": "priority", "values": ["high", "medium", "low"], "default": "medium"},
            {"name": "status", "values": ["proposed", "approved", "implemented", "verified"], "default": "proposed"}
        ],
        "output_file": "requirements_traceability_matrix",
        "enable_traceability": True
    }


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description='Generate Requirements Traceability Matrix (RTM)')
    parser.add_argument('--input', nargs='+', help='Input Markdown file(s)')
    parser.add_argument('--output-dir', default='output', help='Output directory (default: output)')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--format', nargs='+', choices=['json', 'yaml', 'markdown', 'html'], 
                        default=['json', 'yaml', 'markdown'], 
                        help='Output formats (default: json, yaml, markdown)')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    
    args = parser.parse_args()
    
    # Set up logging level
    import logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config = load_config(args.config)
    
    # Look for markdown files in the output directory if no input specified
    if not args.input:
        output_dir = 'output'
        if os.path.exists(output_dir):
            md_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                       if f.endswith('.md') and os.path.isfile(os.path.join(output_dir, f))]
            
            if md_files:
                args.input = md_files
                print(f"Found {len(md_files)} Markdown files in output directory")
            else:
                print("No input files specified and no Markdown files found in output directory")
                # Create a dummy markdown file for testing
                test_md = os.path.join(output_dir, 'test_requirements.md')
                os.makedirs(output_dir, exist_ok=True)
                with open(test_md, 'w', encoding='utf-8') as f:
                    f.write("# Test Requirements\n\n")
                    f.write("## Functional Requirements\n\n")
                    f.write("The system shall provide user authentication.\n\n")
                    f.write("The system must support multiple user roles.\n\n")
                    f.write("## Performance Requirements\n\n")
                    f.write("The system shall respond within 2 seconds.\n\n")
                args.input = [test_md]
                print(f"Created test file: {test_md}")
        else:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")
            # Create a dummy markdown file for testing
            test_md = os.path.join(output_dir, 'test_requirements.md')
            with open(test_md, 'w', encoding='utf-8') as f:
                f.write("# Test Requirements\n\n")
                f.write("## Functional Requirements\n\n")
                f.write("The system shall provide user authentication.\n\n")
                f.write("The system must support multiple user roles.\n\n")
                f.write("## Performance Requirements\n\n")
                f.write("The system shall respond within 2 seconds.\n\n")
            args.input = [test_md]
            print(f"Created test file: {test_md}")
    
    print(f"Generating RTM from {len(args.input)} files...")
    print(f"Output formats: {', '.join(args.format)}")
    
    try:
        # Initialize generator with configuration
        # Fix: Create the generator with config parameter properly
        generator = RTMGenerator(config=config)
        
        # Generate RTM
        rtm = generator.generate_rtm(args.input)
        
        # Save in requested formats
        generator.save_rtm(rtm, args.output_dir, args.format)
        
        # Also save RTM_QQQ.yaml for pipeline compatibility
        rtm_yaml = os.path.join(args.output_dir, "RTM_QQQ.yaml")
        with open(rtm_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(rtm, f, default_flow_style=False)
        print(f"Pipeline RTM file saved: {rtm_yaml}")
        
    except Exception as e:
        print(f"Error generating RTM: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
