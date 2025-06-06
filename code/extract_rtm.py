#!/usr/bin/env python3
"""
Extract Requirements Traceability Matrix
Extract requirements from markdown documents
"""

import re
import yaml
from pathlib import Path
import sys

# Determine project root (assuming this script is in code/ subdirectory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def extract_requirements_from_md(md_file_path_str: str, output_file_str: str = None):
    """Extract requirements from markdown file"""
    md_file_path = Path(md_file_path_str)

    if not md_file_path.exists():
        print(f"Error: Markdown input file not found: {md_file_path}")
        return False

    if output_file_str is None:
        # Default output path relative to project root's output directory
        output_dir = PROJECT_ROOT / "output" / "rtm_extractions"
        output_file_path = output_dir / f"{md_file_path.stem}_requirements.yaml"
    else:
        output_file_path = Path(output_file_str)

    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(md_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        requirements = []

        # Common requirement patterns
        patterns = [
            r"(?:REQ-\d+:?\s*)?(?:The\s+)?(?:system|contractor|applicant)\s+shall\s+([^.]+)",
            r"(?:REQ-\d+:?\s*)?(?:The\s+)?(?:system|contractor|applicant)\s+must\s+([^.]+)",
            r"(?:REQ-\d+:?\s*)?(?:The\s+)?(?:system|contractor|applicant)\s+will\s+([^.]+)",
            r"(REQ-\d+)[:\s]+([^.]+)",
        ]

        req_counter = 1

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                req_text = match.group(0).strip()

                # Extract or generate requirement ID
                req_id_match = re.search(r"REQ-\d+", req_text)
                if req_id_match:
                    req_id = req_id_match.group(0)
                else:
                    req_id = f"REQ-AUTO-{req_counter:03d}"
                    req_counter += 1

                # Clean up the requirement text
                clean_text = re.sub(r"^REQ-\d+:?\s*", "", req_text)

                requirements.append(
                    {
                        "id": req_id,
                        "text": clean_text,
                        "type": (
                            "functional"
                            if "shall" in req_text.lower()
                            else "constraint"
                        ),
                        "source": "document",
                    }
                )

        # Remove duplicates
        unique_requirements = []
        seen_texts = set()
        for req in requirements:
            if req["text"] not in seen_texts:
                unique_requirements.append(req)
                seen_texts.add(req["text"])

        # Save requirements
        with open(output_file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "requirements": unique_requirements,
                    "total_requirements": len(unique_requirements),
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
            )

    except Exception as e:
        print(f"Error extracting requirements from {md_file_path.name}: {e}")
        return False

    print(
        f"Requirements extracted from {md_file_path.name} and saved to {output_file_path}"
    )
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_md_file = Path(sys.argv[1])
        if not input_md_file.is_absolute():
            # Assume relative to project root if not absolute
            input_md_file = PROJECT_ROOT / input_md_file

        # Allow optional output file argument
        custom_output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        if custom_output_file and not custom_output_file.is_absolute():
            custom_output_file = PROJECT_ROOT / custom_output_file

        extract_requirements_from_md(
            str(input_md_file), str(custom_output_file) if custom_output_file else None
        )
    else:
        # Default example: look for a common output file from a previous step
        default_input_md = (
            PROJECT_ROOT / "output" / "MASTER_1805_1144.md"
        )  # Example path
        print(f"No input file provided. Trying default: {default_input_md}")
        extract_requirements_from_md(str(default_input_md))
