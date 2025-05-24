#!/usr/bin/env python3
"""
DOCX RTM Automation - Main Application
=====================================

Main entry point for the DOCX to RTM automation pipeline.
Handles document conversion, structure extraction, and requirements analysis.

Author: DOCX RTM Automation Project
Version: 1.0.0
License: MIT
"""

import yaml
import sys
import os
import argparse
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Project metadata
__version__ = "1.0.0"
__author__ = "DOCX RTM Automation Project"

def setup_logging(log_level=logging.INFO, debug=False):
    """
    Setup comprehensive logging configuration
    
    Args:
        log_level: Logging level (default: INFO)
        debug: Enable debug mode with verbose output
    """
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"rtm_automation_{timestamp}.log"
    
    # Configure logging format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if debug:
        log_level = logging.DEBUG
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    
    # Setup handlers
    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, mode="a", encoding="utf-8")
    ]
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"DOCX RTM Automation v{__version__} - Logging initialized")
    logger.info(f"Log file: {log_file}")
    
    return logger

def load_configuration(config_path="config/paths.yaml"):
    """
    Load and validate configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Validate required sections
        required_sections = ['paths', 'pandoc_options']
        for section in required_sections:
            if section not in config:
                config[section] = {}
        
        # Set defaults
        defaults = {
            'paths': {
                'input_dir': 'input',
                'output_dir': 'output',
                'logs_dir': 'logs',
                'config_dir': 'config'
            },
            'pandoc_options': {
                'toc': True,
                'toc_depth': 6,
                'number_sections': True,
                'standalone': True
            }
        }
        
        # Merge defaults
        for section, values in defaults.items():
            for key, value in values.items():
                if key not in config[section]:
                    config[section][key] = value
        
        return config
        
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML configuration: {e}")

def check_dependencies():
    """
    Check if required dependencies are available
    
    Returns:
        dict: Status of each dependency
    """
    dependencies = {
        'pandoc': False,
        'python': True  # Assuming Python is available since we're running
    }
    
    # Check Pandoc
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, check=True)
        dependencies['pandoc'] = True
        version = result.stdout.split('\n')[0]
        logging.getLogger(__name__).info(f"Pandoc found: {version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.getLogger(__name__).error("Pandoc not found in PATH")
    
    return dependencies

def run_pandoc_conversion(input_file, output_file, config, logger):
    """
    Run Pandoc conversion with enhanced error handling and validation
    
    Args:
        input_file: Path to input DOCX file
        output_file: Path to output Markdown file
        config: Configuration dictionary
        logger: Logger instance
        
    Returns:
        bool: Success status
    """
    try:
        # Validate inputs
        if not Path(input_file).exists():
            logger.error(f"Input file not found: {input_file}")
            return False
        
        # Create output directory
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Get Pandoc options from config
        pandoc_opts = config.get('pandoc_options', {})
        toc_depth = max(1, min(6, pandoc_opts.get('toc_depth', 6)))  # Clamp to 1-6
        
        # Check for Lua filter
        lua_filter_path = Path("config/extend_headings.lua")
        lua_filter_args = []
        
        if lua_filter_path.exists():
            lua_filter_args = ['--lua-filter', str(lua_filter_path)]
            logger.info(f"Using Lua filter: {lua_filter_path}")
        else:
            logger.warning(f"Lua filter not found: {lua_filter_path}")
        
        # Build Pandoc command
        cmd = [
            'pandoc',
            str(input_file),
            '-f', 'docx',
            '-t', 'markdown',
            '-o', str(output_file)
        ]
        
        # Add optional arguments
        if pandoc_opts.get('toc', True):
            cmd.extend(['--toc', f'--toc-depth={toc_depth}'])
        
        if pandoc_opts.get('number_sections', True):
            cmd.append('--number-sections')
        
        if pandoc_opts.get('standalone', True):
            cmd.append('--standalone')
        
        # Add Lua filter if available
        cmd.extend(lua_filter_args)
        
        # Execute conversion
        logger.info(f"Converting {input_file} to {output_file}")
        logger.debug(f"Pandoc command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            # Validate output
            if Path(output_file).exists() and Path(output_file).stat().st_size > 0:
                logger.info(f"✅ Conversion successful: {output_file}")
                logger.info(f"📄 Output file size: {Path(output_file).stat().st_size:,} bytes")
                return True
            else:
                logger.error("❌ Conversion produced empty or missing output file")
                return False
        else:
            logger.error("❌ Pandoc conversion failed")
            logger.error(f"📤 Stdout: {result.stdout}")
            logger.error(f"📥 Stderr: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Conversion error: {e}")
        return False

def run_additional_processing(output_file, logger):
    """
    Run additional processing modules if available
    
    Args:
        output_file: Path to converted markdown file
        logger: Logger instance
        
    Returns:
        list: List of successfully created output files
    """
    outputs_created = []
    
    # Add paths for module imports
    sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "core"))
    sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "modules"))
    sys.path.insert(0, str(Path(__file__).parent))
    
    # Document outline extraction
    try:
        from extract_outline import extract_outline_from_md
        outline_file = "output/document_outline.yaml"
        logger.info("📋 Extracting document outline...")
        
        if extract_outline_from_md(output_file, outline_file):
            outputs_created.append(outline_file)
            logger.info(f"✅ Document outline extracted: {outline_file}")
        else:
            logger.warning("⚠️ Document outline extraction failed")
            
    except ImportError as e:
        logger.warning(f"⚠️ extract_outline module not available: {e}")
    except Exception as e:
        logger.error(f"❌ Document outline extraction error: {e}")
    
    # Requirements extraction
    try:
        from extract_rtm import extract_requirements_from_md
        requirements_file = "output/requirements.yaml"
        logger.info("📊 Extracting requirements...")
        
        if extract_requirements_from_md(output_file, requirements_file):
            outputs_created.append(requirements_file)
            logger.info(f"✅ Requirements extracted: {requirements_file}")
        else:
            logger.warning("⚠️ Requirements extraction failed")
            
    except ImportError as e:
        logger.warning(f"⚠️ extract_rtm module not available: {e}")
    except Exception as e:
        logger.error(f"❌ Requirements extraction error: {e}")
    
    # ASCII structure diagram
    try:
        from ascii_diagram import generate_structure_diagram
        diagram_file = "output/document_structure.txt"
        logger.info("📈 Generating structure diagram...")
        
        if generate_structure_diagram(output_file, diagram_file):
            outputs_created.append(diagram_file)
            logger.info(f"✅ Structure diagram generated: {diagram_file}")
        else:
            logger.warning("⚠️ Structure diagram generation failed")
            
    except ImportError as e:
        logger.warning(f"⚠️ ascii_diagram module not available: {e}")
    except Exception as e:
        logger.error(f"❌ Structure diagram generation error: {e}")
    
    return outputs_created

def create_argument_parser():
    """Create and configure argument parser"""
    parser = argparse.ArgumentParser(
        description="DOCX RTM Automation - Convert DOCX documents to RTM format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Process default input file
  %(prog)s --input mydoc.docx                 # Process specific file
  %(prog)s --input mydoc.docx --output out/   # Specify output directory
  %(prog)s --debug                            # Enable debug logging
  %(prog)s --config myconfig.yaml             # Use custom config
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        default="input/MASTER_1805_1144.docx",
        help="Input DOCX file path (default: input/MASTER_1805_1144.docx)"
    )
    
    parser.add_argument(
        '--output', '-o',
        help="Output directory or file path (default: output/)"
    )
    
    parser.add_argument(
        '--config', '-c',
        default="config/paths.yaml",
        help="Configuration file path (default: config/paths.yaml)"
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help="Enable debug logging"
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'DOCX RTM Automation v{__version__}'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help="Check dependencies and exit"
    )
    
    return parser

def main():
    """
    Main application entry point
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Parse command line arguments
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(debug=args.debug)
    
    try:
        logger.info("🚀 Starting DOCX RTM Automation pipeline")
        
        # Check dependencies if requested
        if args.check_deps:
            logger.info("🔍 Checking dependencies...")
            deps = check_dependencies()
            for name, available in deps.items():
                status = "✅ Available" if available else "❌ Missing"
                logger.info(f"  {name}: {status}")
            return 0 if all(deps.values()) else 1
        
        # Load configuration
        logger.info("📋 Loading configuration...")
        try:
            config = load_configuration(args.config)
            logger.info(f"✅ Configuration loaded from {args.config}")
        except Exception as e:
            logger.error(f"❌ Configuration error: {e}")
            return 1
        
        # Check dependencies
        deps = check_dependencies()
        if not deps['pandoc']:
            logger.error("❌ Pandoc is required but not available")
            logger.error("   Please install Pandoc: https://pandoc.org/installing.html")
            return 1
        
        # Determine input and output paths
        input_file = Path(args.input)
        
        if args.output:
            output_path = Path(args.output)
            if output_path.is_dir() or str(output_path).endswith('/'):
                output_file = output_path / f"{input_file.stem}.md"
            else:
                output_file = output_path
        else:
            output_file = Path(config['paths']['output_dir']) / f"{input_file.stem}.md"
        
        # Validate input file
        if not input_file.exists():
            logger.error(f"❌ Input file not found: {input_file}")
            return 1
        
        logger.info(f"📖 Input file: {input_file}")
        logger.info(f"📝 Output file: {output_file}")
        
        # Run Pandoc conversion
        logger.info("🔄 Starting document conversion...")
        conversion_success = run_pandoc_conversion(input_file, output_file, config, logger)
        
        if not conversion_success:
            logger.error("💥 Document conversion failed!")
            return 1
        
        # Get file size for summary
        file_size = output_file.stat().st_size
        
        # Run additional processing
        logger.info("🔄 Running additional processing...")
        additional_outputs = run_additional_processing(str(output_file), logger)
        
        # Generate summary
        logger.info("📊 Processing Summary:")
        logger.info(f"  ✅ Main conversion: {output_file} ({file_size:,} bytes)")
        
        for output in additional_outputs:
            try:
                size = Path(output).stat().st_size
                logger.info(f"  ✅ Additional output: {output} ({size:,} bytes)")
            except:
                logger.info(f"  ✅ Additional output: {output}")
        
        total_files = 1 + len(additional_outputs)
        logger.info(f"🎉 Processing completed successfully! Created {total_files} files.")
        
        return 0
        
    except KeyboardInterrupt:
        logger.warning("⚠️ Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        if args.debug:
            import traceback
            logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
