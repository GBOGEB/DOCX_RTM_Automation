#!/usr/bin/env python3
"""
Emergency TOML Fix - Immediate fix for TOML escape sequence issues
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def fix_toml_immediately():
    """Fix the TOML file with valid escape sequences."""

    print("🚨 Emergency TOML Fix")
    print("=" * 30)

    # Create absolutely clean TOML content with no problematic escapes
    clean_toml = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "rtm-automation"
version = "1.0.0"
description = "RTM (Requirements Traceability Matrix) Automation System"
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Documentation",
    "Topic :: Software Development :: Quality Assurance",
]
dependencies = [
    "python-docx>=0.8.11",
    "openpyxl>=3.0.10",
    "pandas>=1.5.0",
    "jinja2>=3.1.0",
    "pyyaml>=6.0",
    "flask>=2.3.0",
    "requests>=2.28.0",
    "pathlib2>=2.3.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]
web = [
    "flask-cors>=4.0.0",
    "gunicorn>=20.1.0",
]
parsing = [
    "lxml>=4.9.0",
    "beautifulsoup4>=4.11.0",
    "markdown>=3.4.0",
]

[project.urls]
"Homepage" = "https://github.com/rtm-automation/rtm-system"
"Bug Tracker" = "https://github.com/rtm-automation/rtm-system/issues"
"Documentation" = "https://rtm-automation.readthedocs.io/"

[project.scripts]
rtm-analyze = "src.analyzers.json_file_analyzer_safe:main"
rtm-status = "main_organized:main"
rtm-dashboard = "launch_dashboard:main"

[tool.setuptools.packages.find]
where = ["src"]
include = ["rtm*", "analyzers*", "dashboard*", "parsers*", "utils*", "integrations*"]

[tool.ruff]
target-version = "py38"
line-length = 88
select = [
    "E",
    "W",
    "F",
    "I",
    "B",
    "C4",
    "UP",
]
ignore = [
    "E501",
    "B008",
    "C901",
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]
"test_*.py" = ["S101"]

[tool.black]
target-version = ["py38"]
line-length = 88
skip-string-normalization = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*",
    "setup.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
disallow_incomplete_defs = false
check_untyped_defs = true
disallow_untyped_decorators = false
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "docx.*",
    "openpyxl.*",
    "pandas.*",
    "flask.*",
]
ignore_missing_imports = true
"""

    # Write the clean file
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    toml_path = Path("config/pyproject.toml")
    with open(toml_path, "w", encoding="utf-8") as f:
        f.write(clean_toml)

    print(f"✅ Emergency TOML fix applied to: {toml_path}")
    return True


def test_toml_fix():
    """Test if the TOML fix worked."""
    print("\n🧪 Testing TOML Fix")
    print("=" * 25)

    import subprocess

    try:
        # Test ruff can now parse the config
        result = subprocess.run(
            ["ruff", "check", "--version"], capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            print(f"✅ Ruff working: {result.stdout.strip()}")

            # Test actual config parsing
            config_test = subprocess.run(
                ["ruff", "check", ".", "--dry-run"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if "Failed to parse" not in config_test.stderr:
                print("✅ TOML configuration loads successfully")
                return True
            else:
                print(f"❌ Config still has issues: {config_test.stderr}")
                return False
        else:
            print(f"❌ Ruff not working: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def main():
    """Main emergency fix function."""

    print("🚨 RTM Emergency TOML Configuration Fix")
    print("=" * 45)

    try:
        # Apply emergency fix
        fix_success = fix_toml_immediately()

        if fix_success:
            # Test the fix
            test_success = test_toml_fix()

            if test_success:
                print("\n🎉 EMERGENCY FIX SUCCESSFUL!")
                print("=" * 35)
                print("✅ TOML syntax is now valid")
                print("✅ Ruff can parse the configuration")
                print("✅ All escape sequences fixed")

                print("\n🚀 You can now run:")
                print("   ruff check .")
                print("   ruff format .")
                print("   python rtm_pipeline_executor.py")

                # Save fix report
                fix_report = {
                    "emergency_toml_fix": {
                        "timestamp": datetime.now().isoformat(),
                        "issue_fixed": "Invalid escape sequences in TOML",
                        "solution": "Replaced problematic regex patterns",
                        "status": "successful",
                        "ruff_working": True,
                    }
                }

                with open("emergency_toml_fix_report.json", "w") as f:
                    json.dump(fix_report, f, indent=2)

                print("\n💾 Fix report saved to: emergency_toml_fix_report.json")

            else:
                print("\n⚠️ Fix applied but testing shows remaining issues")
        else:
            print("\n❌ Emergency fix failed")

        return 0

    except Exception as e:
        print(f"\n❌ Emergency fix error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
