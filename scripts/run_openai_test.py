import os
import sys

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now you can import from config
from config.openai_integration import initialize_openai, test_openai_connection

if __name__ == "__main__":
    client = initialize_openai()
    if client:
        success, message = test_openai_connection(client)
        print(f"Connection test: {'Success' if success else 'Failed'}")
        print(f"Response: {message}")
