#!/usr/bin/env python
import os
import json
import tempfile
import sys
import logging
import re
import subprocess
import unittest  # Add this import at the top
from pathlib import Path
import shutil
from datetime import datetime
from typing import Dict, List, Any, Union, Optional

"""
This script converts a master markdown file (converted from MASTER.docx)
into two outputs:
1. A JSON file outlining the nested heading structure.
2. A YAML file containing global configuration settings (paths, API keys,
    deliverables matrix data, etc.)

Usage:
  python WORD_round_trip_250520_1519.py --input MASTER.md

Make sure to install PyYAML: pip install pyyaml
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def ensure_package_installed(package_name: str) -> bool:
    """
    Checks if a package is installed, and installs it if missing.
    
    Args:
        package_name: Name of the package to check/install
        
    Returns:
        bool: True if the package is available (was installed or already present)
    """
    try:
        __import__(package_name)
        logger.debug(f"Package {package_name} is already installed")
        return True
    except ImportError:
        try:
            logger.info(f"Installing missing package: {package_name}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package_name}: {e}")
            return False

# Check for required packages
if not ensure_package_installed("yaml"):
    logger.error("PyYAML installation failed. Please install it manually using 'pip install pyyaml'.")
    sys.exit(1)
else:
    import yaml

# Check for pytest for testing
ensure_package_installed("pytest")

def validate_markdown(md_content: str) -> bool:
    """
    Validates that the markdown file has the expected structure.
    
    Args:
        md_content: The markdown content to validate
        
    Returns:
        bool: True if the content is valid, otherwise False
    """
    if not md_content or not md_content.strip():
        logger.warning("Empty markdown content")
        return False
        
    # Check for minimum requirements - at least one level 1 heading
    if not re.search(r'^#\s+', md_content, re.MULTILINE):
        logger.warning("No level 1 headings found in markdown")
        return False
        
    # Check for consistency in heading levels (no skipping levels)
    headings = re.findall(r'^(#{1,7})\s+', md_content, re.MULTILINE)
    prev_level = 0
    for h in headings:
        level = len(h)
        if level > prev_level + 1 and prev_level > 0:
            logger.warning(f"Skipped heading level. Found level {level} after level {prev_level}")
        prev_level = level
        
    return True

def parse_markdown(md_content: str) -> List[Dict[str, Any]]:
    """
    Parses markdown headings (levels 1 to 7) and builds
    a nested dictionary structure.
    
    Args:
        md_content: The markdown content to parse
        
    Returns:
        List[Dict]: A list of dictionaries representing the heading structure
    """
    if not md_content or not md_content.strip():
        return []
        
    outline = []
    heading_stack = []

    # Regular expression for markdown headings from level 1 to 7
    heading_re = re.compile(r'^(#{1,7})\s+(.*)$', re.MULTILINE)
    
    # Find all heading matches
    for match in heading_re.finditer(md_content):
        hashes, title = match.groups()
        level = len(hashes)
        node = {
            "title": title.strip(),
            "level": level,
            "children": []
        }

        # If stack is empty, add node at root.
        if not heading_stack:
            heading_stack.append(node)
            outline.append(node)
        else:
            # Pop from stack until correct parent is found
            while heading_stack and heading_stack[-1]["level"] >= level:
                heading_stack.pop()
            if heading_stack:
                heading_stack[-1]["children"].append(node)
            else:
                outline.append(node)
            heading_stack.append(node)
        
    return outline

def write_json(data: Any, outfile: Union[str, Path]) -> None:
    """
    Writes data to a JSON file with proper encoding.
    
    Args:
        data: The data to write to the file
        outfile: The output file path
    """
    outfile = Path(outfile) if not isinstance(outfile, Path) else outfile
    try:
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"JSON outline written to: {outfile}")
        logger.info(f"JSON outline written to: {outfile}")
    except Exception as e:
        logger.error(f"Failed to write JSON file {outfile}: {e}")
        raise

def write_yaml(data: Any, outfile: Union[str, Path]) -> None:
    """
    Writes data to a YAML file with proper formatting.
    
    Args:
        data: The data to write to the file
        outfile: The output file path
    """
    outfile = Path(outfile) if not isinstance(outfile, Path) else outfile
    try:
        with open(outfile, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        logger.info(f"YAML configuration written to: {outfile}")
    except Exception as e:
        logger.error(f"Failed to write YAML file {outfile}: {e}")
        raise

def generate_global_config() -> Dict[str, Any]:
    """
    Generates a dictionary containing global configurations.
    Uses environment variables for sensitive data when available.
    
    Returns:
        Dict: The configuration dictionary
    """
    # Get the current user's username
    username = os.environ.get('USERNAME', os.environ.get('USER', 'user'))
    
    # Get the login from environment or use default
    login = os.environ.get('USER_LOGIN', 'GBOGEB')
    
    # Get current timestamp
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    
    # Default template path with fallback options
    template_path = os.environ.get(
        'OFFICE_TEMPLATE_PATH', 
        str(Path.home() / "OneDrive - Studiecentrum voor Kernenergie/Documents/Custom Office Templates/GPT Outline.dotx")
    )
    
    config = {
        "metadata": {
            "created_by": login,
            "created_at": timestamp,
            "last_updated": timestamp
        },
        "paths": {
            "python": str(Path(sys.executable)),
            "git_bash": str(Path(os.environ.get(
                'GIT_BASH_PATH', 
                "C:/Program Files/Git/bin/bash.exe"
            ))),
            "pandoc": os.environ.get('PANDOC_PATH', "pandoc"),
            "office_template": str(Path(template_path))
        },
        "environment": {
            "development": "MS VS Code, Git BASH and PowerShell",
            "requirements": [
                "Python 3.x",
                "PyYAML",
                "pandoc"
            ]
        },
        "api_keys": {
            "openai": os.environ.get('OPENAI_API_KEY', ""),
            "github": os.environ.get('GITHUB_API_KEY', "")
        },
        "deliverables_matrix": {
            "data_tables": 15,
            "description": "YAML data tables for design/process deliverables"
        }
    }
    return config

def install_dependencies(requirements_file: Union[str, Path] = "requirements.txt") -> bool:
    """
    Installs dependencies from a requirements file using subprocess.
    
    Args:
        requirements_file: Path to the requirements file
        
    Returns:
        bool: True if installation was successful, False otherwise
    """
    requirements_file = Path(requirements_file) if not isinstance(requirements_file, Path) else requirements_file
    if not requirements_file.is_file():
        logger.warning(f"Requirements file '{requirements_file}' not found")
        return False
        
    logger.info(f"Installing dependencies from {requirements_file}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def run_tests() -> bool:
    """
    Run built-in tests to validate the script functionality.
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    logger.info("Running built-in tests...")
    
    # Test markdown parsing
    test_md = (
        "# Heading 1\n\n"
        "## Heading 2\n\n"
        "### Heading 3\n\n"
        "## Another Heading 2"
    )
    
    result = parse_markdown(test_md)
    
    # Simple validation
    try:
        assert len(result) == 1, "Expected one top-level heading"
        assert result[0]["title"] == "Heading 1", "First heading should be 'Heading 1'"
        assert len(result[0]["children"]) == 2, "Expected two level 2 headings"
        assert result[0]["children"][0]["title"] == "Heading 2", "First child should be 'Heading 2'"
        assert result[0]["children"][1]["title"] == "Another Heading 2", "Second child should be 'Another Heading 2'"
        assert len(result[0]["children"][0]["children"]) == 1, "First level 2 heading should have one child"
        
        # Test validation function
        assert validate_markdown("# Valid heading\nContent") == True
        assert validate_markdown("Invalid content without heading") == False
        assert validate_markdown("") == False
        
        logger.info("All tests passed!")
        return True
    except AssertionError as e:
        logger.error(f"Test failed: {e}")
        return False

