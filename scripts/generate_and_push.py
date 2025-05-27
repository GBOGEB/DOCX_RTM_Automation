#!/usr/bin/env python3
"""
Generate and Push Script

This script generates all RTM outputs and pushes them to GitHub in one step.
"""

import sys
import os
import logging
import argparse
import subprocess
from pathlib import Path
import datetime

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import loading function
try:
    from generate_rtm import load_config
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)


def run_command(command, description, logger):
    """Run a command and log the output."""
    logger.info(f"Running {description}...")
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        logger.info(f"{description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"{description} failed: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Generate RTM outputs and push to GitHub")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--commit-message", default=None, help="Custom commit message")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    # Ensure output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a timestamp for log files and commit messages
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create default commit message if not provided
    commit_message = args.commit_message
    if not commit_message:
        commit_message = f"Update RTM outputs - {timestamp}"
    
    # 1. Generate RTM in all formats
    logger.info("Step 1: Generating RTM in all formats...")
    rtm_cmd = [
        sys.executable,
        "generate_rtm.py",
        "--format", "json", "yaml", "markdown",
        "--output-dir", str(output_dir)
    ]
    if args.config:
        rtm_cmd.extend(["--config", args.config])
    if args.debug:
        rtm_cmd.append("--debug")
        
    if not run_command(rtm_cmd, "RTM generation", logger):
        logger.error("RTM generation failed, stopping process")
        return 1
    
    # 2. Generate ASCII diagrams
    logger.info("Step 2: Generating ASCII diagrams...")
    try:
        from scripts.modules.ascii_diagram import generate_ascii_diagram
        
        # Generate RTM diagram
        rtm_diagram = generate_ascii_diagram("rtm")
        rtm_diagram_path = output_dir / "rtm_diagram.txt"
        with open(rtm_diagram_path, "w", encoding="utf-8") as f:
            f.write(rtm_diagram)
        logger.info(f"Saved RTM diagram to {rtm_diagram_path}")
        
        # Generate pipeline diagram
        pipeline_diagram = generate_ascii_diagram("pipeline")
        pipeline_diagram_path = output_dir / "pipeline_diagram.txt"
        with open(pipeline_diagram_path, "w", encoding="utf-8") as f:
            f.write(pipeline_diagram)
        logger.info(f"Saved pipeline diagram to {pipeline_diagram_path}")
        
        # Generate requirements diagram
        req_diagram = generate_ascii_diagram("requirements")
        req_diagram_path = output_dir / "requirements_diagram.txt"
        with open(req_diagram_path, "w", encoding="utf-8") as f:
            f.write(req_diagram)
        logger.info(f"Saved requirements diagram to {req_diagram_path}")
        
        # Generate tree diagram
        tree_diagram = generate_ascii_diagram("tree")
        tree_diagram_path = output_dir / "tree_diagram.txt"
        with open(tree_diagram_path, "w", encoding="utf-8") as f:
            f.write(tree_diagram)
        logger.info(f"Saved tree diagram to {tree_diagram_path}")
        
    except ImportError:
        logger.warning("ASCII diagram module not found. Skipping diagram generation.")
    
    # 3. Push all outputs to GitHub
    logger.info("Step 3: Pushing all outputs to GitHub...")
    push_cmd = [
        sys.executable,
        "scripts/push_to_github.py",
        "--output-dir", str(output_dir),
        "--include-all",
        "--message", commit_message
    ]
    if args.config:
        push_cmd.extend(["--config", args.config])
    if args.debug:
        push_cmd.append("--debug")
        
    if not run_command(push_cmd, "GitHub push", logger):
        logger.error("GitHub push failed")
        return 1
    
    logger.info("Complete! All RTM outputs have been generated and pushed to GitHub.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
