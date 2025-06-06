"""Script to manage and trace project requirements."""
import os
import re
import json
import subprocess
import markdown

# Constants
INPUT_DIR = r"C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\input"
OUTPUT_DIR = r"C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\output"
REQUIREMENTS_FILE = os.path.join(INPUT_DIR, "requirements.md")
OUTPUT_SUMMARY = os.path.join(OUTPUT_DIR, "summary_analysis.txt")
OUTPUT_TRACEABILITY = os.path.join(OUTPUT_DIR, "requirements_traceability.json")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)


def check_git_repo():
    """Check if the script is running inside a Git repository."""
    try:
        subprocess.run(
            ["git", "status"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print("This script is running inside a Git repository.")
        return True
    except subprocess.CalledProcessError:
        print("Warning: This script is not running inside a Git repository.")
        return False


def find_project_files(directory="."):
    """Find all relevant project files (excluding certain directories/files)."""
    excluded_dirs = [".git", ".venv", "__pycache__", "node_modules", "output"]
    excluded_extensions = [".pyc", ".pyo", ".pyd", ".git", ".DS_Store"]

    all_files_local = []

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in excluded_dirs]

        for file in files:
            _, ext = os.path.splitext(file)
            if ext not in excluded_extensions and not file.startswith("."):
                file_path = os.path.join(root, file)
                all_files_local.append(file_path)

    return all_files_local


def parse_markdown(file_path):
    """Parse a markdown file and return its content."""
    with open(file_path, "r", encoding="utf-8") as file:
        content_local = file.read()
    return content_local


def extract_requirements(content_param):
    """Extract requirements from markdown content."""
    requirements_local = {}

    req_pattern = re.compile(r"^#+\s+((?:[A-Z]+-\d+(?:\.\d+)*):.*?)$", re.MULTILINE)

    for match in req_pattern.finditer(content_param):
        req_id = match.group(1).strip()
        line_num = content_param[: match.start()].count("\n") + 1

        category = req_id.split("-")[0]

        requirements_local[req_id] = {
            "line": line_num,
            "text": match.group(0).strip(),
            "implementation_files": [],
            "category": category,
            "status": "Not Implemented",
        }

    return requirements_local


def find_requirements_in_code(code_files, requirements_local):
    """Search for requirements in code files."""
    for file_path in code_files:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content_local = file.read()

                for req_id in requirements_local:
                    if req_id in content_local:
                        requirements_local[req_id]["implementation_files"].append(file_path)
                        requirements_local[req_id]["status"] = "Implemented"
        except OSError as e:
            print(f"Error reading file {file_path}: {e}")

    return requirements_local


def analyze_requirements(content_param):
    """Analyze requirements from markdown content."""
    lines = content_param.splitlines()
    total_lines = len(lines)

    requirement_pattern = re.compile(r"^#+\s+([A-Z]+-\d+(?:\.\d+)*):")
    requirements = [line for line in lines if requirement_pattern.match(line)]
    total_requirements = len(requirements)

    requirement_types = {}
    for req in requirements:
        match = requirement_pattern.match(req)
        if match:
            req_id = match.group(1)
            req_type = req_id.split("-")[0]
            requirement_types[req_type] = requirement_types.get(req_type, 0) + 1

    return {
        "total_lines": total_lines,
        "total_requirements": total_requirements,
        "requirement_types": requirement_types,
        "requirements": requirements,
    }


def write_summary(analysis_data_param, requirements_with_files_param):
    """Write a summary of the requirements analysis."""
    with open(OUTPUT_SUMMARY, "w", encoding="utf-8") as file:
        file.write("Summary and Analysis\n")
        file.write("====================\n")
        file.write(f"Total Lines: {analysis_data_param['total_lines']}\n")
        file.write(f"Total Requirements: {analysis_data_param['total_requirements']}\n\n")

        file.write("Requirement Types:\n")
        for req_type, count in analysis_data_param["requirement_types"].items():
            category_name = get_category_name(req_type)
            file.write(f"  {req_type} ({category_name}): {count}\n")

        file.write("\nRequirements and Implementation Files:\n")
        for req_id, details in requirements_with_files_param.items():
            file.write(f"\n{req_id}:\n")
            file.write(f"  Description: {details['text']}\n")
            file.write(f"  Status: {details['status']}\n")
            if details["implementation_files"]:
                file.write("  Implementation Files:\n")
                for impl_file in details["implementation_files"]:
                    file.write(f"    - {impl_file}\n")
            else:
                file.write("  No implementation files found\n")

    print(f"Summary written to {OUTPUT_SUMMARY}")


def get_category_name(category_code):
    """Get full category names for requirement types."""
    categories = {
        "CF": "Core Functionality",
        "FR": "Functional Requirement",
        "NFR": "Non-Functional Requirement",
        "IR": "Interface Requirement",
        "IM": "Integration Method",
    }
    return categories.get(category_code, "Unknown Category")


def generate_traceability_matrix(requirements_with_files_param):
    """Generate a traceability matrix for requirements and implementation files."""
    traceability = {"requirements": {}, "files": {}}

    for req_id, details in requirements_with_files_param.items():
        traceability["requirements"][req_id] = {
            "description": details["text"],
            "files": details["implementation_files"],
            "status": details["status"],
        }

    file_to_reqs = {}
    for req_id, details in requirements_with_files_param.items():
        for file_path in details["implementation_files"]:
            if file_path not in file_to_reqs:
                file_to_reqs[file_path] = []
            file_to_reqs[file_path].append(req_id)

    traceability["files"] = file_to_reqs

    with open(OUTPUT_TRACEABILITY, "w", encoding="utf-8") as f:
        json.dump(traceability, f, indent=2)

    print(f"Traceability matrix written to {OUTPUT_TRACEABILITY}")


def main():
    """Main function to run the requirement extraction and analysis."""
    is_git_repo_local = check_git_repo()

    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"Error: Requirements file '{REQUIREMENTS_FILE}' does not exist.")
    else:
        project_root_local = "."
        if is_git_repo_local:
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--show-toplevel"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                project_root_local = result.stdout.strip()
            except subprocess.CalledProcessError:
                pass

        print(f"Using project root: {project_root_local}")

        all_files = find_project_files(project_root_local)
        print(f"Found {len(all_files)} files in the project")

        content_local = parse_markdown(REQUIREMENTS_FILE)

        requirements = extract_requirements(content_local)
        print(f"Extracted {len(requirements)} requirements from {REQUIREMENTS_FILE}")

        requirements_with_files = find_requirements_in_code(all_files, requirements)

        analysis_data = analyze_requirements(content_local)

        write_summary(analysis_data, requirements_with_files)
        generate_traceability_matrix(requirements_with_files)


if __name__ == "__main__":
    main()
