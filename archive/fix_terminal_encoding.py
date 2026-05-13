#!/usr/bin/env python3
"""
Fix Terminal Encoding - Address Unicode display issues in different terminals
"""

import sys
import os
import locale
from pathlib import Path

def check_terminal_encoding():
    """Check and report terminal encoding capabilities."""
    print("TERMINAL ENCODING DIAGNOSTICS")
    print("=" * 35)
    print()

    # Check system encoding
    print(f"System encoding: {sys.getdefaultencoding()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    print(f"Locale: {locale.getdefaultlocale()}")
    print(f"Preferred encoding: {locale.getpreferredencoding()}")
    print()

    # Check if we're in different terminal types
    terminal_type = "Unknown"
    if "MINGW" in os.environ.get("MSYSTEM", ""):
        terminal_type = "Git Bash (MINGW)"
    elif "cmd.exe" in os.environ.get("COMSPEC", "").lower():
        terminal_type = "Windows Command Prompt"
    elif "powershell" in os.environ.get("PSModulePath", "").lower():
        terminal_type = "PowerShell"

    print(f"Terminal type: {terminal_type}")
    print()

    # Test Unicode support
    print("UNICODE SUPPORT TEST:")
    print("-" * 25)

    test_chars = [
        ("Basic ASCII", "Hello World"),
        ("Checkmark", "✓ Success"),
        ("Cross", "✗ Failed"),
        ("Arrow", "→ Next"),
        ("Bullet", "• Item"),
        ("Warning", "⚠ Warning"),
        ("Rocket", "🚀 Launch"),
        ("File", "📄 Document"),
        ("Folder", "📁 Directory"),
    ]

    for name, test_string in test_chars:
        try:
            print(f"{name:12}: {test_string}")
        except UnicodeEncodeError:
            print(f"{name:12}: [ENCODING ERROR]")

    print()

def create_clean_output_functions():
    """Create clean output functions for different environments."""
    print("CREATING CLEAN OUTPUT FUNCTIONS")
    print("=" * 35)
    print()

    # Simple text-only versions
    clean_output_code = '''
def clean_print_header(title, width=40):
    """Print a clean header without Unicode."""
    print("=" * width)
    print(title.center(width))
    print("=" * width)

def clean_print_success(message):
    """Print success message without emojis."""
    print(f"[SUCCESS] {message}")

def clean_print_error(message):
    """Print error message without emojis."""
    print(f"[ERROR] {message}")

def clean_print_info(message):
    """Print info message without emojis."""
    print(f"[INFO] {message}")

def clean_print_warning(message):
    """Print warning message without emojis."""
    print(f"[WARNING] {message}")

def clean_print_file(filepath, description=""):
    """Print file information without emojis."""
    if description:
        print(f"[FILE] {filepath} - {description}")
    else:
        print(f"[FILE] {filepath}")

def clean_print_directory(dirpath, description=""):
    """Print directory information without emojis."""
    if description:
        print(f"[DIR] {dirpath} - {description}")
    else:
        print(f"[DIR] {dirpath}")
'''

    # Write to a utilities file
    utils_path = Path("terminal_utils.py")
    with open(utils_path, 'w', encoding='utf-8') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('"""\nClean Terminal Output Utilities\n"""\n\n')
        f.write(clean_output_code)

    print(f"Created clean output utilities: {utils_path}")
    print()

def suggest_terminal_fixes():
    """Suggest fixes for terminal encoding issues."""
    print("TERMINAL ENCODING FIX SUGGESTIONS")
    print("=" * 40)
    print()

    print("For Git Bash (MINGW):")
    print("  1. Use: export LANG=en_US.UTF-8")
    print("  2. Or run: chcp 65001 (in cmd before starting bash)")
    print("  3. Consider using Windows Terminal instead")
    print()

    print("For Windows Command Prompt:")
    print("  1. Run: chcp 65001")
    print("  2. Use a better terminal like Windows Terminal")
    print("  3. Set font to 'Consolas' or 'Cascadia Code'")
    print()

    print("For PowerShell:")
    print("  1. Run: [Console]::OutputEncoding = [System.Text.Encoding]::UTF8")
    print("  2. Use Windows Terminal with PowerShell")
    print()

    print("Best Solution:")
    print("  * Install Windows Terminal from Microsoft Store")
    print("  * Use PowerShell or Command Prompt within Windows Terminal")
    print("  * Set encoding to UTF-8 in terminal settings")
    print()

def test_clean_pipeline():
    """Test the pipeline with clean output."""
    print("TESTING CLEAN PIPELINE OUTPUT")
    print("=" * 35)
    print()

    # Import our clean functions
    try:
        from terminal_utils import clean_print_header, clean_print_success, clean_print_file

        clean_print_header("RTM Pipeline Test")
        clean_print_success("Pipeline completed successfully")
        clean_print_file("output/sample_document.docx", "Processed document")

        print()
        print("Clean output functions are working!")

    except ImportError:
        print("Clean utilities not found. Run this script first to create them.")

def main():
    """Main function."""
    check_terminal_encoding()
    create_clean_output_functions()
    suggest_terminal_fixes()
    test_clean_pipeline()

    print("=" * 50)
    print("ENCODING FIX COMPLETE")
    print()
    print("RECOMMENDATIONS:")
    print("1. Use the clean batch file: run_pipeline_clean.bat")
    print("2. Consider switching to Windows Terminal")
    print("3. Set your terminal to UTF-8 encoding")
    print("4. Use the clean utility functions in Python scripts")

if __name__ == "__main__":
    main()
