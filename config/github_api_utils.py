import os


def load_github_api_key():
    # Get the API key from an environment variable
    api_key = os.getenv("GITHUB_API_KEY")
    if not api_key:
        raise ValueError("GITHUB_API_KEY environment variable is not set.")
