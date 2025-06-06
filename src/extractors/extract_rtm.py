#!/usr/bin/env python3
"""
Extract Requirements Traceability Matrix data from Markdown files.
"""

import os
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import glob
import argparse
import logging
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RTMExtractor:
    """
    Extract Requirements Traceability Matrix data from Markdown files.
    """

    def __init__(self):
        # Regex patterns for requirements and test cases
        self.req_pattern = r"REQ-\d+(?:-\d+)*"
        self.test_pattern = r"TC-\d+(?:-\d+)*"
        self.link_pattern = r"\[({}|{})\]\s*->\s*\[({}|{})\]".format(
            self.req_pattern, self.test_pattern, self.req_pattern, self.test_pattern
        )

    def extract_from_file(self, input_file, output_file=None):
        """
        Extract RTM data from a Markdown file and save to JSON.

        Args:
            input_file: Path to input Markdown file
            output_file: Path to output JSON file (if None, derived from input_file)

        Returns:
            Dictionary with extracted RTM data
        """
        input_path = Path(input_file)
        if not input_path.exists():
            logger.error("Input file not found: %s", input_file)
            return None

        if output_file is None:
            output_file = input_path.with_suffix(".rtm.json")

        # Read the input file
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError as e:
            logger.error(f"Failed to read input file: {e}")
            return None

        # Extract RTM data
        rtm_data = self._extract_rtm_data(content)

        # Write output file
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(rtm_data, f, indent=2)

            logger.info(f"RTM data extracted and saved to {output_file}")
            return rtm_data
        except Exception as e:
            logger.error(f"Failed to write output file: {e}")
            return rtm_data  # Return data even if file write fails

    def _extract_rtm_data(self, content):
        """
        Extract RTM data from content.

        Args:
            content: String content to process

        Returns:
            Dictionary with extracted RTM data
        """
        # Extract requirements
        requirements = self._extract_requirements(content)

        # Extract test cases
        test_cases = self._extract_test_cases(content)

        # Extract links
        links = self._extract_links(content)

        return {
            "requirements": requirements,
            "test_cases": test_cases,
            "links": links,
            "stats": {
                "requirements_count": len(requirements),
                "test_cases_count": len(test_cases),
                "links_count": len(links),
            },
        }

    def _extract_requirements(self, content):
        """Extract requirements from content."""
        requirements = {}

        # Find all requirement IDs
        req_ids = set(re.findall(self.req_pattern, content))

        for req_id in req_ids:
            # Find the requirement description
            # Look for a line with the requirement ID and description
            pattern = r"(^|\n).*?({}).*?[:|-]?\s*(.*?)($|\n)".format(re.escape(req_id))
            match = re.search(pattern, content)

            if match:
                description = match.group(3).strip()
                requirements[req_id] = {
                    "id": req_id,
                    "description": description,
                }
            else:
                requirements[req_id] = {
                    "id": req_id,
                    "description": "",
                }

        return requirements

    def _extract_test_cases(self, content):
        """Extract test cases from content."""
        test_cases = {}

        # Find all test case IDs
        tc_ids = set(re.findall(self.test_pattern, content))

        for tc_id in tc_ids:
            # Find the test case description
            # Look for a line with the test case ID and description
            pattern = r"(^|\n).*?({}).*?[:|-]?\s*(.*?)($|\n)".format(re.escape(tc_id))
            match = re.search(pattern, content)

            if match:
                description = match.group(3).strip()
                test_cases[tc_id] = {
                    "id": tc_id,
                    "description": description,
                }
            else:
                test_cases[tc_id] = {
                    "id": tc_id,
                    "description": "",
                }

        return test_cases

    def _extract_links(self, content):
        """Extract links between requirements and test cases."""
        links = []

        # Find direct links using [REQ-xxx] -> [TC-yyy] syntax
        for match in re.finditer(self.link_pattern, content):
            link_text = match.group(0)
            link_parts = re.findall(
                r"\[({}|{})\]".format(self.req_pattern, self.test_pattern), link_text
            )

            if len(link_parts) >= 2:
                source_id = link_parts[0][0]
                target_id = link_parts[1][0]

                # Determine link type (req->test or test->req)
                if re.match(self.req_pattern, source_id) and re.match(
                    self.test_pattern, target_id
                ):
                    link_type = "validates"
                elif re.match(self.test_pattern, source_id) and re.match(
                    self.req_pattern, target_id
                ):
                    link_type = "verifies"
                else:
                    # Both are the same type, use "references"
                    link_type = "references"

                links.append(
                    {"source": source_id, "target": target_id, "type": link_type}
                )

        return links


def process_all_md_files(input_dir, output_dir=None):
    """
    Process all Markdown files in a directory.

    Args:
        input_dir: Directory containing Markdown files
        output_dir: Directory for output JSON files

    Returns:
        List of paths to output JSON files
    """
    # Create output directory if needed
    if not output_dir:
        output_dir = os.path.join(PROJECT_ROOT, "output", "rtm")

    os.makedirs(output_dir, exist_ok=True)

    # Find all Markdown files
    md_files = glob.glob(os.path.join(input_dir, "*.md"))
    md_files.extend(glob.glob(os.path.join(os.path.join(input_dir, "**"), "*.md")))

    if not md_files:
        logger.warning(f"No Markdown files found in {input_dir}")
        return []

    logger.info(f"Found {len(md_files)} Markdown files to process")

    extractor = RTMExtractor()
    output_files = []

    for md_file in md_files:
        output_file = os.path.join(
            output_dir, os.path.splitext(os.path.basename(md_file))[0] + "_rtm.json"
        )
        result = extractor.extract_from_file(md_file, output_file)
        if result:
            output_files.append(output_file)

    return output_files


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Extract RTM data from Markdown")
    parser.add_argument("--input", help="Input Markdown file")
    parser.add_argument("-o", "--output", help="Output JSON file")
    parser.add_argument("--input-dir", help="Directory containing input files")
    parser.add_argument("--output-dir", help="Directory for output files")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    return parser.parse_args()


def main():
    """Main function."""
    args = parse_arguments()

    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Process a single file
    if args.input:
        extractor = RTMExtractor()
        rtm_data = extractor.extract_from_file(args.input, args.output)

        if rtm_data:
            logger.info(
                f"Extracted {rtm_data['stats']['requirements_count']} requirements, "
                f"{rtm_data['stats']['test_cases_count']} test cases, and "
                f"{rtm_data['stats']['links_count']} links."
            )
            return 0
        else:
            logger.error("RTM extraction failed.")
            return 1

    # Process directory if specified
    if args.input_dir:
        input_dir = args.input_dir
    else:
        input_dir = os.path.join(PROJECT_ROOT, "output")

    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = os.path.join(PROJECT_ROOT, "output", "rtm")

    results = process_all_md_files(input_dir, output_dir)

    if results:
        logger.info(f"Successfully processed {len(results)} files:")
        for result in results:
            logger.info(f"  - {result}")
        return 0
    else:
        logger.warning("No files were processed.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
