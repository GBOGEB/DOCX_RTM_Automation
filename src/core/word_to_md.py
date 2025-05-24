#!/usr/bin/env python3
"""
Word to Markdown Converter

This module handles the conversion of Word documents to Markdown format
with enhanced support for RTM extraction using the Pandoc integration.
"""

import os
import sys
import argparse
import logging
import yaml
from pathlib import Path

# Add src directory to path if not already there
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import the enhanced Pandoc integration
from src.modules.pandoc_integration import PandocConverter, PandocError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path="config/paths.yaml"):
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary containing configuration
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Convert Word documents to Markdown")
    parser.add_argument("input", help="Input Word document path")
    parser.add_argument("-o", "--output", help="Output Markdown file path")
    parser.add_argument("-c", "--config", help="Configuration file path")
    parser.add_argument("--extract-rtm", action="store_true", help="Extract RTM data during conversion")
    parser.add_argument("--rtm-output", help="RTM data output file")
    parser.add_argument("--lua-filter", help="Path to custom Lua filter")
    parser.add_argument("--no-toc", action="store_true", help="Disable table of contents generation")
    parser.add_argument("--no-numbering", action="store_true", help="Disable section numbering")
    
    return parser.parse_args()

def convert_word_to_md(input_file, output_file, config=None, **kwargs):
    """
    Convert Word document to Markdown using enhanced Pandoc integration.
    
    Args:
        input_file: Path to input Word document
        output_file: Path to output Markdown file
        config: Configuration dictionary (optional)
        **kwargs: Additional parameters for PandocConverter
        
    Returns:
        True if conversion was successful
    """
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return False
    
    # Create output directory if needed
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize converter with config if provided
    config_file = None
    if config and isinstance(config, dict):
        # Create temporary config file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp:
            yaml.dump(config, temp)
            config_file = temp.name
    
    # Extract Pandoc options from config
    pandoc_options = {}
    if config and 'pandoc_options' in config:
        pandoc_options = config['pandoc_options']
    
    # Override with kwargs
    for key, value in kwargs.items():
        pandoc_options[key] = value
    
    # Create converter
    converter = PandocConverter(config_file)
    
    # Build conversion parameters
    params = {
        'from_format': 'docx',
        'to_format': 'markdown',
        'toc': pandoc_options.get('toc', True),
        'toc_depth': pandoc_options.get('toc_depth', 6),
        'number_sections': pandoc_options.get('number_sections', True),
        'lua_filter': pandoc_options.get('lua_filter')
    }
    
    # Override with any kwargs
    params.update(kwargs)
    
    try:
        # Perform the conversion
        logger.info(f"Converting {input_file} to {output_file}")
        converter.convert_document(input_file, output_file, **params)
        
        # Extract RTM data if requested
        if kwargs.get('extract_rtm'):
            rtm_output = kwargs.get('rtm_output')
            if not rtm_output:
                rtm_output = output_path.with_suffix('.rtm.json')
                
            logger.info(f"Extracting RTM data to {rtm_output}")
            converter.extract_rtm_data(output_file, rtm_output)
        
        logger.info(f"Conversion successful. Output saved to {output_file}")
        return True
    except PandocError as e:
        logger.error(f"Conversion error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        # Clean up temporary config file if created
        if config_file and os.path.exists(config_file) and config_file.startswith(tempfile.gettempdir()):
            os.unlink(config_file)

def main():
    """Main function."""
    args = parse_arguments()
    
    # Load configuration
    config_path = args.config or "config/paths.yaml"
    config = load_config(config_path)
    
    # Determine output path if not specified
    output_file = args.output
    if not output_file:
        if 'md_output' in config:
            # Use default from config
            output_file = config['md_output']
        else:
            # Derive from input filename
            output_file = os.path.splitext(args.input)[0] + ".md"
    
    # Override config with command line arguments
    conversion_params = {}
    
    if args.lua_filter:
        conversion_params['lua_filter'] = args.lua_filter
    
    if args.no_toc:
        conversion_params['toc'] = False
    
    if args.no_numbering:
        conversion_params['number_sections'] = False
    
    conversion_params['extract_rtm'] = args.extract_rtm
    if args.rtm_output:
        conversion_params['rtm_output'] = args.rtm_output
    
    # Perform conversion
    success = convert_word_to_md(args.input, output_file, config, **conversion_params)
    
    if success:
        print("Conversion completed successfully.")
        return 0
    else:
        print("Conversion failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
