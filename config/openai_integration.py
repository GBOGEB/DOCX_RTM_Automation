import openai
import os

# Change from absolute import to relative import
from .config_loader import get_api_keys, get_project_paths


# Make this module importable by others
def initialize_openai():
    """Initialize the OpenAI client and return it for use in other modules."""
    print("Initializing OpenAI integration...")

    api_key_val = None
    source_of_key = "unknown"

    # 1. Try environment variable
    api_key_env = os.getenv("OPENAI_API_KEY")
    if api_key_env:
        api_key_val = api_key_env.strip()
        source_of_key = "environment variable OPENAI_API_KEY"

    # 2. Try paths.yaml (via config_loader)
    if not api_key_val:
        project_paths = get_project_paths()
        if (
            project_paths
            and "secrets" in project_paths
            and "openai_key_path" in project_paths["secrets"]
        ):
            openai_key_path_from_config = project_paths["secrets"]["openai_key_path"]
            if openai_key_path_from_config and os.path.exists(
                openai_key_path_from_config
            ):
                try:
                    with open(openai_key_path_from_config, "r", encoding="utf-8") as f:
                        key_from_file = f.read().strip()
                    if key_from_file:
                        api_key_val = key_from_file
                        source_of_key = f"file specified in paths.yaml: {openai_key_path_from_config}"
                except Exception as e:
                    print(
                        f"Error reading API key from file {openai_key_path_from_config}: {e}"
                    )

    # 3. Try apikeys.yaml (via config_loader)
    if not api_key_val:
        api_keys_from_yaml = get_api_keys()
        if api_keys_from_yaml and "openai" in api_keys_from_yaml:
            key_from_apikeys = (
                str(api_keys_from_yaml["openai"]).strip()
                if api_keys_from_yaml["openai"] is not None
                else None
            )
            if key_from_apikeys:
                api_key_val = key_from_apikeys
                source_of_key = "config/apikeys.yaml"

    if api_key_val:
        try:
            # For openai SDK v1.0.0+
            # Explicitly pass api_key to constructor
            client = openai.OpenAI(api_key=api_key_val)
            print(f"OpenAI client (v1.x+) initialized using key from {source_of_key}.")
            return client
        except AttributeError:  # openai.OpenAI does not exist (older SDK)
            openai.api_key = api_key_val  # Set for old SDK
            print(
                f"OpenAI API key set for older SDK (pre v1.x) using key from {source_of_key}."
            )
            return openai  # Return the module itself
        except openai.AuthenticationError as e:
            print(
                f"OpenAI AuthenticationError during client initialization with key from {source_of_key}: {e}"
            )
            return None
        except Exception as e:
            print(
                f"Failed to initialize OpenAI client (v1.x+) with key from {source_of_key}: {e}"
            )
            # Fallback: if new client fails for other reasons, try to set for old SDK if not already done
            if not hasattr(
                openai, "OpenAI"
            ):  # Check again if it was an AttributeError path
                openai.api_key = api_key_val
                print(
                    f"OpenAI API key set for older SDK (pre v1.x) as fallback, using key from {source_of_key}."
                )
                return openai
            return None
    else:
        print(
            "OpenAI API key not found. Please set OPENAI_API_KEY environment variable, or configure paths.yaml or apikeys.yaml."
        )
        return None


