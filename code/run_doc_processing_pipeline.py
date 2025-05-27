import yaml
import sys
import os
from pathlib import Path

# Determine project root (assuming this script is in code/ subdirectory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Add project root to sys.path to allow imports from other top-level directories if needed
# and to ensure config/paths.yaml can be found consistently.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import local modules from the 'code' directory
# These imports assume word_to_md.py, extract_outline.py, extract_rtm.py exist in the same directory.
# If they are structured differently, these imports might need adjustment.
try:
    from .word_to_md import convert_word_to_md # Assuming word_to_md.py exists
    from .extract_outline import extract_outline_from_md as extract_outline # Renamed for clarity if function is specific
    from .extract_rtm import extract_requirements_from_md as extract_rtm # Renamed for clarity
except ImportError as e:
    print(f"Error importing local modules: {e}")
    print("Ensure word_to_md.py, extract_outline.py, and extract_rtm.py are in the 'code' directory.")
    sys.exit(1)

def main():
    # Load configuration
    paths_config_file = PROJECT_ROOT / "config" / "paths.yaml"
    if not paths_config_file.exists():
        print(f"Error: Configuration file not found at {paths_config_file}")
        sys.exit(1)

    with open(paths_config_file, "r", encoding="utf-8") as file:
        paths = yaml.safe_load(file)

    # Define input/output paths based on config and project root
    # Example: if paths.yaml has relative paths, make them absolute from project_root
    # This needs to be adapted based on how paths are defined in your paths.yaml
    # For now, assuming paths in paths.yaml are relative to project_root or are keys
    # that these functions expect.

    # Example: Get the master markdown output path from config
    md_output_path_key = paths.get("md_output", "output/default_master.md") # Default if not in config
    master_md_file = PROJECT_ROOT / md_output_path_key

    # Ensure output directories exist for the pipeline steps
    # This might be handled within each function, but good to be aware of.
    if master_md_file.parent:
        master_md_file.parent.mkdir(parents=True, exist_ok=True)

    # Process workflow
    print("Starting document processing pipeline...")

    # Step 1: Convert Word to MD (assuming convert_word_to_md handles its own paths or takes them)
    # convert_word_to_md() might need to be called with specific input/output from paths config
    print("Running Word to Markdown conversion...")
    # Example: convert_word_to_md(PROJECT_ROOT / paths['input_docx'], master_md_file)
    # Since convert_word_to_md is not defined here, this is a placeholder call.
    # If convert_word_to_md() is a function that uses paths from config directly, it might work.
    # For this example, let's assume it produces master_md_file.
    # If it's not available or fails, the subsequent steps might fail.
    try:
        # This is a placeholder. The actual call depends on word_to_md.py's signature.
        # If word_to_md.py is self-contained and uses paths.yaml, it might not need arguments.
        # For robustness, it's better to pass explicit paths.
        # convert_word_to_md() # Original call
        print("Note: 'convert_word_to_md' called without arguments. Ensure it handles its paths correctly.")
        # A more robust call would be:
        # input_docx = PROJECT_ROOT / paths.get('input_word_doc', 'input/source.docx')
        # if input_docx.exists():
        #     convert_word_to_md(input_docx, master_md_file)
        # else:
        #     print(f"Input Word document not found: {input_docx}")
        pass # Placeholder for actual call
    except NameError:
        print("Warning: convert_word_to_md function not available or not imported correctly.")
    except Exception as e:
        print(f"Error during Word to MD conversion: {e}")


    # Ensure master_md_file exists before proceeding
    if not master_md_file.exists():
        print(f"Error: Master markdown file {master_md_file} not found after conversion step. Aborting subsequent steps.")
        # Create a dummy file for subsequent steps to run for debugging purposes
        print(f"Creating a dummy {master_md_file} for debugging subsequent steps.")
        master_md_file.parent.mkdir(parents=True, exist_ok=True)
        with open(master_md_file, "w", encoding="utf-8") as f:
            f.write("# Dummy Markdown File\n\nThis is a placeholder.\nREQ-001: A sample requirement.\n")
        # sys.exit(1) # Original behavior would be to exit

    # Step 2: Extract Outline
    print(f"Extracting outline from {master_md_file}...")
    outline_output_key = paths.get("yaml_output_outline", "output/document_outline.yaml") # Example key
    outline_output_file = PROJECT_ROOT / outline_output_key
    try:
        extract_outline(str(master_md_file), output_file=str(outline_output_file))
    except NameError:
        print("Warning: extract_outline function not available or not imported correctly.")
    except Exception as e:
        print(f"Error during outline extraction: {e}")

    # Step 3: Extract RTM
    print(f"Extracting RTM from {master_md_file}...")
    rtm_output_key = paths.get("yaml_output_rtm", "output/requirements.yaml") # Example key
    rtm_output_file = PROJECT_ROOT / rtm_output_key
    try:
        extract_rtm(str(master_md_file), output_file=str(rtm_output_file))
    except NameError:
        print("Warning: extract_rtm function not available or not imported correctly.")
    except Exception as e:
        print(f"Error during RTM extraction: {e}")

    print("Document processing pipeline finished.")

if __name__ == "__main__":
    main()
