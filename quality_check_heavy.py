#!/usr/bin/env python3
"""
Heavy Code Quality Check - Comprehensive analysis
Complete project analysis with detailed reporting
"""

import subprocess
import sys
import json
from pathlib import Path
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class HeavyQualityChecker:
    """Comprehensive code quality checker."""

    def __init__(self):
        self.results = {
            "flake8": {"files": 0, "issues": 0, "details": []},
            "structure": {"score": 0, "issues": []},
            "dependencies": {"available": 0, "missing": 0, "details": []},
            "coverage": {"files_with_docstrings": 0, "total_files": 0}
        }

    def run_comprehensive_flake8(self):
        """Run comprehensive flake8 analysis."""
        print("🔍 Running comprehensive flake8 analysis...")

        # Strict configuration for heavy check
        heavy_config = [
            "--max-line-length=88",
            "--extend-ignore=E203,W503",  # Only ignore Black conflicts
            "--statistics",
            "--count",
            "--exclude=.git,__pycache__,.venv,venv,build,dist,.ariana"
        ]

        # Find all Python files
        python_files = list(Path(".").glob("**/*.py"))
        python_files = [
            f for f in python_files
            if not any(exclude in str(f) for exclude in ['.venv', '__pycache__', '.git', '.ariana'])
        ]

        total_issues = 0

        for py_file in python_files:
            try:
                result = subprocess.run(
                    ["flake8"] + heavy_config + [str(py_file)],
                    capture_output=True, text=True, timeout=60
                )

                if result.stdout.strip():
                    file_issues = result.stdout.strip().split('\n')
                    total_issues += len(file_issues)
                    self.results["flake8"]["details"].extend([
                        {"file": str(py_file), "issue": issue}
                        for issue in file_issues
                    ])

            except Exception as e:
                logger.warning(f"Error checking {py_file}: {e}")

        self.results["flake8"]["files"] = len(python_files)
        self.results["flake8"]["issues"] = total_issues

        print(f"   Checked {len(python_files)} files, found {total_issues} issues")

    def check_project_structure(self):
        """Analyze project structure quality."""
        print("🏗️ Analyzing project structure...")

        expected_structure = {
            "directories": ["input", "output", "src", "tests"],
            "core_files": [
                "enhance_document_parsing.py",
                "digital_twin_parser.py",
                "verify_system_status.py"
            ],
            "config_files": ["requirements.txt", "README.md"]
        }

        score = 0
        max_score = 0
        issues = []

        # Check directories
        for directory in expected_structure["directories"]:
            max_score += 1
            if Path(directory).exists():
                score += 1
            else:
                issues.append(f"Missing directory: {directory}")

        # Check core files
        for file_path in expected_structure["core_files"]:
            max_score += 1
            if Path(file_path).exists():
                score += 1
            else:
                issues.append(f"Missing core file: {file_path}")

        # Check config files
        for file_path in expected_structure["config_files"]:
            max_score += 1
            if Path(file_path).exists():
                score += 1
            else:
                issues.append(f"Missing config file: {file_path}")

        structure_score = int((score / max_score) * 100) if max_score > 0 else 0
        self.results["structure"]["score"] = structure_score
        self.results["structure"]["issues"] = issues

        print(f"   Structure score: {structure_score}/100")

    def check_dependencies(self):
        """Check dependency availability and versions."""
        print("🔧 Checking dependencies...")

        required_deps = {
            "markdown": "Markdown processing",
            "yaml": "YAML file handling",
            "json": "JSON processing",
            "pathlib": "Path operations"
        }

        optional_deps = {
            "docx": "Word document processing",
            "matplotlib": "Visualization",
            "numpy": "Numerical operations"
        }

        available = 0
        missing = 0
        details = []

        # Check required dependencies
        for dep_name, description in required_deps.items():
            try:
                __import__(dep_name)
                available += 1
                details.append({"name": dep_name, "status": "available", "type": "required"})
            except ImportError:
                missing += 1
                details.append({"name": dep_name, "status": "missing", "type": "required"})

        # Check optional dependencies
        for dep_name, description in optional_deps.items():
            try:
                __import__(dep_name)
                details.append({"name": dep_name, "status": "available", "type": "optional"})
            except ImportError:
                details.append({"name": dep_name, "status": "missing", "type": "optional"})

        self.results["dependencies"]["available"] = available
        self.results["dependencies"]["missing"] = missing
        self.results["dependencies"]["details"] = details

        print(f"   Required deps: {available} available, {missing} missing")

    def check_documentation_coverage(self):
        """Check documentation coverage."""
        print("📚 Checking documentation coverage...")

        python_files = list(Path(".").glob("**/*.py"))
        python_files = [
            f for f in python_files
            if not any(exclude in str(f) for exclude in ['.venv', '__pycache__', '.git', '.ariana'])
        ]

        files_with_docstrings = 0

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple check for module docstring
                if '"""' in content[:500] or "'''" in content[:500]:
                    files_with_docstrings += 1

            except Exception:
                continue

        self.results["coverage"]["files_with_docstrings"] = files_with_docstrings
        self.results["coverage"]["total_files"] = len(python_files)

        coverage_percent = int((files_with_docstrings / len(python_files)) * 100) if python_files else 0
        print(f"   Documentation coverage: {coverage_percent}% ({files_with_docstrings}/{len(python_files)} files)")

    def generate_comprehensive_report(self):
        """Generate and save comprehensive report."""
        print("\n📊 Generating comprehensive report...")

        # Calculate overall quality score
        flake8_score = max(0, 100 - self.results["flake8"]["issues"] * 2)
        structure_score = self.results["structure"]["score"]
        deps_score = int((self.results["dependencies"]["available"] /
                         (self.results["dependencies"]["available"] + self.results["dependencies"]["missing"])) * 100) \
                         if (self.results["dependencies"]["available"] + self.results["dependencies"]["missing"]) > 0 else 100

        doc_score = int((self.results["coverage"]["files_with_docstrings"] /
                        self.results["coverage"]["total_files"]) * 100) \
                        if self.results["coverage"]["total_files"] > 0 else 0

        overall_score = int((flake8_score + structure_score + deps_score + doc_score) / 4)

        # Create comprehensive report
        report = {
            "project": "DOCX RTM Automation v1.0",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_score": overall_score,
            "component_scores": {
                "code_quality": flake8_score,
                "structure": structure_score,
                "dependencies": deps_score,
                "documentation": doc_score
            },
            "detailed_results": self.results,
            "recommendations": self._generate_recommendations()
        }

        # Save report
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        report_file = output_dir / "comprehensive_quality_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        # Print summary
        self._print_summary(report)

        return report

    def _generate_recommendations(self):
        """Generate improvement recommendations."""
        recommendations = []

        if self.results["flake8"]["issues"] > 50:
            recommendations.append("Consider running 'black .' to auto-fix many formatting issues")

        if self.results["structure"]["score"] < 80:
            recommendations.append("Improve project structure by adding missing directories/files")

        if self.results["dependencies"]["missing"] > 0:
            recommendations.append("Install missing required dependencies")

        if self.results["coverage"]["files_with_docstrings"] < self.results["coverage"]["total_files"] * 0.5:
            recommendations.append("Add docstrings to improve documentation coverage")

        return recommendations

    def _print_summary(self, report):
        """Print comprehensive summary."""
        print("\n" + "="*60)
        print("COMPREHENSIVE CODE QUALITY REPORT")
        print("="*60)

        print(f"Overall Quality Score: {report['overall_score']}/100")
        print(f"Timestamp: {report['timestamp']}")

        print(f"\nComponent Scores:")
        for component, score in report['component_scores'].items():
            print(f"  {component.replace('_', ' ').title()}: {score}/100")

        print(f"\nKey Metrics:")
        print(f"  Files checked: {self.results['flake8']['files']}")
        print(f"  Issues found: {self.results['flake8']['issues']}")
        print(f"  Structure score: {self.results['structure']['score']}/100")
        print(f"  Dependencies available: {self.results['dependencies']['available']}")

        if report['recommendations']:
            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")

        print(f"\nDetailed report saved to: output/comprehensive_quality_report.json")
        print("="*60)

def main():
    """Run heavy quality check."""
    print("🔄 Heavy Code Quality Check")
    print("=" * 40)
    print("⏱️  This may take a few minutes...")

    start_time = time.time()

    checker = HeavyQualityChecker()

    # Run all checks
    checker.run_comprehensive_flake8()
    checker.check_project_structure()
    checker.check_dependencies()
    checker.check_documentation_coverage()

    # Generate report
    report = checker.generate_comprehensive_report()

    duration = time.time() - start_time
    print(f"\n⏱️ Heavy check completed in {duration:.1f} seconds")

    # Return exit code based on overall score
    return 0 if report['overall_score'] >= 70 else 1

if __name__ == "__main__":
    sys.exit(main())