class TestWriteJson(unittest.TestCase):
    def test_file_created_and_content_correct(self):
        data = {"key": "value", "number": 123}
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = os.path.join(tmpdir, "test.json")
            captured_output = tempfile.TemporaryFile(mode='w+t')
            original_stdout = sys.stdout
            sys.stdout = captured_output
            try:
                write_json(data, outfile)
            finally:
                sys.stdout = original_stdout
                captured_output.seek(0)
                output = captured_output.read()

            # Confirm file was created
            self.assertTrue(os.path.isfile(outfile))
            # Read the file and check its content
            with open(outfile, "r", encoding="utf-8") as f:
                written_data = json.load(f)
            self.assertEqual(written_data, data)
            # Check that the print statement contains the correct message
            self.assertIn(f"JSON outline written to: {outfile}", output)

    def test_overwrites_existing_file(self):
        data_initial = {"initial": "data"}
        data_new = {"new": "data"}
        with tempfile.TemporaryDirectory() as tmpdir:
            outfile = os.path.join(tmpdir, "test.json")
            # Write initial content
            with open(outfile, "w", encoding="utf-8") as f:
                f.write("old content")
            # Overwrite with new data
            write_json(data_new, outfile)
            with open(outfile, "r", encoding="utf-8") as f:
                written_data = json.load(f)
            self.assertEqual(written_data, data_new)

