#!/usr/bin/env python3
"""
RTM Extension Management and Monitoring System
Manages and monitors all active extensions, plugins, and integrations
"""

import os
import sys
import json
import time
import logging
import importlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Extension:
    """Represents a single extension in the RTM system."""

    def __init__(self, name: str, path: str, extension_type: str = "unknown"):
        self.name = name
        self.path = path
        self.extension_type = extension_type
        self.status = "inactive"
        self.last_used = None
        self.error_count = 0
        self.config = {}
        self.dependencies = []
        self.description = ""
        self.version = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert extension to dictionary for serialization."""
        return {
            "name": self.name,
            "path": self.path,
            "type": self.extension_type,
            "status": self.status,
            "last_used": self.last_used,
            "error_count": self.error_count,
            "config": self.config,
            "dependencies": self.dependencies,
            "description": self.description,
            "version": self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Extension':
        """Create extension from dictionary."""
        ext = cls(data["name"], data["path"], data.get("type", "unknown"))
        ext.status = data.get("status", "inactive")
        ext.last_used = data.get("last_used")
        ext.error_count = data.get("error_count", 0)
        ext.config = data.get("config", {})
        ext.dependencies = data.get("dependencies", [])
        ext.description = data.get("description", "")
        ext.version = data.get("version", "unknown")
        return ext


class ExtensionManager:
    """Main extension management system."""

    def __init__(self, config_path: str = "extension_config.json"):
        self.config_path = config_path
        self.extensions: Dict[str, Extension] = {}
        self.monitoring_active = False
        self.load_config()
        self.discover_extensions()

    def load_config(self):
        """Load extension configuration from file."""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

                for ext_data in config_data.get("extensions", []):
                    ext = Extension.from_dict(ext_data)
                    self.extensions[ext.name] = ext

                logger.info(f"Loaded {len(self.extensions)} extensions from config")
            else:
                logger.info("No extension config found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading extension config: {e}")

    def save_config(self):
        """Save extension configuration to file."""
        try:
            config_data = {
                "last_updated": datetime.now().isoformat(),
                "extensions": [ext.to_dict() for ext in self.extensions.values()]
            }

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"Saved configuration for {len(self.extensions)} extensions")
        except Exception as e:
            logger.error(f"Error saving extension config: {e}")

    def discover_extensions(self):
        """Automatically discover extensions in the system."""
        print("🔍 Discovering RTM Extensions...")

        # Define extension categories and their patterns
        extension_patterns = {
            "parsers": ["*parser*.py", "*parsing*.py"],
            "generators": ["*generator*.py", "*builder*.py"],
            "analyzers": ["*analyzer*.py", "*analysis*.py"],
            "converters": ["*converter*.py", "*transform*.py"],
            "integrations": ["*integration*.py", "*connector*.py"],
            "ai_modules": ["*ai*.py", "*ariana*.py", "*ml*.py"],
            "quality_tools": ["*quality*.py", "*check*.py", "*verify*.py"],
            "utilities": ["*util*.py", "*helper*.py", "*tool*.py"],
            "agents": ["agent*.py", "*agent*.py"],
            "workflows": ["*pipeline*.py", "*workflow*.py", "*process*.py"]
        }

        discovered_count = 0

        # Search current directory and subdirectories
        for category, patterns in extension_patterns.items():
            for pattern in patterns:
                for file_path in Path(".").rglob(pattern):
                    if file_path.is_file() and file_path.suffix == ".py":
                        ext_name = file_path.stem

                        # Skip if already registered
                        if ext_name in self.extensions:
                            continue

                        # Create new extension
                        extension = Extension(ext_name, str(file_path), category)
                        extension.description = self._extract_description(file_path)
                        extension.version = self._extract_version(file_path)
                        extension.dependencies = self._extract_dependencies(file_path)

                        self.extensions[ext_name] = extension
                        discovered_count += 1

                        print(f"   📄 Found {category}: {ext_name}")

        # Discover Ariana AI extensions
        ariana_dir = Path(".ariana")
        if ariana_dir.exists():
            for config_file in ariana_dir.glob("*.json"):
                ext_name = f"ariana_{config_file.stem}"
                if ext_name not in self.extensions:
                    extension = Extension(ext_name, str(config_file), "ai_config")
                    extension.description = f"Ariana AI configuration: {config_file.stem}"
                    extension.status = "active"
                    self.extensions[ext_name] = extension
                    discovered_count += 1
                    print(f"   🤖 Found AI config: {ext_name}")

        # Discover GitHub workflows
        github_dir = Path(".github/workflows")
        if github_dir.exists():
            for workflow_file in github_dir.glob("*.yml"):
                ext_name = f"workflow_{workflow_file.stem}"
                if ext_name not in self.extensions:
                    extension = Extension(ext_name, str(workflow_file), "github_workflow")
                    extension.description = f"GitHub workflow: {workflow_file.stem}"
                    self.extensions[ext_name] = extension
                    discovered_count += 1
                    print(f"   ⚙️ Found workflow: {ext_name}")

        print(f"   ✅ Discovered {discovered_count} new extensions")

        if discovered_count > 0:
            self.save_config()

    def _extract_description(self, file_path: Path) -> str:
        """Extract description from file docstring."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for module docstring
            import ast
            tree = ast.parse(content)
            if (tree.body and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)):
                return tree.body[0].value.value.split('\n')[0].strip()
        except Exception:
            pass

        return f"RTM extension: {file_path.stem}"

    def _extract_version(self, file_path: Path) -> str:
        """Extract version information from file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for version patterns
            import re
            version_patterns = [
                r'__version__\s*=\s*["\']([^"\']+)["\']',
                r'VERSION\s*=\s*["\']([^"\']+)["\']',
                r'version\s*=\s*["\']([^"\']+)["\']'
            ]

            for pattern in version_patterns:
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
        except Exception:
            pass

        return "1.0.0"

    def _extract_dependencies(self, file_path: Path) -> List[str]:
        """Extract dependencies from import statements."""
        dependencies = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            import ast
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module.split('.')[0])
        except Exception:
            pass

        # Filter common standard library modules
        stdlib_modules = {'os', 'sys', 'json', 'time', 'datetime', 're', 'pathlib', 'logging'}
        return [dep for dep in set(dependencies) if dep not in stdlib_modules]

    def get_extension_status(self, name: str) -> Dict[str, Any]:
        """Get detailed status of a specific extension."""
        if name not in self.extensions:
            return {"error": "Extension not found"}

        ext = self.extensions[name]
        status = ext.to_dict()

        # Add runtime information
        status["file_exists"] = Path(ext.path).exists()
        status["file_size"] = Path(ext.path).stat().st_size if Path(ext.path).exists() else 0
        status["last_modified"] = datetime.fromtimestamp(
            Path(ext.path).stat().st_mtime
        ).isoformat() if Path(ext.path).exists() else None

        # Check if dependencies are available
        status["dependencies_available"] = self._check_dependencies(ext.dependencies)

        return status

    def _check_dependencies(self, dependencies: List[str]) -> Dict[str, bool]:
        """Check if dependencies are available."""
        results = {}
        for dep in dependencies:
            try:
                importlib.import_module(dep)
                results[dep] = True
            except ImportError:
                results[dep] = False
        return results

    def activate_extension(self, name: str) -> bool:
        """Activate an extension."""
        if name not in self.extensions:
            logger.error(f"Extension '{name}' not found")
            return False

        try:
            ext = self.extensions[name]
            ext.status = "active"
            ext.last_used = datetime.now().isoformat()

            # For Python modules, try to import them
            if ext.extension_type in ["parsers", "generators", "analyzers"]:
                if ext.path.endswith('.py'):
                    spec = importlib.util.spec_from_file_location(name, ext.path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

            logger.info(f"Activated extension: {name}")
            self.save_config()
            return True

        except Exception as e:
            ext.error_count += 1
            ext.status = "error"
            logger.error(f"Error activating extension '{name}': {e}")
            self.save_config()
            return False

    def deactivate_extension(self, name: str) -> bool:
        """Deactivate an extension."""
        if name not in self.extensions:
            logger.error(f"Extension '{name}' not found")
            return False

        ext = self.extensions[name]
        ext.status = "inactive"
        logger.info(f"Deactivated extension: {name}")
        self.save_config()
        return True

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all extensions."""
        summary = {
            "total_extensions": len(self.extensions),
            "by_type": {},
            "by_status": {},
            "active_extensions": [],
            "error_extensions": [],
            "recent_activity": []
        }

        for ext in self.extensions.values():
            # Count by type
            ext_type = ext.extension_type
            summary["by_type"][ext_type] = summary["by_type"].get(ext_type, 0) + 1

            # Count by status
            status = ext.status
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

            # Track active and error extensions
            if ext.status == "active":
                summary["active_extensions"].append(ext.name)
            elif ext.status == "error":
                summary["error_extensions"].append(ext.name)

            # Track recent activity
            if ext.last_used:
                summary["recent_activity"].append({
                    "name": ext.name,
                    "last_used": ext.last_used,
                    "type": ext.extension_type
                })

        # Sort recent activity
        summary["recent_activity"].sort(
            key=lambda x: x["last_used"] or "1970-01-01",
            reverse=True
        )
        summary["recent_activity"] = summary["recent_activity"][:10]  # Top 10

        return summary

    def monitor_extensions(self, duration: int = 60):
        """Monitor extension activity for a specified duration."""
        print(f"🔍 Monitoring extensions for {duration} seconds...")
        self.monitoring_active = True

        start_time = time.time()
        while time.time() - start_time < duration and self.monitoring_active:
            # Check for file changes
            for ext in self.extensions.values():
                if Path(ext.path).exists():
                    current_mtime = Path(ext.path).stat().st_mtime
                    # Implementation would track file modifications

            time.sleep(5)  # Check every 5 seconds

        print("✅ Monitoring complete")

    def generate_report(self, output_path: str = "extension_report.json"):
        """Generate comprehensive extension report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "extensions": {}
        }

        for name, ext in self.extensions.items():
            report["extensions"][name] = self.get_extension_status(name)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"📊 Extension report saved to: {output_path}")
        return report


def main():
    """Main function to run extension management."""
    print("🔧 RTM Extension Management System")
    print("=" * 50)

    manager = ExtensionManager()

    # Show summary
    summary = manager.get_summary()
    print(f"\n📊 Extension Summary:")
    print(f"   Total Extensions: {summary['total_extensions']}")
    print(f"   Active Extensions: {len(summary['active_extensions'])}")
    print(f"   Error Extensions: {len(summary['error_extensions'])}")

    print(f"\n📈 Extensions by Type:")
    for ext_type, count in summary['by_type'].items():
        print(f"   {ext_type}: {count}")

    print(f"\n⚡ Extensions by Status:")
    for status, count in summary['by_status'].items():
        print(f"   {status}: {count}")

    if summary['active_extensions']:
        print(f"\n✅ Active Extensions:")
        for ext_name in summary['active_extensions'][:10]:
            print(f"   - {ext_name}")

    if summary['error_extensions']:
        print(f"\n❌ Extensions with Errors:")
        for ext_name in summary['error_extensions']:
            print(f"   - {ext_name}")

    # Generate report
    report = manager.generate_report()

    print(f"\n🎯 Extension Management Commands:")
    print(f"   python extension_manager.py --activate <name>")
    print(f"   python extension_manager.py --deactivate <name>")
    print(f"   python extension_manager.py --status <name>")
    print(f"   python extension_manager.py --monitor <seconds>")
    print(f"   python extension_manager.py --report")

    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        manager = ExtensionManager()

        if sys.argv[1] == "--activate" and len(sys.argv) > 2:
            result = manager.activate_extension(sys.argv[2])
            print(f"✅ Activated: {sys.argv[2]}" if result else f"❌ Failed to activate: {sys.argv[2]}")

        elif sys.argv[1] == "--deactivate" and len(sys.argv) > 2:
            result = manager.deactivate_extension(sys.argv[2])
            print(f"✅ Deactivated: {sys.argv[2]}" if result else f"❌ Failed to deactivate: {sys.argv[2]}")

        elif sys.argv[1] == "--status" and len(sys.argv) > 2:
            status = manager.get_extension_status(sys.argv[2])
            print(json.dumps(status, indent=2))

        elif sys.argv[1] == "--monitor" and len(sys.argv) > 2:
            duration = int(sys.argv[2])
            manager.monitor_extensions(duration)

        elif sys.argv[1] == "--report":
            manager.generate_report()

        else:
            print("Invalid command. Run without arguments to see available commands.")
    else:
        sys.exit(main())
