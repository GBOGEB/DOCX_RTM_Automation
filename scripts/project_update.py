#!/usr/bin/env python3
"""
DOCX RTM Automation - Complete Project Update & Refactor
========================================================

This script performs a comprehensive update of the DOCX RTM Automation project:
1. Project structure analysis and standardization
2. Error detection and fixing
3. Code refactoring and optimization
4. Documentation updates
5. GitHub repository preparation
"""

import sys
import json
import yaml
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import logging
import re  # Added for regex operations


# ANSI colors for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


class ProjectUpdater:
    def __init__(self):
        self.project_root = Path.cwd()
        self.setup_logging()
        self.issues_found = []
        self.fixes_applied = []
        self.config = self._load_global_config()
        self.sub_repo_paths = []
        if self.config:
            self.sub_repo_paths = [
                self.project_root / Path(p)
                for p in self.config.get("repository_settings", {}).get(
                    "sub_repositories", []
                )
            ]

    def _load_global_config(self):
        """Load global_config.yaml"""
        config_path = self.project_root / "global_config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                self.print_status("ERROR", f"Failed to load global_config.yaml: {e}")
                return {}
        return {}

    def setup_logging(self):
        """Setup comprehensive logging"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"project_update_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file, encoding="utf-8"),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def print_header(self, text, color=Colors.BLUE):
        """Print formatted header"""
        print(f"\n{color}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
        print(f"{color}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
        print(f"{color}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")

    def print_status(self, status, message, details=None):
        """Print status with color coding"""
        color_map = {
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "INFO": Colors.BLUE,
            "FIXED": Colors.CYAN,
        }

        color = color_map.get(status, Colors.BLUE)
        print(f"{color}[{status}]{Colors.ENDC} {message}")

        if details:
            print(f"         {details}")

        self.logger.info(f"[{status}] {message}")

    def analyze_project_structure(self):
        """Analyze current project structure"""
        self.print_header("PROJECT STRUCTURE ANALYSIS")

        expected_structure = {
            "code": "Main application code",
            "src": "Source modules and components",
            "src/core": "Core functionality modules",
            "src/modules": "Feature-specific modules",
            "src/extractors": "Data extraction utilities",
            "config": "Configuration files",
            "input": "Input documents directory",
            "output": "Generated output files",
            "logs": "Application logs",
            "scripts": "Utility and automation scripts",
            "docs": "Project documentation",
            "tests": "Unit and integration tests",
        }

        existing_dirs = []
        missing_dirs = []

        for dir_path, description in expected_structure.items():
            full_path = self.project_root / dir_path
            if full_path.exists():
                existing_dirs.append(dir_path)
                self.print_status("INFO", f"Directory exists: {dir_path}", description)
            else:
                missing_dirs.append(dir_path)
                self.issues_found.append(f"Missing directory: {dir_path}")

        if missing_dirs:
            self.print_status("WARNING", f"Missing {len(missing_dirs)} directories")
            for missing in missing_dirs:
                self.print_status("WARNING", f"  - {missing}")

        # Analyze sub-repositories if configured
        if self.sub_repo_paths:
            self.print_status("INFO", "Analyzing configured sub-repositories...")
            for sub_repo_path in self.sub_repo_paths:
                if sub_repo_path.exists() and sub_repo_path.is_dir():
                    self.print_status("INFO", f"Sub-repository found: {sub_repo_path}")
                else:
                    self.print_status(
                        "WARNING",
                        f"Sub-repository not found or not a directory: {sub_repo_path}",
                    )
                    self.issues_found.append(f"Missing sub-repository: {sub_repo_path}")
        else:
            self.print_status(
                "INFO", "No sub-repositories configured in global_config.yaml"
            )

        return existing_dirs, missing_dirs, expected_structure

    def create_missing_directories(self, missing_dirs, expected_structure):
        """Create missing directories with README files"""
        self.print_header("CREATING MISSING DIRECTORIES")

        for dir_path in missing_dirs:
            try:
                full_path = self.project_root / dir_path
                full_path.mkdir(parents=True, exist_ok=True)

                # Create README.md for documentation
                readme_content = f"""# {dir_path.replace("/", " - ").title()}

{expected_structure[dir_path]}

## Purpose
This directory is part of the DOCX RTM Automation project structure.

## Contents
- [Add description of contents here]

## Usage
- [Add usage instructions here]

