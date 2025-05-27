#!/usr/bin/env python3
"""
Extract Requirements Traceability Matrix
Extract requirements from markdown documents
"""

import re
import yaml
from pathlib import Path
import os


def extract_requirements_from_md(md_file, output_file="output/requirements.yaml"):
    """Extract requirements from markdown file"""
    try:
        with open(md_file, "r", encoding="utf-8") as f:
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
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(
                {
                    "requirements": unique_requirements,
                    "total_requirements": len(unique_requirements),
                },
                f,
                default_flow_style=False,
                allow_unicode=True,
            )

        return True

    except Exception as e:
        print(f"Error extracting requirements: {e}")
        return False


if __name__ == "__main__":
    import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    if len(sys.argv) > 1:
        extract_requirements_from_md(sys.argv[1])
    else:
        extract_requirements_from_md("output/MASTER_1805_1144.md")
