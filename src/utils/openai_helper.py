#!/usr/bin/env python3
"""
OpenAI API integration helper for enhancing RTM automation workflows.

This module provides functions for leveraging OpenAI's capabilities
to improve requirements analysis, test coverage analysis, and more.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

import sys

# Add project root to path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_MODEL = "gpt-4"
DEFAULT_TEMPERATURE = 0.3
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


class OpenAIHelper:
    """Helper class for OpenAI API integration."""

    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        """
        Initialize OpenAI helper.

        Args:
            api_key: OpenAI API key (if None, read from environment variable)
            model: OpenAI model to use
        """
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")

        if not self.api_key:
            # Try to read from config file
            config_path = self._find_config_file()
            if config_path:
                self.api_key = self._read_api_key_from_config(config_path)

        # Lazy import to avoid dependency if not used
        self._client = None

    def _find_config_file(self) -> Optional[Path]:
        """Find OpenAI configuration file."""
        # Look in standard locations
        possible_locations = [
            Path("config/openai_key.txt"),
            Path("config/openai.json"),
            Path.home() / ".openai" / "config.json",
            Path.home() / ".config" / "openai" / "api_key.txt",
        ]

        for location in possible_locations:
            if location.exists():
                return location

        return None

    def _read_api_key_from_config(self, config_path: Path) -> Optional[str]:
        """Read API key from configuration file."""
        try:
            if config_path.suffix.lower() == ".json":
                with open(config_path, "r") as f:
                    config = json.load(f)
                return config.get("api_key")
            else:
                with open(config_path, "r") as f:
                    return f.read().strip()
        except Exception as e:
            logger.error(f"Error reading API key from {config_path}: {e}")
            return None

    @property
    def client(self):
        """Get OpenAI client, initializing if necessary."""
        if self._client is None:
            try:
                import openai

                # Configure the client
                if not self.api_key:
                    raise ValueError(
                        "OpenAI API key not found. Please set OPENAI_API_KEY environment variable or provide in config file."
                    )

                openai.api_key = self.api_key
                self._client = openai.OpenAI(api_key=self.api_key)

            except ImportError:
                logger.error(
                    "OpenAI package not installed. Install with: pip install openai"
                )
                raise

        return self._client

    def analyze_requirement(
        self, requirement: str, additional_context: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze a requirement for quality and completeness.

        Args:
            requirement: Requirement text to analyze
            additional_context: Additional context for analysis

        Returns:
            Dictionary with analysis results
        """
        try:
            # Prepare the prompt
            prompt = f"""Analyze the following requirement for quality, completeness, and clarity:

Requirement: {requirement}

{additional_context}

Please provide a structured analysis with the following:
1. Clarity score (1-10): Is the requirement clear and unambiguous?
2. Testability score (1-10): Can this requirement be verified through testing?
3. Feasibility score (1-10): Is this requirement technically feasible?
4. Issues: Identify any issues such as ambiguity, incompleteness, or contradiction
5. Improvement suggestions: Specific recommendations to improve the requirement

Return your analysis as JSON with the following structure:
{{
  "clarity_score": <score>,
  "testability_score": <score>,
  "feasibility_score": <score>,
  "issues": ["issue 1", "issue 2", ...],
  "suggestions": ["suggestion 1", "suggestion 2", ...]
}}

Your analysis should focus on making the requirement more specific, measurable, achievable, relevant, and time-bound (SMART).
"""

            # Call OpenAI API
            response = self._call_api(prompt)

            # Parse response
            try:
                # Try to parse as JSON
                analysis = json.loads(response)
                return analysis

            except json.JSONDecodeError:
                # If not valid JSON, extract scores manually
                logger.warning(
                    "Response was not valid JSON, attempting to extract data manually"
                )

                # Fallback result
                analysis = {
                    "clarity_score": self._extract_score(response, "clarity"),
                    "testability_score": self._extract_score(response, "testability"),
                    "feasibility_score": self._extract_score(response, "feasibility"),
                    "issues": self._extract_list_items(response, "Issues"),
                    "suggestions": self._extract_list_items(
                        response, "Improvement suggestions"
                    ),
                    "raw_response": response,
                }

                return analysis

        except Exception as e:
            logger.error(f"Error analyzing requirement: {e}")
            return {"error": str(e), "requirement": requirement}

    def generate_test_cases(self, requirement: str, count: int = 3) -> Dict[str, Any]:
        """
        Generate test cases for a requirement.

        Args:
            requirement: Requirement to generate test cases for
            count: Number of test cases to generate

        Returns:
            Dictionary with generated test cases
        """
        try:
            # Prepare the prompt
            prompt = f"""Generate {count} test cases for the following requirement:

Requirement: {requirement}

Each test case should include:
1. Test ID (in format TC-XXX)
2. Test description
3. Preconditions
4. Steps to execute
5. Expected results
6. Pass/Fail criteria

Return your test cases as JSON with the following structure:
{{
  "test_cases": [
    {{
      "id": "TC-001",
      "description": "...",
      "preconditions": "...",
      "steps": ["step 1", "step 2", ...],
      "expected_results": "...",
      "pass_fail_criteria": "..."
    }},
    ...
  ]
}}
"""

            # Call OpenAI API
            response = self._call_api(prompt)

            # Parse response
            try:
                # Try to parse as JSON
                result = json.loads(response)
                return result

            except json.JSONDecodeError:
                # If not valid JSON, return structured data with raw response
                logger.warning("Response was not valid JSON")
                return {
                    "error": "Failed to parse response as JSON",
                    "raw_response": response,
                }

        except Exception as e:
            logger.error(f"Error generating test cases: {e}")
            return {"error": str(e), "requirement": requirement}

    def analyze_traceability(
        self, requirements: List[Dict[str, Any]], test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze traceability between requirements and test cases.

        Args:
            requirements: List of requirement dictionaries
            test_cases: List of test case dictionaries

        Returns:
            Dictionary with traceability analysis
        """
        try:
            # Prepare the prompt
            req_json = json.dumps(requirements, indent=2)
            tc_json = json.dumps(test_cases, indent=2)

            prompt = f"""Analyze the traceability between the following requirements and test cases:

Requirements:
{req_json}

Test Cases:
{tc_json}

Please provide a detailed analysis of:
1. Which requirements are covered by test cases
2. Which requirements lack test coverage
3. Suggestions for additional test cases to improve coverage

Return your analysis as JSON with the following structure:
{{
  "covered_requirements": ["REQ-001", ...],
  "uncovered_requirements": ["REQ-002", ...],
  "coverage_percentage": 85,
  "suggested_test_cases": [
    {{
      "for_requirement": "REQ-002",
      "test_description": "..."
    }},
    ...
  ]
}}
"""

            # Call OpenAI API with increased max_tokens
            response = self._call_api(prompt, max_tokens=2048)

            # Parse response
            try:
                # Try to parse as JSON
                analysis = json.loads(response)
                return analysis

            except json.JSONDecodeError:
                # If not valid JSON, return structured data with raw response
                logger.warning("Response was not valid JSON")
                return {
                    "error": "Failed to parse response as JSON",
                    "raw_response": response,
                }

        except Exception as e:
            logger.error(f"Error analyzing traceability: {e}")
            return {
                "error": str(e),
            }

    def _call_api(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = DEFAULT_TEMPERATURE,
    ) -> str:
        """Call OpenAI API with retry logic."""
        retries = 0

        while retries <= MAX_RETRIES:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant specializing in requirements engineering and software testing.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                # Extract the response text
                if hasattr(response, "choices") and len(response.choices) > 0:
                    return response.choices[0].message.content.strip()
                else:
                    raise ValueError("Unexpected response structure from OpenAI API")

            except Exception as e:
                retries += 1
                logger.warning(
                    f"API call failed (attempt {retries}/{MAX_RETRIES}): {e}"
                )

                if retries <= MAX_RETRIES:
                    # Exponential backoff
                    sleep_time = RETRY_DELAY * (2 ** (retries - 1))
                    logger.info(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    raise

        raise RuntimeError("All API call attempts failed")

    def _extract_score(self, text: str, score_type: str) -> int:
        """Extract score from text."""
        import re

        # Look for patterns like "Clarity score: 7" or "Clarity: 7/10"
        pattern = rf"{score_type}\s*(?:score)?(?:\s*:)?\s*(\d+)(?:/\d+)?"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return int(match.group(1))
        else:
            return 0

    def _extract_list_items(self, text: str, section_name: str) -> List[str]:
        """Extract list items from a section in text."""
        import re

        # Find the section
        section_pattern = rf"{section_name}:(.*?)(?:\n\n|\n[A-Z]|$)"
        section_match = re.search(section_pattern, text, re.IGNORECASE | re.DOTALL)

        if not section_match:
            return []

        section_text = section_match.group(1)

        # Extract list items (numbered or bullet points)
        items = []
        for line in section_text.strip().split("\n"):
            # Remove leading numbers, dashes, asterisks, etc.
            clean_line = re.sub(r"^\s*(?:\d+\.|\-|\*|\•)\s*", "", line).strip()
            if clean_line:
                items.append(clean_line)

        return items


def main():
    """Command-line interface for OpenAI helper."""
    import argparse

    parser = argparse.ArgumentParser(description="OpenAI integration tools")
    parser.add_argument(
        "--api-key", help="OpenAI API key (optional, can use environment variable)"
    )
    parser.add_argument("--analyze-requirement", help="Analyze a requirement")
    parser.add_argument(
        "--generate-tests", help="Generate test cases for a requirement"
    )
    parser.add_argument(
        "--count", type=int, default=3, help="Number of test cases to generate"
    )
    parser.add_argument("--model", help="OpenAI model to use", default=DEFAULT_MODEL)

    args = parser.parse_args()

    helper = OpenAIHelper(api_key=args.api_key, model=args.model)

    if args.analyze_requirement:
        result = helper.analyze_requirement(args.analyze_requirement)
        print(json.dumps(result, indent=2))

    elif args.generate_tests:
        result = helper.generate_test_cases(args.generate_tests, args.count)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
