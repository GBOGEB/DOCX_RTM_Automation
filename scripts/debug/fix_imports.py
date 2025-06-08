#!/usr/bin/env python3
"""
Fix import errors in the agents directory by correcting import paths.
"""

import re
from pathlib import Path


def add_sys_path_code(content):
    """Add code to add project root to sys.path if not already present"""
    if "import sys" not in content:
        sys_path_code = (
            "import sys\n"
            "from pathlib import Path\n\n"
            "# Add project root to path\n"
            "_project_root = Path(__file__).resolve().parent.parent\n"
            "if str(_project_root) not in sys.path:\n"
            "    sys.path.insert(0, str(_project_root))\n\n"
        )
        # Find the best place to insert this code - after existing imports or at the top
        import_match = re.search(
            r"^import\s+[a-zA-Z0-9_]+|^from\s+[a-zA-Z0-9_\.]+\s+import",
            content,
            re.MULTILINE,
        )
        if import_match:
            # Find the last import statement
            matches = list(
                re.finditer(
                    r"^import\s+[a-zA-Z0-9_]+|^from\s+[a-zA-Z0-9_\.]+\s+import",
                    content,
                    re.MULTILINE,
                )
            )
            if matches:
                last_import = matches[-1]
                last_import_line_end = content.find("\n", last_import.end())
                if last_import_line_end == -1:  # No newline after last import
                    last_import_line_end = len(content)
                return (
                    content[: last_import_line_end + 1]
                    + "\n"
                    + sys_path_code
                    + content[last_import_line_end + 1 :]
                )

        # If no imports found, insert at the top after any module docstrings
        docstring_match = re.search(r'^""".*?"""', content, re.DOTALL)
        if docstring_match:
            return (
                content[: docstring_match.end()]
                + "\n\n"
                + sys_path_code
                + content[docstring_match.end() :]
            )
        else:
            return sys_path_code + content
    return content


def fix_imports_in_file(file_path):
    """Fix incorrect imports in a file."""
    print(f"Checking {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if there are any problematic imports
    has_changed = False

    # Replace incorrect imports referring to DOCX_RTM_Automation_v1_0
    if "DOCX_RTM_Automation_v1_0" in content:
        fixed_content = re.sub(r"from\s+DOCX_RTM_Automation_v1_0\.", "from ", content)
        fixed_content = re.sub(
            r"import\s+DOCX_RTM_Automation_v1_0\.", "import ", fixed_content
        )

        if fixed_content != content:
            has_changed = True
            content = fixed_content
            print(f"  Fixed incorrect imports in {file_path}")

    # Add sys.path modification if needed
    fixed_content = add_sys_path_code(content)
    if fixed_content != content:
        has_changed = True
        content = fixed_content
        print(f"  Added sys.path modification to {file_path}")

    # Write back if changes were made
    if has_changed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  Updated {file_path}")
        return True

    print(f"  No import issues found in {file_path}")
    return False


def fix_agent_imports():
    """Fix imports in agent files."""
    agents_dir = Path("agents")
    if not agents_dir.exists():
        print("Agents directory not found.")
        return

    fixed_files = 0
    for file_path in agents_dir.glob("**/*.py"):
        if fix_imports_in_file(file_path):
            fixed_files += 1

    print(f"\nFixed imports in {fixed_files} files in the agents directory.")


def create_vscode_launch_json():
    """Create or update .vscode/launch.json for proper Python imports."""
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    launch_json = vscode_dir / "launch.json"

    config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: Current File with Project Root",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}"},
            },
            {
                "name": "Python: Debug RTM Pipeline",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/scripts/full_integration.py",
                "args": ["--pipeline"],
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}"},
            },
        ],
    }

    import json

    with open(launch_json, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    print(f"Created/updated VS Code launch.json at {launch_json}")


def fix_src_imports():
    """Fix imports in src files."""
    src_dir = Path("src")
    if not src_dir.exists():
        print("Src directory not found.")
        return

    fixed_files = 0
    for file_path in src_dir.glob("**/*.py"):
        if fix_imports_in_file(file_path):
            fixed_files += 1

    print(f"\nFixed imports in {fixed_files} files in the src directory.")


if __name__ == "__main__":
    print("Fixing import errors...\n")

    # Fix imports in agent files
    fix_agent_imports()

    # Fix imports in src files
    fix_src_imports()

    # Create VS Code launch.json
    create_vscode_launch_json()

    print("\nImport fixes complete. Now try running:")
    print("  python debug_helpers.py")
    print("to check if import errors are resolved.")
