# Pandoc Integration Model

import subprocess

# Ensure Pandoc is in your system's PATH.

# Other paths...
pandoc_path = "pandoc"


def get_pandoc_version():
    """Get the installed Pandoc version."""
    try:
        result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
        return result.stdout.split("\n")[0]
    except Exception as e:
        return f"Error getting Pandoc version: {str(e)}"


def convert_with_pandoc(
    input_file,
    output_file,
    format_from="docx",
    format_to="markdown",
    toc=True,
    toc_depth=6,
    number_sections=True,
    lua_filter=None,
):
    """
    Convert a document using Pandoc with specified options.

    Args:
        input_file: Path to input file
        output_file: Path to output file
        format_from: Input format (default: 'docx')
        format_to: Output format (default: 'markdown')
        toc: Whether to include table of contents (default: True)
        toc_depth: Depth of table of contents (default: 6)
        number_sections: Whether to number sections (default: True)
        lua_filter: Path to Lua filter file (default: None)
    """
    cmd = ["pandoc", input_file, "-f", format_from, "-t", format_to]

    if toc:
        cmd.extend(["--toc", f"--toc-depth={toc_depth}"])

    if number_sections:
        cmd.append("--number-sections")

    if lua_filter:
        cmd.append(f"--lua-filter={lua_filter}")

    cmd.extend(["-o", output_file])

    print(f"Running Pandoc command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Pandoc conversion failed: {result.stderr}")

    return result.stdout
