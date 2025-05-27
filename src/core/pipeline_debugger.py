#!/usr/bin/env python3
"""
Simple Pipeline Debugger

This is a minimal implementation of the pipeline debugger to support
the SRC_Master.py import requirements.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def debug_pipeline(config: Dict[str, Any], interactive: bool = True) -> int:
    """
    Debug the RTM generation pipeline.
    
    Args:
        config: Configuration dictionary
        interactive: Whether to start interactive mode
        
    Returns:
        Exit code (0 on success)
    """
    logger.info("Starting pipeline debugger...")
    
    if interactive:
        print("\nRTM Pipeline Debugger")
        print("====================")
        print("\nConfiguration Summary:")
        print(f"- Project: {config.get('project', {}).get('name', 'Not specified')}")
        print(f"- Version: {config.get('project', {}).get('version', 'Not specified')}")
        
        # Count requirements patterns
        req_patterns = config.get("requirement_patterns", [])
        print(f"- Requirement patterns: {len(req_patterns)}")
        
        # Show output formats
        formats = config.get("export_formats", ["json", "yaml", "markdown"])
        print(f"- Output formats: {', '.join(formats)}")
        
        print("\nDebugger completed successfully.")
    else:
        logger.info("Non-interactive debugging completed")
    
    return 0