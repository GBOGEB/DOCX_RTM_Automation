import re
from pathlib import Path

YELLOW_MD = "<!-- YELLOW: Check for unmatched or missing brackets below -->"
YELLOW_YAML_START = "# YELLOW: Check for unmatched or missing brackets below"
YELLOW_YAML_END = "# YELLOW: End of YAML file, check for unmatched or missing brackets above"

def process_markdown(filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = []
    in_code_block = False
    for i, line in enumerate(lines):
        # Detect start of code block
        if re.match(r"^```", line):
            if not in_code_block:
                new_lines.append(f"{YELLOW_MD}\n")
                in_code_block = True
            else:
                in_code_block = False
        new_lines.append(line)
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def process_yaml(filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines[0].startswith("# YELLOW"):
        lines.insert(0, f"{YELLOW_YAML_START}\n")
    if not lines[-1].startswith("# YELLOW: End of YAML"):
        lines.append(f"{YELLOW_YAML_END}\n")
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

def main():
    root = Path(".")
    for item_path in root.rglob('*'):
        if item_path.is_file():
            if item_path.suffix == ".md":
                print(f"Processing Markdown: {item_path}")
                process_markdown(item_path)
            elif item_path.suffix in [".yml", ".yaml"]:
                print(f"Processing YAML: {item_path}")
                process_yaml(item_path)

if __name__ == "__main__":
    main()
