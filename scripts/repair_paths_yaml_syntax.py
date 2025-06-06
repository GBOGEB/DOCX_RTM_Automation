"""
Script to automatically fix the YAML syntax issue in config/paths.yaml.fixed,
specifically targeting the broken secrets.openai_key_path.
No user input is required.
"""

import os


def repair_yaml_syntax():
    """
    Automatically fix the YAML syntax issue in config/paths.yaml.fixed.
    """
    file_path = os.path.join("config", "paths.yaml.fixed")
    print(f"Attempting to automatically repair YAML syntax in: {file_path}")

    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}. Cannot proceed.")
        return False

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

    original_content = content

    correct_path_value = "C:/Users/gbonthuy/OneDrive - Studiecentrum voor Kernenergie/Documents/GPT_Automation/openai_key.txt"
    # Ensure the corrected block ends with a newline to separate it from the next block
    correct_secrets_block_text = (
        f"secrets:\n  openai_key_path: '{correct_path_value}'\n"
    )

    # Pattern for the specific broken structure
    broken_pattern_specific = r"secrets:\s*\n\s*openai_key_path:\s*'C:/Users/gbonthuy/OneDrive - Studiecentrum voor Kernenergie/Documents/'\s*\n\s*GPT_Automation/openai_key\.txt\s*\n\s*\n\s*''"

    # General pattern for any 'secrets:' block to replace.
    # This
