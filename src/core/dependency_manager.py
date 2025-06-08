#!/usr/bin/env python3
"""
Dependency Manager for RTM Automation

This module validates and manages external dependencies required for RTM generation,
including Python modules and Lua filters.
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)


class DependencyManager:
    """Manages verification and loading of project dependencies."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration dictionary."""
        self.config = config
        self.errors = []
        self.warnings = []

    def check_pandoc(self) -> bool:
        """Check if pandoc is installed and available in PATH."""
        import shutil

        pandoc_path = shutil.which("pandoc")
        if not pandoc_path:
            self.errors.append("Pandoc not found in PATH. Please install Pandoc.")
            return False

        logger.info(f"Found Pandoc at: {pandoc_path}")
        return True

    def check_lua_filters(self) -> bool:
        """Check if needed Lua filters exist."""
        filters_ok = True

        # Check configured filter if specified
        lua_filter = self.config.get("pandoc_options", {}).get("lua_filter")
        if lua_filter:
            filter_path = Path(lua_filter)
            if not filter_path.exists():
                self.warnings.append(f"Configured Lua filter not found: {filter_path}")
                filters_ok = False
            else:
                logger.info(f"Found configured Lua filter: {filter_path}")

        # Check default filters directory
        filters_dir = Path("config/filters")
        if not filters_dir.exists():
            self.warnings.append(f"Default filters directory not found: {filters_dir}")
        else:
            # Check for rtm_filter.lua
            rtm_filter = filters_dir / "rtm_filter.lua"
            if not rtm_filter.exists():
                self.warnings.append(f"Default RTM Lua filter not found: {rtm_filter}")
                filters_ok = False
            else:
                logger.info(f"Found default RTM Lua filter: {rtm_filter}")

        return filters_ok

    def check_pandoc_modules(self) -> bool:
        """Check if required Pandoc Python modules exist."""
        modules_ok = True
        pandoc_modules = self.config.get("pandoc_modules", {})

        for module_name, module_path in pandoc_modules.items():
            if not module_path:
                continue

            path = Path(module_path)
            if not path.exists():
                self.warnings.append(
                    f"Pandoc module '{module_name}' not found at {path}"
                )
                modules_ok = False
            else:
                logger.info(f"Found Pandoc module '{module_name}' at {path}")

        # Check for specific module in scripts/modules
        pandoc_integration_path = Path("scripts/modules/pandoc_integration.py")
        if not pandoc_integration_path.exists():
            self.warnings.append(
                f"Pandoc integration module not found: {pandoc_integration_path}"
            )
        else:
            logger.info(f"Found Pandoc integration module: {pandoc_integration_path}")

        return modules_ok

    def is_package_available(self, package_name):
        """Check if a package is available in the current environment using direct import."""
        # The most reliable way to check if a package is actually usable
        try:
            # Try directly importing the package (this is what matters for actual usage)
            __import__(package_name)
            return True
        except ImportError:
            return False

    def check_required_packages(self, packages: List[str]) -> bool:
        """Check if required Python packages are installed."""
        missing_packages = []

        for package in packages:
            # For pyyaml, we need to check for 'yaml' which is what you actually import
            if package == "pyyaml":
                actual_import_name = "yaml"
            else:
                actual_import_name = package

            if self.is_package_available(actual_import_name):
                logger.info(f"Package '{package}' is available")
            else:
                missing_packages.append(package)
                self.warnings.append(f"Required package '{package}' is not installed")

        if missing_packages:
            packages_str = " ".join(missing_packages)
            self.warnings.append(
                f"To install missing packages, run: pip install {packages_str}"
            )
            return False

        return True

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Validate all dependencies and return status with error/warning messages."""
        # Reset errors and warnings
        self.errors = []
        self.warnings = []

        # Print diagnostic information
        logger.debug(f"Python executable: {sys.executable}")
        logger.debug(f"Python version: {sys.version}")

        # First check Python packages since they're the most critical
        packages_ok = self.check_required_packages(["pyyaml", "markdown"])

        # Only check other dependencies if they're needed based on config
        pandoc_ok = True

        # Check for optional Pandoc-related dependencies if relevant settings exist
        if any(
            key in self.config
            for key in ["pandoc_options", "pandoc_modules", "pandoc_path"]
        ):
            pandoc_ok = self.check_pandoc()
            if pandoc_ok:
                self.check_lua_filters()
                self.check_pandoc_modules()

        # Overall status - packages must be available for the system to work
        all_ok = packages_ok

        return all_ok, self.errors, self.warnings


# Helper functions
def find_file_in_paths(filename: str, search_paths: List[Path]) -> Optional[Path]:
    """Find a file in a list of search paths."""
    for path in search_paths:
        file_path = path / filename
        if file_path.exists():
            return file_path
    return None


def validate_dependencies(config: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
    """Validate all dependencies based on config."""
    manager = DependencyManager(config)
    return manager.validate_all()


# Main function for testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"sys.path: {sys.path}")

    try:
        import yaml

        print(f"PyYAML is installed at: {yaml.__file__}")
    except ImportError:
        print("PyYAML is not installed or importable")

    # Test configuration
    test_config = {
        "pandoc_options": {"lua_filter": "config/filters/rtm_filter.lua"},
        "pandoc_modules": {
            "init": "scripts/modules/pandoc_init.py",
            "main": "scripts/modules/pandoc_integration.py",
            "runner": "scripts/modules/pandoc_runner.py",
        },
    }

    # Run validation
    ok, errors, warnings = validate_dependencies(test_config)

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if ok:
        print("\nAll critical dependencies are available.")
        sys.exit(0)
    else:
        print("\nSome dependencies are missing or misconfigured.")
        sys.exit(1)