def check_openai_availability(client):
    """
    Checks if the OpenAI API is available and authenticated.
    Makes a lightweight call to the API.

    Args:
        client: The initialized OpenAI client (instance for v1.x+, module for older).

    Returns:
        A tuple (bool, str): (True if available, "Success message") or (False if not, "Error message").
    """
    if not client:
        print("OpenAI client/module not provided for availability check.")
        return False, "Client not initialized or provided."

    try:
        if hasattr(client, "models") and callable(
            getattr(client.models, "list", None)
        ):  # New SDK client instance
            client.models.list(limit=1)
            status_message = "OpenAI API is available and authenticated (v1.x+ client)."
        elif (
            hasattr(client, "Model")
            and callable(getattr(client.Model, "list", None))
            and getattr(client, "api_key", None)
        ):  # Old SDK module with api_key set
            client.Model.list(limit=1)  # Old SDK style call
            status_message = (
                "OpenAI API is available and authenticated (older SDK module)."
            )
        else:
            return (
                False,
                "OpenAI client/module is not in a recognized state for health check or API key not set.",
            )

        print(status_message)
        return True, status_message
    except openai.APIConnectionError as e:
        error_msg = f"OpenAI API connection error: {e}"
        print(error_msg)
        return False, error_msg
    except openai.AuthenticationError as e:
        error_msg = f"OpenAI API authentication error: {e}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error checking OpenAI availability: {e}"
        print(error_msg)
        return False, error_msg


def create_agent(system_prompt: str, client, model: str = "gpt-3.5-turbo"):
    """
    Creates a simple agent function that interacts with the OpenAI API.

    Args:
        system_prompt (str): The system prompt to define the agent's behavior.
        client: The initialized OpenAI client (or the openai module if using older versions).
        model (str): The model to use for the chat completion.

    Returns:
        A function that takes a user_prompt (str) and returns a tuple (content_str, metadata_dict).
    """
    if not client:
        print("OpenAI client not initialized. Cannot create agent.")

        # Return a dummy function that indicates an error
        def error_agent(user_prompt: str) -> tuple[str, dict]:
            return "Error: OpenAI client not initialized.", {
                "error": "Client not initialized"
            }

        return error_agent

    def agent_function(user_prompt: str) -> tuple[str, dict]:
        """
        The actual agent function that sends a prompt to OpenAI and gets a response.
        """
        try:
            # Check for new OpenAI SDK client instance (v1.x+)
            if (
                hasattr(client, "chat")
                and hasattr(client.chat, "completions")
                and callable(client.chat.completions.create)
            ):
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                content = response.choices[0].message.content
                usage = response.usage
                metadata = {
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens,
                    }
                }
            # Check for old OpenAI SDK module (pre v1.x)
            elif hasattr(client, "ChatCompletion") and callable(
                client.ChatCompletion.create
            ):
                response = client.ChatCompletion.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                content = response.choices[0].message.content
                # Usage data structure might differ for older SDK versions
                usage_data = response.get("usage", {})
                metadata = {
                    "usage": {
                        "prompt_tokens": usage_data.get("prompt_tokens"),
                        "completion_tokens": usage_data.get("completion_tokens"),
                        "total_tokens": usage_data.get("total_tokens"),
                    }
                }
            else:
                error_msg = "Error: OpenAI client interaction method not determined. Unsupported client object."
                print(error_msg)
                return error_msg, {"error": "Unsupported OpenAI client interaction"}

            return content, metadata
        except openai.APIConnectionError as e:
            error_message = f"OpenAI API Connection Error: {e}"
            print(error_message)
            return f"Error: Could not connect to OpenAI. Details: {str(e)}", {
                "error": str(e),
                "type": "APIConnectionError",
            }
        except openai.AuthenticationError as e:
            error_message = f"OpenAI API Authentication Error: {e}"
            print(error_message)
            return f"Error: Authentication failed. Details: {str(e)}", {
                "error": str(e),
                "type": "AuthenticationError",
            }
        except openai.RateLimitError as e:
            error_message = f"OpenAI API Rate Limit Error: {e}"
            print(error_message)
            return f"Error: Rate limit exceeded. Details: {str(e)}", {
                "error": str(e),
                "type": "RateLimitError",
            }
        except Exception as e:
            error_message = f"Error during OpenAI API call: {e}"
            print(error_message)
            return f"Error: Could not get response. Details: {str(e)}", {
                "error": str(e),
                "type": "APICallError",
            }

    return agent_function
