import os


def load_github_api_key():
    # Get the API key from an environment variable
    api_key = os.getenv("GITHUB_API_KEY")
    if not api_key:
        raise ValueError("GITHUB_API_KEY is not set in the environment")
    return api_key


def main():
    try:
        load_github_api_key()
        # Use the API key for your GitHub interactions
        print("GitHub API key loaded successfully.")
        # TODO: Add code here to call GitHub APIs
    except ValueError as error:
        print(error)


if __name__ == "__main__":
    main()
