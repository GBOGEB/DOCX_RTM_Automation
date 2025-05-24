# Pandoc Integration Model

import sys
import os
import subprocess

# Add path to Pandoc pip modules
PANDOC_PIP_PATH = r"c:\Users\gbonthuy\Downloads\pandoc-3.6.3-windows-x86_64\pandoc-3.6.3\venv\Lib\site-packages"

# Other paths...
pandoc_path = "pandoc"
pandoc_pip_modules = {
    "init": "c:/Users/gbonthuy/Downloads/pandoc-3.6.3-windows-x86_64/pandoc-3.6.3/venv/Lib/site-packages/pip/__init__.py",
    "main": "c:/Users/gbonthuy/Downloads/pandoc-3.6.3-windows-x86_64/pandoc-3.6.3/venv/Lib/site-packages/pip/__main__.py",
    "runner": "c:/Users/gbonthuy/Downloads/pandoc-3.6.3-windows-x86_64/pandoc-3.6.3/venv/Lib/site-packages/pip/__pip-runner__.py"
}

# Add Pandoc pip path to system path if it exists
if os.path.exists(PANDOC_PIP_PATH):
    sys.path.append(PANDOC_PIP_PATH)
    print(f"Added Pandoc modules path: {PANDOC_PIP_PATH}")
else:
    print(f"Warning: Pandoc modules path not found: {PANDOC_PIP_PATH}")

def get_pandoc_version():
    """Get the installed Pandoc version."""
    try:
        result = subprocess.run(['pandoc', '--version'], capture_output=True, text=True)
        return result.stdout.split('\n')[0]
    except Exception as e:
        return f"Error getting Pandoc version: {str(e)}"

def convert_with_pandoc(input_file, output_file, format_from='docx', format_to='markdown', 
                        toc=True, toc_depth=7, number_sections=True, lua_filter=None):
    """
    Convert a document using Pandoc with specified options.
    
    Args:
        input_file: Path to input file
        output_file: Path to output file
        format_from: Input format (default: 'docx')
        format_to: Output format (default: 'markdown')
        toc: Whether to include table of contents (default: True)
        toc_depth: Depth of table of contents (default: 7)
        number_sections: Whether to number sections (default: True)
        lua_filter: Path to Lua filter file (default: None)
    """
    cmd = ['pandoc', input_file, '-f', format_from, '-t', format_to]
    
    if toc:
        cmd.extend(['--toc', f'--toc-depth={toc_depth}'])
    
    if number_sections:
        cmd.append('--number-sections')
    
    if lua_filter:
        cmd.append(f'--lua-filter={lua_filter}')
    
    cmd.extend(['-o', output_file])
    
    print(f"Running Pandoc command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Pandoc conversion failed: {result.stderr}")
    
    return result.stdout
