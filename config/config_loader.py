import os
import yaml

def load_config(config_file):
    """Load configuration from a yaml file"""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    return None

def get_project_paths():
    """Load paths configuration from paths.yaml"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths_file = os.path.join(base_dir, 'config', 'paths.yaml')

    if os.path.exists(paths_file):
        return load_config(paths_file)

    # Return default paths if no file exists
    return {
        'input_dir': os.path.join(base_dir, 'input'),
        'output_dir': os.path.join(base_dir, 'output'),
        'config_dir': os.path.join(base_dir, 'config')
    }

def get_api_keys():
    """Load API keys from apikeys.yaml"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api_keys_file = os.path.join(base_dir, 'config', 'apikeys.yaml')

    if os.path.exists(api_keys_file):
        return load_config(api_keys_file)
    return {}

# When run directly, print the loaded configs for testing
if __name__ == "__main__":
    paths = get_project_paths()
    print("Project paths:")
    for key, value in paths.items():
        if isinstance(value, dict):
            print(f"  {key}: [complex object]")
        else:
            print(f"  {key}: {value}")

    keys = get_api_keys()
    print("\nAPI Keys (masked):")
    for key in keys:
        if keys[key]:
            masked = keys[key][:4] + "****" if len(keys[key]) > 8 else "****"
            print(f"  {key}: {masked}")
