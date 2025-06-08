import sys
import os
import re
import yaml  # Ensure PyYAML is installed: pip install pyyaml


def pre_fix_secrets_block(file_content):
    """
    Attempts to fix/ensure the 'secrets.openai_key_path' block is correctly formatted.
    Returns the potentially fixed content and a boolean indicating if a change was made.
    """
    print("  Attempting pre-fix for 'secrets.openai_key_path' block...")

    correct_path_value = "C:/Users/gbonthuy/OneDrive - Studiecentrum voor Kernenergie/Documents/GPT_Automation/openai_key.txt"
    # Correct block, ends with a newline to ensure separation
    correct_secrets_block_text_with_newline = (
        f"secrets:\n  openai_key_path: '{correct_path_value}'\n"
    )

    # Normalize line endings for consistent processing
    content_normalized = file_content.replace("\r\n", "\n")

    # Regex to find the 'secrets:' block from its start to the start of the next top-level key or EOF
    # A top-level key starts at the beginning of a line (no indentation) and is followed by a colon.
    secrets_block_regex = r"^(secrets:[\s\S]*?)(?=\n^\S[^:\s][^:]*:|\Z)"
    # Explanation of lookahead:
    # \n^\S          : newline, then start of line, then non-whitespace
    # [^:\s][^:]*   : a character that is not a colon or whitespace, followed by zero or more non-colon characters
    # :              : a colon
    # This aims to correctly identify the start of the next distinct top-level key.
    # |\Z            : or end of string

    match = re.search(secrets_block_regex, content_normalized, re.MULTILINE)

    fixed_content = content_normalized
    made_change = False

    if match:
        print("    'secrets:' block found. Checking/replacing...")
        current_block_text = match.group(1)
        # Check if current block is already correct
        try:
            current_yaml = yaml.safe_load(current_block_text)
            if (
                isinstance(current_yaml, dict)
                and current_yaml.get("secrets", {}).get("openai_key_path")
                == correct_path_value
            ):
                print(
                    "    'secrets.openai_key_path' is already correct. No change to this block."
                )
            else:
                raise yaml.YAMLError("Needs replacement")  # Force replacement
        except yaml.YAMLError:
            print("    Replacing existing 'secrets:' block with correct version.")
            pre_block = content_normalized[: match.start()]
            post_block = content_normalized[
                match.end() :
            ]  # Content after the matched secrets block

            # Ensure the new block is properly separated
            # correct_secrets_block_text_with_newline already ends with \n
            fixed_content = (
                pre_block
                + correct_secrets_block_text_with_newline
                + post_block.lstrip("\r\n")
            )
            # lstrip on post_block to prevent double newlines if it already started with one
            # that was part of the lookahead's newline.
            made_change = True
    else:
        print("    'secrets:' block not found. Appending a correct 'secrets' block.")
        # Append, ensuring it's on a new line if original content exists and doesn't end with newline
        if content_normalized.strip() and not content_normalized.endswith("\n"):
            fixed_content = (
                content_normalized + "\n" + correct_secrets_block_text_with_newline
            )
        elif not content_normalized.strip():  # File is empty or only whitespace
            fixed_content = correct_secrets_block_text_with_newline
        else:  # File ends with a newline
            fixed_content = content_normalized + correct_secrets_block_text_with_newline
        made_change = True

    if made_change:
        # Final check: if fixed_content is just the secrets block, ensure it ends with one newline.
        # If it has content before/after, the logic above should handle newlines.
        if fixed_content.strip() == correct_secrets_block_text_with_newline.strip():
            fixed_content = (
                correct_secrets_block_text_with_newline.rstrip() + "\n"
            )  # Ensure single trailing newline

        print("    Pre-fix applied, content modified.")
    else:
        print("    No pre-fix applied or content effectively unchanged by pre-fix.")

    # Return the content with original line endings if no change was made,
    # or the fixed content (which will have LF endings, to be handled by writer)
    return fixed_content if made_change else file_content, made_change