class TestMarkdownParser(unittest.TestCase):
    def test_empty_markdown(self):
        self.assertEqual(parse_markdown(""), [])
        self.assertFalse(validate_markdown(""))
        
    def test_simple_heading(self):
        md = "# Test Heading"
        result = parse_markdown(md)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Test Heading")
        self.assertEqual(result[0]["level"], 1)
        
    def test_nested_headings(self):
        md = """# H1
## H2
### H3
## H2-2"""
        result = parse_markdown(md)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]["children"]), 2)
        self.assertEqual(result[0]["children"][0]["children"][0]["title"], "H3")
        
    def test_validation(self):
        self.assertTrue(validate_markdown("# Valid\n## Structure"))
        self.assertFalse(validate_markdown("Invalid structure"))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Markdown to JSON/YAML converter",
        epilog="Example: python WORD_round_trip_250520_1519.py --input MASTER.md\n" +
               "         python WORD_round_trip_250520_1519.py --test"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory")
    parser.add_argument("--input", type=str, help="Input markdown file")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--run-tests", action="store_true", help="Run built-in tests")
    parser.add_argument("--unit-tests", action="store_true", help="Run unittest suite")
    args = parser.parse_args()

    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.debug("Verbose logging enabled")

    # Run unit tests if requested
    if args.unit_tests:
        import unittest
        suite = unittest.TestLoader().loadTestsFromTestCase(TestWriteJson)
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMarkdownParser))
        unittest.TextTestRunner(verbosity=2).run(suite)
        sys.exit(0)
        
    # Run built-in tests if requested
    if args.run_tests:
        success = run_tests()
        sys.exit(0 if success else 1)

    # If no arguments provided, default to test mode
    if len(sys.argv) == 1:
        logger.info("No arguments provided. Running in test mode...")
        args.test = True

    # Install dependencies if flag is provided
    if args.install_deps:
        if install_dependencies():
            logger.info("Dependencies installed successfully")
        else:
            logger.error("Failed to install dependencies")
        sys.exit(0)

    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        logger.info(f"Creating output directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)

    global_config = generate_global_config()

    # Check if pandoc is available in PATH
    pandoc_exe = shutil.which(global_config["paths"]["pandoc"])
    if pandoc_exe is None:
        logger.warning("Pandoc executable not found in PATH")
        logger.warning("Some features may not work. Please install pandoc and add it to your system PATH")

    if args.input:
        input_file = Path(args.input)
        if not input_file.is_file():
            logger.error(f"Input file not found: {input_file}")
            sys.exit(1)
            
        try:
            with open(input_file, "r", encoding="utf-8") as f:
                md_content = f.read()
        except Exception as e:
            logger.error(f"Failed to read input file {input_file}: {e}")
            sys.exit(1)
            
        # Validate input file
        if not validate_markdown(md_content):
            logger.warning("Input file has validation warnings. Continuing anyway...")
    else:  # Test mode
        logger.info("Running in test mode with sample markdown content...")
        md_content = (
            "# Heading 1\n\n"
            "Some text under heading 1\n\n"
            "## Heading 2\n\n"
            "More text under heading 2\n\n"
            "### Heading 3\n\n"
            "Text under heading 3\n\n"
            "## Another Heading 2\n\n"
            "Text under another heading 2"
        )

    # Process markdown
    outline = parse_markdown(md_content)

    # Define output file paths
    json_output_file = output_dir / "outline.json"
    yaml_output_file = output_dir / "global_config.yaml"

    # Write output files
    write_json(outline, json_output_file)
    write_yaml(global_config, yaml_output_file)

    logger.info("Conversion completed successfully!")

# Debug configuration for VS Code - can be saved as .vscode/launch.json
debug_config = {
  "version": "0.2.0",
  "configurations": [
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Launch Python Program",
      "program": "${workspaceFolder}/WORD_round_trip_250520_1519.py",
      "console": "integratedTerminal",
      "args": ["${input:commandLineArgs}"]
    },
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Debug Current File",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Run Tests",
      "program": "${workspaceFolder}/WORD_round_trip_250520_1519.py",
      "args": ["--run-tests"],
      "console": "integratedTerminal"
    },
    {
      "type": "debugpy",
      "request": "launch",
      "name": "Run Unit Tests",
      "program": "${workspaceFolder}/WORD_round_trip_250520_1519.py",
      "args": ["--unit-tests"],
      "console": "integratedTerminal"
    }
  ],
  "inputs": [
    {
      "type": "promptString",
      "id": "commandLineArgs",
      "description": "Command line arguments",
      "default": "--test"
    }
  ]
}