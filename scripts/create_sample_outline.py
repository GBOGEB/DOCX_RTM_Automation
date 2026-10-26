import yaml
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def create_sample_outline():
    """
    Create a sample YAML outline file for testing purposes.
    This generates a hierarchical structure that mimics a document outline or requirements document.
    """
    # Define the sample outline structure
    sample_outline = {
        "document": {
            "title": "Sample Requirements Document",
            "version": "1.0",
            "sections": [
                {
                    "id": "1",
                    "title": "Introduction",
                    "content": "This is the introduction section.",
                    "subsections": [
                        {
                            "id": "1.1",
                            "title": "Purpose",
                            "content": "The purpose of this document is to outline requirements.",
                        },
                        {
                            "id": "1.2",
                            "title": "Scope",
                            "content": "This document covers system requirements.",
                        },
                    ],
                },
                {
                    "id": "2",
                    "title": "System Requirements",
                    "content": "This section details the system requirements.",
                    "subsections": [
                        {
                            "id": "2.1",
                            "title": "Functional Requirements",
                            "content": "Description of functional requirements.",
                            "requirements": [
                                {
                                    "req_id": "FR-001",
                                    "description": "The system shall allow users to log in.",
                                    "priority": "High",
                                },
                                {
                                    "req_id": "FR-002",
                                    "description": "The system shall provide data export functionality.",
                                    "priority": "Medium",
                                },
                            ],
                        },
                        {
                            "id": "2.2",
                            "title": "Non-Functional Requirements",
                            "content": "Description of non-functional requirements.",
                            "requirements": [
                                {
                                    "req_id": "NFR-001",
                                    "description": "The system shall respond within 2 seconds.",
                                    "priority": "High",
                                },
                                {
                                    "req_id": "NFR-002",
                                    "description": "The system shall be available 99.9% of the time.",
                                    "priority": "High",
                                },
                            ],
                        },
                    ],
                },
            ],
        }
    }

    # Write the outline to a YAML file
    output_file_path = BASE_DIR / "sample_outline.yaml"
    with open(output_file_path, "w", encoding="utf-8") as f:
        yaml.dump(sample_outline, f, default_flow_style=False, sort_keys=False)

    print(f"Sample outline created in {output_file_path.resolve()}")


if __name__ == "__main__":
    create_sample_outline()
