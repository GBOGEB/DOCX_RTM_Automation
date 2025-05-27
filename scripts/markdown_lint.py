import sys
from pathlib import Path

def check_markdown_files(root="."):
    md_files = list(Path(root).rglob("*.md"))
    if not md_files:
        print("No Markdown files found.")
        return 0

    issues = 0
    for md_file in md_files:
        with open(md_file, encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if len(line.rstrip("\n")) > 120:
                    print(f"{md_file}:{i}: Line exceeds 120 characters")
                    issues += 1
                if "\t" in line:
                    print(f"{md_file}:{i}: Contains tab character")
                    issues += 1
    if issues == 0:
        print("All Markdown files passed basic lint checks.")
    else:
        print(f"Found {issues} issues.")
    return issues

if __name__ == "__main__":
    sys.exit(check_markdown_files())
