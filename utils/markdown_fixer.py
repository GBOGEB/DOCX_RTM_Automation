import re
import os

def fix_markdown_headers(file_path):
    """
    Fixes markdown headers in a file by ensuring there is a space after the '#' characters.

    Args:
        file_path (str): Path to the markdown file to be fixed.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        fixed_lines = []
        for line in lines:
            fixed_line = re.sub(r'^(#+)([^\s#])', r'\1 \2', line)
            fixed_lines.append(fixed_line)

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(fixed_lines)

        print(f"Markdown headers fixed in file: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage:
    # To use this script directly, uncomment the following lines:
    # file_to_fix_input = input("Enter the path to the markdown file: ").strip()
    # if os.path.isfile(file_to_fix_input):
    #     fix_markdown_headers(file_to_fix_input)
    # else:
    #     print(f"File not found: {file_to_fix_input")

    # Test Markdown Fixer
    print("Running test for fix_markdown_headers...")
    dummy_md_filename = "test_markdown_fixer_temp_file.md"
    original_content = "##Header1\n#Header2\n###NoSpace\nText\n#### Valid Header\n"
    expected_fixed_content = "## Header1\n# Header2\n### NoSpace\nText\n#### Valid Header\n"

    with open(dummy_md_filename, "w", encoding="utf-8") as f:
        f.write(original_content)

    fix_markdown_headers(dummy_md_filename)

    with open(dummy_md_filename, "r", encoding="utf-8") as f:
        fixed_content = f.read()

    if fixed_content == expected_fixed_content:
        print(f"✓ Test passed: Markdown headers in '{dummy_md_filename}' fixed correctly.")
    else:
        print(f"✗ Test failed: Markdown headers in '{dummy_md_filename}' not fixed as expected.")
        print("Expected:")
        print(expected_fixed_content)
        print("Got:")
        print(fixed_content)

    if os.path.exists(dummy_md_filename):
        os.remove(dummy_md_filename)
    print("Test finished.")