---
*Created by project_update.py on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
                readme_path = full_path / "README.md"
                if not readme_path.exists():
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write(readme_content)

                self.print_status("FIXED", f"Created directory: {dir_path}")
                self.fixes_applied.append(f"Created directory: {dir_path}")

            except Exception as e:
                self.print_status("ERROR", f"Failed to create {dir_path}: {e}")

    def scan_python_files(self):
        """Scan all Python files for common issues"""
        self.print_header("PYTHON FILES ANALYSIS")

        python_files_to_scan = list(self.project_root.rglob("*.py"))

        # Add files from sub-repositories
        for sub_repo_path in self.sub_repo_paths:
            if sub_repo_path.exists() and sub_repo_path.is_dir():
                self.print_status(
                    "INFO", f"Scanning Python files in sub-repository: {sub_repo_path}"
                )
                python_files_to_scan.extend(list(sub_repo_path.rglob("*.py")))

        # Remove duplicates that might arise if sub_repo_path is within project_root (e.g. "./submodule")
        python_files = sorted(list(set(python_files_to_scan)))

        issues = {
            "missing_docstrings": [],
            "import_errors": [],
            "syntax_errors": [],
            "hardcoded_paths": [],
            "toc_depth_issues": [],
        }

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for missing module docstrings
                if not content.strip().startswith(
                    '"""'
                ) and not content.strip().startswith("'''"):
                    issues["missing_docstrings"].append(str(py_file))

                # Check for hardcoded paths
                if "\\" in content or "C:" in content:
                    issues["hardcoded_paths"].append(str(py_file))

                # Check for toc-depth issues (values > 6)
                # This regex looks for toc-depth followed by a colon or equals, then a number 7,8,9 or any 2+ digit number.
                if re.search(
                    r"toc-depth\s*[:=]\s*([7-9]|\d{2,})", content, re.IGNORECASE
                ):
                    issues["toc_depth_issues"].append(str(py_file))

                # Basic syntax check
                try:
                    compile(content, py_file, "exec")
                except SyntaxError as e:
                    issues["syntax_errors"].append(f"{py_file}: {e}")

            except Exception as e:
                self.print_status("ERROR", f"Error analyzing {py_file}: {e}")

        # Report findings
        for issue_type, files in issues.items():
            if files:
                self.print_status(
                    "WARNING", f"Found {len(files)} files with {issue_type}"
                )
                for file in files[:5]:  # Show first 5
                    self.print_status("WARNING", f"  - {file}")
                if len(files) > 5:
                    self.print_status("WARNING", f"  ... and {len(files) - 5} more")

        return issues

    def fix_common_python_issues(self, issues):
        """Fix common Python code issues"""
        self.print_header("FIXING PYTHON ISSUES")

        # Fix toc-depth issues
        if issues["toc_depth_issues"]:
            self.print_status(
                "INFO",
                f"Attempting to fix toc-depth issues in {len(issues['toc_depth_issues'])} files...",
            )
        for file_path_str in issues["toc_depth_issues"]:
            file_path = Path(file_path_str)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                original_content = content

                # Patterns to fix toc-depth values > 6
                # Targets values 7,8,9 and any multi-digit numbers (e.g., 10, 12)
                patterns = [
                    (r"--toc-depth=([7-9]\d*|\d{2,})", "--toc-depth=6"),
                    (r"--toc-depth=([7-9])", "--toc-depth=6"),
                    (r'"toc-depth":\s*([7-9]\d*|\d{2,})', '"toc-depth": 6'),
                    (r'"toc-depth":\s*([7-9])', '"toc-depth": 6'),
                    (r"toc_depth:\s*([7-9]\d*|\d{2,})", "toc_depth: 6"),
                    (r"toc_depth:\s*([7-9])", "toc_depth: 6"),
                    (r"toc_depth\s*=\s*([7-9]\d*|\d{2,})", "toc_depth=6"),
                    (r"toc_depth\s*=\s*([7-9])", "toc_depth=6"),
                    (r"TOC_DEPTH\s*=\s*([7-9]\d*|\d{2,})", "TOC_DEPTH=6"),
                    (r"TOC_DEPTH\s*=\s*([7-9])", "TOC_DEPTH=6"),
                ]

                modified_content = content
                changes_made_count = 0
                for pattern, replacement in patterns:
                    new_content_after_sub = re.sub(
                        pattern, replacement, modified_content
                    )
                    if new_content_after_sub != modified_content:
                        changes_made_count += 1
                    modified_content = new_content_after_sub

                if modified_content != original_content:
                    # Create backup
                    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                    shutil.copy2(file_path, backup_path)
                    self.print_status("INFO", f"Created backup: {backup_path}")

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(modified_content)

                    self.print_status(
                        "FIXED",
                        f"Fixed toc-depth in {file_path} ({changes_made_count} replacements)",
                    )
                    self.fixes_applied.append(f"Fixed toc-depth in {file_path}")
                else:
                    self.print_status(
                        "INFO",
                        f"No toc-depth changes needed for {file_path} after checking patterns.",
                    )

            except Exception as e:
                self.print_status(
                    "ERROR", f"Failed to fix toc-depth in {file_path}: {e}"
                )

    def update_configuration_files(self):
        """Update and standardize global_config.yaml"""
        self.print_header("CONFIGURATION FILES UPDATE")

        config_path = self.project_root / "global_config.yaml"
        config_updated = False

        if not config_path.exists():
            self.print_status(
                "WARNING", f"{config_path} not found. Creating with defaults."
            )
            config = {}
        else:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f) or {}
            except Exception as e:
                self.print_status(
                    "ERROR",
                    f"Failed to load {config_path}: {e}. Will create with defaults.",
                )
                config = {}

        original_config_str = yaml.dump(config)

        # Ensure 'project' section
        if "project" not in config:
            config["project"] = {}
        config["project"].setdefault("name", "DOCX RTM Automation")
        config["project"].setdefault("version", "1.0.0")

        # Ensure 'paths' section
        if "paths" not in config:
            config["paths"] = {}
        config["paths"].setdefault("input_dir", "input")
        config["paths"].setdefault("output_dir", "output")
        config["paths"].setdefault("logs_dir", "logs")
        config["paths"].setdefault("config_dir", "config")

        # Ensure 'repository_settings' section
        if "repository_settings" not in config:
            config["repository_settings"] = {}
        config["repository_settings"].setdefault("main_repository_path", ".")
        config["repository_settings"].setdefault("sub_repositories", [])
        config["repository_settings"].setdefault("default_branch", "main")

        # Ensure 'api_keys' section and 'openai' key
        if "api_keys" not in config:
            config["api_keys"] = {}
        config["api_keys"].setdefault("openai", "your-openai-api-key")
        config["api_keys"].setdefault("github", "")

        # Ensure 'ai_services' and 'openai' subsection
        if "ai_services" not in config:
            config["ai_services"] = {}
        if "openai" not in config["ai_services"]:
            config["ai_services"]["openai"] = {}
        config["ai_services"]["openai"].setdefault(
            "default_model", "gpt-4-turbo-preview"
        )
        config["ai_services"]["openai"].setdefault("max_tokens", 4096)
        config["ai_services"]["openai"].setdefault("temperature", 0.7)

        # Ensure 'pandoc' section and fix 'toc_depth'
        if "pandoc" not in config:
            config["pandoc"] = {}
        config["pandoc"].setdefault("lua_filter", "config/extend_headings.lua")
        config["pandoc"].setdefault("number_sections", True)

        current_toc_depth = config["pandoc"].get("toc_depth")
        if current_toc_depth is None:  # Set default if not present
            config["pandoc"]["toc_depth"] = 6
        elif isinstance(current_toc_depth, int) and current_toc_depth > 6:
            config["pandoc"]["toc_depth"] = 6
            self.print_status(
                "FIXED", "Adjusted pandoc.toc_depth to 6 in global_config.yaml"
            )
            self.fixes_applied.append("Adjusted pandoc.toc_depth in global_config.yaml")
        elif (
            not isinstance(current_toc_depth, int) or current_toc_depth <= 0
        ):  # Correct invalid values
            config["pandoc"]["toc_depth"] = 6
            self.print_status(
                "FIXED",
                f"Corrected invalid pandoc.toc_depth (was {current_toc_depth}) to 6 in global_config.yaml",
            )
            self.fixes_applied.append(
                "Corrected pandoc.toc_depth in global_config.yaml"
            )

        if yaml.dump(config) != original_config_str or not config_path.exists():
            config_updated = True

        if config_updated:
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                self.print_status("SUCCESS", f"Updated {config_path}")
                self.fixes_applied.append(f"Updated {config_path}")
            except Exception as e:
                self.print_status("ERROR", f"Failed to write {config_path}: {e}")
        else:
            self.print_status("INFO", f"{config_path} is up-to-date.")

        # Reload self.config if it was updated
        if config_updated:
            self.config = self._load_global_config()

    def create_project_documentation(self):
        """Create comprehensive project documentation"""
        self.print_header("DOCUMENTATION CREATION")

        # Create main README.md
        readme_content = f"""# DOCX RTM Automation

A comprehensive automation pipeline for converting DOCX documents to Requirements Traceability Matrix (RTM) format.

## 🚀 Features

- **DOCX to Markdown Conversion**: Uses Pandoc with custom Lua filters
- **Requirements Extraction**: Automatically identifies and extracts requirements
- **Document Structure Analysis**: Generates hierarchical document outlines
- **ASCII Diagrams**: Creates text-based structure visualizations
- **Quality Assurance**: Built-in validation and error checking

## 📁 Project Structure

```
DOCX_RTM_Automation_v1.0/
├── code/                   # Main application code
├── src/                   # Source modules
│   ├── core/             # Core functionality
│   ├── modules/          # Feature modules
│   └── extractors/       # Data extraction utilities
├── config/               # Configuration files
├── input/                # Input DOCX files
├── output/               # Generated outputs
├── logs/                 # Application logs
├── scripts/              # Utility scripts
├── docs/                 # Documentation
└── tests/                # Test files
```

## 🛠️ Installation

1. **Prerequisites**:
   ```bash
   # Install Pandoc
   # Windows: Download from https://pandoc.org/installing.html
   # macOS: brew install pandoc
   # Linux: sudo apt-get install pandoc

   # Install Python dependencies
   pip install -r requirements.txt
   ```

2. **Setup**:
   ```bash
   # Clone the repository
   git clone <repository-url>
   cd DOCX_RTM_Automation_v1.0

   # Run the setup script
   python project_update.py
   ```

## 🏃‍♂️ Quick Start

1. **Place your DOCX file** in the `input/` directory
2. **Run the main pipeline**:
   ```bash
   python code/main.py
   ```
3. **Check results** in the `output/` directory

## 📊 Output Files

- `*.md` - Converted Markdown with TOC and section numbering
- `*_outline.yaml` - Document structure hierarchy
- `*_requirements.yaml` - Extracted requirements
- `*_structure.txt` - ASCII structure diagram

## 🔧 Configuration

Edit `config/paths.yaml` to customize:
- Input/output directories
- Pandoc conversion options
- Requirements extraction patterns
- Output formats

## 🐛 Troubleshooting

### Common Issues

1. **Pandoc not found**: Ensure Pandoc is installed and in PATH
2. **TOC depth errors**: TOC depth is automatically limited to 6 (Pandoc maximum)
3. **Lua filter errors**: Check if Lua filters exist in `config/` directory

### Debug Mode

Enable debug logging by setting the log level in your script:
```python
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review the logs in `logs/` for error details

---

*Last updated: {datetime.now().strftime("%Y-%m-%d")}*
"""

        readme_path = self.project_root / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        self.print_status("SUCCESS", "Created comprehensive README.md")

        # Create requirements.txt
        requirements_content = """# DOCX RTM Automation Requirements
# Core dependencies for the automation pipeline

# Document processing
pandoc>=2.19
python-docx>=0.8.11

# Data processing
PyYAML>=6.0
lxml>=4.9.0

# Utilities
pathlib>=1.0.1
argparse>=1.4.0

# Development (optional)
pytest>=7.0.0
black>=22.0.0
flake8>=4.0.0

# Documentation (optional)
sphinx>=4.5.0
sphinx-rtd-theme>=1.0.0
"""

        req_path = self.project_root / "requirements.txt"
        with open(req_path, "w", encoding="utf-8") as f:
            f.write(requirements_content)

        self.print_status("SUCCESS", "Created requirements.txt")

    def create_github_files(self):
        """Create GitHub-specific files"""
        self.print_header("GITHUB REPOSITORY PREPARATION")

        # Create .gitignore
        gitignore_content = """# DOCX RTM Automation - Git Ignore File

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Project specific
logs/*.log
output/*.md
output/*.yaml
output/*.txt
output/*.json
*.backup
*.bak*
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
temp/
tmp/
*.tmp

# Documentation builds
docs/_build/
site/

# Test artifacts
.pytest_cache/
.coverage
htmlcov/

# Environment
.env
.env.local
"""

        gitignore_path = self.project_root / ".gitignore"
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(gitignore_content)

        self.print_status("SUCCESS", "Created .gitignore")

        # Create LICENSE
        license_content = """MIT License

Copyright (c) 2024 DOCX RTM Automation Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

        license_path = self.project_root / "LICENSE"
        with open(license_path, "w", encoding="utf-8") as f:
            f.write(license_content)

        self.print_status("SUCCESS", "Created LICENSE file")

    def run_comprehensive_tests(self):
        """Run comprehensive system tests"""
        self.print_header("COMPREHENSIVE SYSTEM TESTING")

        test_results = {
            "config_valid": False,
            "main_script_runs": False,
            "pandoc_available": False,
            "directories_exist": False,
        }

        # Test 1: Configuration validity
        try:
            config_path = self.project_root / "global_config.yaml"
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    yaml.safe_load(f)  # Test if it's valid YAML
                test_results["config_valid"] = True
                self.print_status("SUCCESS", "global_config.yaml is valid YAML")
            else:
                self.print_status("ERROR", "global_config.yaml missing")
                self.issues_found.append("global_config.yaml missing")
        except Exception as e:
            self.print_status("ERROR", f"global_config.yaml validation failed: {e}")
            self.issues_found.append(f"global_config.yaml validation error: {e}")

        # Test 2: Pandoc availability
        try:
            result = subprocess.run(
                ["pandoc", "--version"], capture_output=True, text=True, check=True
            )
            test_results["pandoc_available"] = True
            version = result.stdout.split("\n")[0]
            self.print_status("SUCCESS", f"Pandoc available: {version}")
        except Exception:
            self.print_status("ERROR", "Pandoc not available in PATH")

        # Test 3: Directory structure
        required_dirs = ["code", "config", "input", "output", "logs"]
        all_exist = all((self.project_root / d).exists() for d in required_dirs)
        test_results["directories_exist"] = all_exist

        if all_exist:
            self.print_status("SUCCESS", "All required directories exist")
        else:
            missing = [d for d in required_dirs if not (self.project_root / d).exists()]
            self.print_status("ERROR", f"Missing directories: {missing}")

        # Test 4: Main script syntax
        try:
            main_script = self.project_root / "code" / "main.py"
            if main_script.exists():
                with open(main_script, "r", encoding="utf-8") as f:
                    compile(f.read(), main_script, "exec")
                test_results["main_script_runs"] = True
                self.print_status("SUCCESS", "Main script syntax is valid")
            else:
                self.print_status("ERROR", "Main script not found")
        except SyntaxError as e:
            self.print_status("ERROR", f"Main script syntax error: {e}")
        except Exception as e:
            self.print_status("ERROR", f"Main script test failed: {e}")

        return test_results

    def generate_update_report(self, test_results):
        """Generate comprehensive update report"""
        self.print_header("PROJECT UPDATE REPORT", Colors.GREEN)

        report = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": len(self.issues_found),
            "fixes_applied": len(self.fixes_applied),
            "test_results": test_results,
            "issues_list": self.issues_found,
            "fixes_list": self.fixes_applied,
        }

        # Save JSON report
        report_path = (
            self.project_root
            / "logs"
            / f"update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print(f"\n{Colors.GREEN}📊 UPDATE SUMMARY{Colors.ENDC}")
        print(f"   Issues Found: {len(self.issues_found)}")
        print(f"   Fixes Applied: {len(self.fixes_applied)}")
        print(f"   Tests Passed: {sum(test_results.values())}/{len(test_results)}")
        print(f"   Report Saved: {report_path}")

        # Print recommendations
        print(f"\n{Colors.CYAN}💡 NEXT STEPS{Colors.ENDC}")
        if all(test_results.values()):
            print("   ✅ Project is ready for production use")
            print("   ✅ All tests passed - you can run: python code/main.py")
            print("   ✅ Consider initializing git repository: git init")
        else:
            print("   ⚠️  Some tests failed - review the issues above")
            print("   ⚠️  Fix remaining issues before production use")

        return report

    def run_full_update(self):
        """Run the complete project update process"""
        self.print_header("DOCX RTM AUTOMATION - FULL PROJECT UPDATE", Colors.PURPLE)

        try:
            # Phase 1: Structure Analysis
            existing, missing, structure = self.analyze_project_structure()

            # Phase 2: Create Missing Directories
            if missing:
                self.create_missing_directories(missing, structure)

            # Phase 3: Python Code Analysis & Fixes
            issues = self.scan_python_files()
            self.fix_common_python_issues(issues)

            # Phase 4: Configuration Updates
            self.update_configuration_files()

            # Phase 5: Documentation
            self.create_project_documentation()

            # Phase 6: GitHub Preparation
            self.create_github_files()

            # Phase 7: System Testing
            test_results = self.run_comprehensive_tests()

            # Phase 8: Generate Report
            report = self.generate_update_report(test_results)

            return report

        except Exception as e:
            self.print_status("ERROR", f"Update process failed: {e}")
            raise


def main():
    """Main execution function"""
    updater = ProjectUpdater()

    try:
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║            DOCX RTM AUTOMATION PROJECT UPDATER          ║")
        print("║                  Complete Refactor & Fix                ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")

        updater.run_full_update()

        print(
            f"\n{Colors.GREEN}{Colors.BOLD}🎉 PROJECT UPDATE COMPLETED SUCCESSFULLY! 🎉{Colors.ENDC}"
        )

        return 0

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Update process interrupted by user{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}❌ Update process failed: {e}{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
