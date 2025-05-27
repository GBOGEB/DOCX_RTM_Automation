import re
import sys

def check_line_length(lines, max_length=80):
    """Check if any line exceeds the maximum allowed length."""
    errors = []
    for i, line in enumerate(lines, start=1):
        if len(line) > max_length:
            errors.append(f"Line {i}: Exceeds {max_length} characters")
    return errors

def check_heading_format(lines):
    """Check if headings are properly formatted."""
    errors = []
    for i, line in enumerate(lines, start=1):
        if line.startswith("#"):
            if not re.match(r"^#{1,6} ", line):
                errors.append(f"Line {i}: Improper heading format")
    return errors

def lint_markdown(file_path):
    """Lint a Markdown file for common issues."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        errors = []
        errors.extend(check_line_length(lines))
        errors.extend(check_heading_format(lines))
        
        if errors:
            print("Markdown Linting Errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("No linting issues found!")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python markdown_lint.py <file_path>")
    else:
        lint_markdown(sys.argv[1])