#!/usr/bin/env python3
"""
Stub for OpenAI service interactions.

This module provides a stub implementation of the OpenAI service,
allowing for testing and development without actual API calls.
"""

import sys
from pathlib import Path
import time
import random
from typing import Optional, List, Dict, Any

# --- Start of standard boilerplate for running files in packages directly ---
_current_file_path_stub = Path(__file__).resolve()
# Assuming 'agents' is the package directory containing this file
_package_dir_stub = _current_file_path_stub.parent
# Assuming the parent of 'agents' is the project root
_project_root_dir_stub = _package_dir_stub.parent

if __name__ == "__main__" and not __package__:
    # If run as a script, set __package__ to the name of the directory
    # this file is in (e.g., 'agents'). This helps resolve relative imports
    # within this package if this script were to use them.
    __package__ = _package_dir_stub.name

if str(_project_root_dir_stub) not in sys.path:
    # Add the project root to sys.path. This allows absolute imports
    # from other packages in the project (e.g., 'from utils import ...').
    sys.path.insert(0, str(_project_root_dir_stub))
# --- End of standard boilerplate ---

import logging

# Configuration for the stub
STUB_CONFIG = {
    "default_model": "gpt-3.5-turbo",
    "response_delay": 0.5,  # Simulated delay in seconds
    "random_seed": 42,
}

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Stub implementation of OpenAIService that provides a compatible interface
    but does not perform actual API calls to OpenAI.
    """

    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        random.seed(STUB_CONFIG["random_seed"])
        logger.info("OpenAIService stub initialized with model: %s", model)

    def generate_text(self, prompt, _max_tokens=100):
        """
        Stub implementation of text generation.

        Args:
            prompt: The text prompt to generate from
            _max_tokens: Maximum number of tokens to generate

        Returns:
            A stub response
        """
        logger.info(
            "Stub generate_text called with prompt: %s...",
            prompt[:30] if prompt else "",
        )
        time.sleep(STUB_CONFIG["response_delay"])  # Simulate delay
        return f"Stub response for prompt: {prompt[:20]}..."

    def analyze_text(self, text, analysis_type="general"):
        """
        Stub implementation of text analysis.

        Args:
            text: The text to analyze
            analysis_type: The type of analysis to perform

        Returns:
            A stub analysis result
        """
        logger.info("Stub analyze_text called for analysis type: %s", analysis_type)
        time.sleep(STUB_CONFIG["response_delay"])  # Simulate delay
        return {
            "analysis_type": analysis_type,
            "summary": "This is a stub analysis result",
            "sentiment": random.choice(["positive", "neutral", "negative"]),
        }

    def is_available(self):
        """
        Check if the OpenAI service is available.

        Returns:
            Always False for the stub implementation
        """
        return False

    def get_completion(
        self, prompt: str, model: str = "text-davinci-003", _max_tokens: int = 150
    ) -> Optional[str]:  # W0613
        """
        Simulate getting a completion from OpenAI.
        """
        logger.info("Stub get_completion called with model: %s", model)
        time.sleep(STUB_CONFIG["response_delay"])  # Simulate delay
        return f"Stub completion for prompt: {prompt[:20]}..."

    def get_embedding(
        self, text: str, model: str = "text-embedding-ada-002"
    ) -> List[float]:  # pylint: disable=unused-argument
        """
        Get embeddings for a given text. (Stub implementation)

        Args:
            text: The text to get embeddings for (unused in stub)
            model: The model to use for generating embeddings (unused in stub)

        Returns:
            A list of floats representing the embedding vector
        """
        # For the stub implementation, return a fixed vector
        return [0.1] * 1536  # 1536 is typical embedding dimension for OpenAI models

    def analyze_sentiment(
        self, text: str, model: str = None
    ) -> Dict[str, Any]:  # pylint: disable=unused-argument
        """
        Analyze sentiment of a text. (Stub implementation)

        Args:
            text: The text to analyze (unused in stub)
            model: Optional model to use (unused in stub)

        Returns:
            A dictionary with sentiment analysis results
        """
        # For the stub implementation, return fixed sentiment
        return {"positive": 0.6, "negative": 0.2, "neutral": 0.2, "overall": "positive"}
