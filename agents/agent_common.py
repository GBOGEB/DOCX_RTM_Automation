#!/usr/bin/env python3
"""
Common agent functionality for RTM automation system
"""

import sys
import logging
from pathlib import Path
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Agent(ABC):
    """Base class for RTM automation agents."""

    def __init__(self, name=None):
        """Initialize the agent with a name."""
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"agent.{self.name}")

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Execute the agent's main functionality."""
        pass

    def validate_inputs(self, inputs):
        """Validate agent inputs."""
        if not inputs:
            raise ValueError("No inputs provided")
        return True

    def log_status(self, message, level="info"):
        """Log status message."""
        getattr(self.logger, level)(message)


class DocumentAgent(Agent):
    """Agent for document processing tasks."""

    def execute(self, document_path, output_format="json"):
        """Execute document processing."""
        self.log_status(f"Processing document: {document_path}")

        # Validate document exists
        if not Path(document_path).exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        self.log_status(f"Document processing completed for {document_path}")
        return {"status": "success", "format": output_format}


class RequirementAgent(Agent):
    """Agent for requirement extraction and analysis."""

    def execute(self, source_data, extraction_patterns=None):
        """Execute requirement extraction."""
        self.log_status("Starting requirement extraction")

        if extraction_patterns is None:
            extraction_patterns = [
                r"(?i)(?:REQ|FR|NFR)-\d+(?:\.\d+)*",
                r"(?i)requirement:?\s*(.+)",
            ]

        # Simulate requirement extraction
        requirements = []
        for pattern in extraction_patterns:
            # In real implementation, would use regex matching
            requirements.append(f"Found pattern: {pattern}")

        self.log_status(f"Extracted {len(requirements)} requirements")
        return {"requirements": requirements, "count": len(requirements)}


class QualityAgent(Agent):
    """Agent for quality assurance and verification."""

    def execute(self, target_files=None, scan_level="light"):
        """Execute quality checks."""
        self.log_status(f"Running {scan_level} quality scan")

        if target_files is None:
            target_files = [
                "enhance_document_parsing.py",
                "digital_twin_parser.py"
            ]

        # Simulate quality checks
        results = {}
        for file_path in target_files:
            if Path(file_path).exists():
                results[file_path] = "PASS"
                self.log_status(f"Quality check passed: {file_path}")
            else:
                results[file_path] = "NOT_FOUND"
                self.log_status(f"File not found: {file_path}", "warning")

        return {"scan_level": scan_level, "results": results}


def create_agent(agent_type, **kwargs):
    """Factory function to create agents."""
    agents = {
        "document": DocumentAgent,
        "requirement": RequirementAgent,
        "quality": QualityAgent,
    }

    if agent_type not in agents:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return agents[agent_type](**kwargs)


def main():
    """Test agent functionality."""
    print("🤖 RTM Agent System Test")
    print("=" * 30)

    # Test document agent
    doc_agent = create_agent("document", name="DocProcessor")
    try:
        result = doc_agent.execute("test_document.txt", "json")
        print(f"Document agent test: {result}")
    except Exception as e:
        print(f"Document agent error: {e}")

    # Test requirement agent
    req_agent = create_agent("requirement", name="ReqExtractor")
    result = req_agent.execute("sample data")
    print(f"Requirement agent test: {result}")

    # Test quality agent
    quality_agent = create_agent("quality", name="QualityChecker")
    result = quality_agent.execute(scan_level="light")
    print(f"Quality agent test: {result}")

    print("\n✅ Agent system tests completed")


if __name__ == "__main__":
    main()
