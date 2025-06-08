import json


def load_config(file_path):
    """
    Load configuration from a JSON file.

    :param file_path: Path to the configuration file.
    :return: Parsed configuration as a dictionary.
    """
    try:
        with open(file_path, "r") as file:
            config = json.load(file)
        return config
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {file_path}")
    return None


def analyze_config(config):
    """
    Analyze the configuration dictionary.

    :param config: Configuration dictionary.
    :return: Analysis results.
    """
    if not config:
        print("Error: No configuration provided for analysis.")
        return None

    # Example analysis: Count the number of keys in the config
    key_count = len(config)
    print(f"Configuration contains {key_count} keys.")
    return key_count


if __name__ == "__main__":
    config_file_path = "config.json"  # Replace with your actual config file path
    config_data = load_config(config_file_path)
    analyze_config(config_data)
