#!/usr/bin/env python3
"""
GitHub Push Utility

This script pushes generated RTM files and other outputs to GitHub.
"""

import sys
import logging
import argparse
from pathlib import Path
import datetime

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Import required modules
try:
    from generate_rtm import load_config
    from src.utils.github_integration import GitHubIntegration
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Push RTM outputs to GitHub repository"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument(
        "--output-dir", default="output", help="Directory containing output files"
    )
    parser.add_argument("--message", default=None, help="Custom commit message")
    parser.add_argument(
        "--include-rtm", action="store_true", default=True, help="Include RTM files"
    )
    parser.add_argument(
        "--include-outline",
        action="store_true",
        default=True,
        help="Include outline files",
    )
    parser.add_argument(
        "--include-diagrams",
        action="store_true",
        default=True,
        help="Include diagram files",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include all files in output directory",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Load configuration
    config = load_config(args.config)

    # Check if GitHub integration is enabled
    github_config = config.get("github", {})
    if not github_config.get("enabled", False):
        logger.error("GitHub integration is not enabled in configuration")
        logger.error(
            "To enable, set 'enabled: true' in the github section of your configuration"
        )
        return 1

    # Initialize GitHub integration
    github = GitHubIntegration(config)

    # Create default commit message if not provided
    if not args.message:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        args.message = f"Update RTM outputs - {timestamp}"

    # Get files to push
    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        logger.error(f"Output directory not found: {output_dir}")
        return 1

    files_to_push = []

    if args.include_all:
        # Include all files in output directory
        files_to_push = [str(f) for f in output_dir.glob("*.*")]
    else:
        # Include RTM files
        if args.include_rtm:
            rtm_files = []
            rtm_files.extend(
                list(output_dir.glob("requirements_traceability_matrix.*"))
            )
            rtm_files.extend(list(output_dir.glob("*_rtm.*")))
            files_to_push.extend([str(f) for f in rtm_files])

        # Include outline files
        if args.include_outline:
            outline_files = []
            outline_files.extend(list(output_dir.glob("*_outline.*")))
            files_to_push.extend([str(f) for f in outline_files])

        # Include diagram files
        if args.include_diagrams:
            diagram_files = []
            diagram_files.extend(list(output_dir.glob("*_diagram.*")))
            files_to_push.extend([str(f) for f in diagram_files])

            # Create ASCII diagram files if they don't exist
            try:
                from scripts.modules.ascii_diagram import generate_ascii_diagram

                # Generate RTM diagram
                rtm_diagram = generate_ascii_diagram("rtm")
                rtm_diagram_path = output_dir / "rtm_diagram.txt"
                with open(rtm_diagram_path, "w", encoding="utf-8") as f:
                    f.write(rtm_diagram)
                files_to_push.append(str(rtm_diagram_path))

                # Generate pipeline diagram
                pipeline_diagram = generate_ascii_diagram("pipeline")
                pipeline_diagram_path = output_dir / "pipeline_diagram.txt"
                with open(pipeline_diagram_path, "w", encoding="utf-8") as f:
                    f.write(pipeline_diagram)
                files_to_push.append(str(pipeline_diagram_path))

            except ImportError:
                logger.warning(
                    "ASCII diagram module not found. Skipping diagram generation."
                )

    # Remove duplicates
    files_to_push = list(set(files_to_push))

    if not files_to_push:
        logger.error("No files found to push")
        return 1

    logger.info(f"Pushing {len(files_to_push)} files to GitHub repository")
    logger.debug(f"Files to push: {files_to_push}")

    # Make sure repository is cloned/updated
    if not github.clone_repository():
        logger.error("Failed to clone/update repository")
        for error in github.errors:
            logger.error(f"Error: {error}")
        return 1

    # Push files to repository
    if github.commit_and_push_changes(files_to_push, args.message):
        logger.info("Successfully pushed files to GitHub repository")
        logger.info(f"Repository URL: {github.repo_url}")
        logger.info(f"Branch: {github.branch}")
        return 0
    else:
        logger.error("Failed to push files to GitHub repository")
        for error in github.errors:
            logger.error(f"Error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