def resolve_paths(yaml_file, base_dir):
    """
    Resolves relative paths in a YAML file to absolute paths.
    Includes a pre-fix step for known structural issues.
    """
    if not os.path.exists(yaml_file):
        print(f"Error: YAML file not found at '{yaml_file}'")
        return
    if not os.path.isdir(base_dir):
        print(f"Error: Base directory not found at '{base_dir}'")
        return

    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            original_content = f.read()
    except IOError as e:
        print(f"Error reading YAML file '{yaml_file}': {e}")
        return

    content_to_parse, pre_fix_made_change = pre_fix_secrets_block(original_content)

    try:
        if not content_to_parse.strip():
            print(
                f"Warning: Content of '{yaml_file}' became empty after pre-fix. No paths to resolve."
            )
            if pre_fix_made_change:
                try:
                    with open(yaml_file, "w", encoding="utf-8", newline="\n") as f:
                        f.write(content_to_parse)
                    print(
                        f"Wrote empty/whitespace content back to '{yaml_file}' after pre-fix."
                    )
                except IOError as e:
                    print(
                        f"Error writing empty/whitespace content to '{yaml_file}': {e}"
                    )
            return

        data = yaml.safe_load(content_to_parse)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file '{yaml_file}' even after pre-fix attempt: {e}")
        print(
            "Please check the YAML syntax, especially around the line numbers indicated in the error."
        )
        return

    if data is None:
        print(
            f"Warning: YAML file '{yaml_file}' parsed to None (empty or comments only) after pre-fix. No paths to resolve."
        )
        if pre_fix_made_change:
            try:
                with open(yaml_file, "w", encoding="utf-8", newline="\n") as f:
                    f.write(content_to_parse)
                print(
                    f"Wrote pre-fixed (but effectively empty for data) content back to '{yaml_file}'."
                )
            except IOError as e:
                print(f"Error writing pre-fixed content to '{yaml_file}': {e}")
        return

    def fix_path_value(path_str, current_base_dir):
        if isinstance(path_str, str) and (
            os.sep in path_str
            or ("/" in path_str and os.altsep == "/")
            or any(
                path_str.lower().endswith(ext)
                for ext in [
                    ".txt",
                    ".yaml",
                    ".yml",
                    ".json",
                    ".md",
                    ".docx",
                    ".pdf",
                    ".csv",
                    ".log",
                    ".template",
                ]
            )
        ):
            if path_str.startswith(
                ("http://", "https://", "<", "ENV_")
            ) or os.path.isabs(path_str):
                return path_str

            if re.match(r"^\$\{.*\}$", path_str) or re.match(r"^%.*%$", path_str):
                print(f"  Skipping environment variable placeholder: '{path_str}'")
                return path_str

            abs_path = os.path.abspath(os.path.join(current_base_dir, path_str))
            print(f"  Resolving relative path: '{path_str}' -> '{abs_path}'")
            return abs_path
        return path_str

    def recursive_fix_paths(item, current_base_dir):
        if isinstance(item, dict):
            for key, value in item.items():
                item[key] = recursive_fix_paths(value, current_base_dir)
        elif isinstance(item, list):
            for i, value in enumerate(item):
                item[i] = recursive_fix_paths(value, current_base_dir)
        elif isinstance(item, str):
            return fix_path_value(item, current_base_dir)
        return item

    print(
        f"Resolving paths in '{yaml_file}' relative to base directory '{base_dir}'..."
    )
    updated_data = recursive_fix_paths(data, base_dir)

    yaml.safe_dump(updated_data, default_flow_style=False, sort_keys=False)

    original_content.replace("\r\n", "\n")
    content_to_parse.replace("\r\n", "\n")

    path_resolution_made_change = False
    if data is not None:
        initial_data_yaml_string = yaml.safe_dump(
            data, default_flow_style=False, sort_keys=False
        )
        resolved_yaml_string = yaml.safe_dump(
            updated_data, default_flow_style=False, sort_keys=False
        )
        path_resolution_made_change = (
            resolved_yaml_string.strip() != initial_data_yaml_string.strip()
        )

    if pre_fix_made_change or path_resolution_made_change:
        try:
            with open(yaml_file, "w", encoding="utf-8", newline="\n") as f:
                if data is not None:
                    yaml.safe_dump(
                        updated_data, f, default_flow_style=False, sort_keys=False
                    )
                else:
                    f.write(content_to_parse)  # Write the raw string if data was None
            print(
                f"File '{yaml_file}' updated (pre-fix applied: {pre_fix_made_change}, path resolution change: {path_resolution_made_change})."
            )
        except IOError as e:
            print(f"Error writing updated YAML file '{yaml_file}': {e}")
        except yaml.YAMLError as e:
            print(f"Error dumping YAML to file '{yaml_file}': {e}")
    else:
        print(
            f"No effective changes made to '{yaml_file}' by pre-fixing or path resolution."
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_paths_yaml.py <path_to_yaml_file> [base_directory]")
        print(
            "If base_directory is not provided, the directory of the YAML file will be used."
        )
        sys.exit(1)

    yaml_file_path = sys.argv[1]

    if len(sys.argv) == 3:
        base_directory = sys.argv[2]
    else:
        base_directory = os.path.dirname(os.path.abspath(yaml_file_path))
        if not base_directory:
            base_directory = "."
        print(
            f"No base directory provided, using directory of YAML file (or CWD if YAML is in CWD): '{os.path.abspath(base_directory)}'"
        )

    resolve_paths(yaml_file_path, base_directory)
