#!/usr/bin/env python3
"""
Code Quality Checker for DOCX RTM Automation Project

This script runs various code quality checks including flake8, and provides
a comprehensive report on code quality issues and suggestions for fixes.
"""

import sys
import subprocess
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CodeQualityChecker:
    """Code quality checker for the RTM Automation project."""

    def __init__(self, project_root=None):
        """Initialize the code quality checker."""
        self.project_root = (
            Path(project_root) if project_root else Path(__file__).parent
        )
        self.results = {}

    def run_flake8_check(self, target_files=None):
        """Run flake8 linting on Python files."""
        logger.info("Running flake8 code quality check...")

        # Define flake8 configuration
        flake8_config = [
            "--max-line-length=88",
            "--extend-ignore=E203,W503,E501",
            "--exclude=.git,__pycache__,.venv,venv,build,dist,.ariana",
            "--statistics",
            "--count",
        ]

        # Determine files to check
        if target_files is None:
            python_files = list(self.project_root.glob("**/*.py"))
            python_files = [
                f
                for f in python_files
                if not any(
                    exclude in str(f)
                    for exclude in [".venv", "__pycache__", ".git", ".ariana"]
                )
            ]
        else:
            python_files = [Path(f) for f in target_files]

        if not python_files:
            logger.warning("No Python files found to check")
            return {"status": "no_files", "issues": []}

        # Run flake8 on each file
        all_issues = []
        for py_file in python_files:
            try:
                cmd = ["flake8"] + flake8_config + [str(py_file)]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=self.project_root
                )

                if result.stdout.strip():
                    for line in result.stdout.strip().split("\n"):
                        if line.strip() and not line.startswith("Total"):
                            all_issues.append(
                                {
                                    "file": str(py_file),
                                    "issue": line.strip(),
                                    "severity": self._classify_flake8_issue(line),
                                }
                            )

            except FileNotFoundError:
                logger.error(
                    "flake8 not found. Make sure it's installed: pip install flake8"
                )
                return {"status": "error", "message": "flake8 not installed"}
            except Exception as e:
                logger.error("Error running flake8 on %s: %s", py_file, e)

        # Summarize results
        error_count = sum(1 for issue in all_issues if issue["severity"] == "error")
        warning_count = sum(1 for issue in all_issues if issue["severity"] == "warning")

        self.results["flake8"] = {
            "status": "completed",
            "files_checked": len(python_files),
            "total_issues": len(all_issues),
            "errors": error_count,
            "warnings": warning_count,
            "issues": all_issues,
        }

        logger.info(
            "Flake8 check completed: %d files, %d issues (%d errors, %d warnings)",
            len(python_files),
            len(all_issues),
            error_count,
            warning_count,
        )

        return self.results["flake8"]

    def _classify_flake8_issue(self, issue_line):
        """Classify flake8 issue as error or warning."""
        parts = issue_line.split(":")
        if len(parts) >= 4:
            error_code = parts[3].strip().split()[0]
            if error_code.startswith(("E", "F")):
                return "error"
            elif error_code.startswith("W"):
                return "warning"
        return "warning"

    def generate_report(self, output_file=None):
        """Generate a comprehensive code quality report."""
        if not self.results:
            logger.warning("No results to report. Run checks first.")
            return

        report = {
            "project": "DOCX RTM Automation v1.0",
            "summary": {},
            "detailed_results": self.results,
        }

        # Calculate summary statistics
        total_issues = 0
        total_errors = 0
        total_warnings = 0

        for check_results in self.results.values():
            if isinstance(check_results, dict) and "issues" in check_results:
                issues = check_results["issues"]
                total_issues += len(issues)

                for issue in issues:
                    if issue.get("severity") == "error":
                        total_errors += 1
                    elif issue.get("severity") == "warning":
                        total_warnings += 1

        report["summary"] = {
            "total_checks_run": len(self.results),
            "total_issues": total_issues,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "quality_score": max(0, 100 - (total_errors * 5) - (total_warnings * 2)),
        }

        # Save report
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)

            logger.info("Code quality report saved to: %s", output_path)

        # Print summary to console
        self._print_summary(report)
        return report

    def _print_summary(self, report):
        """Print a summary of the code quality results."""
        print("\n" + "=" * 60)
        print("CODE QUALITY REPORT")
        print("=" * 60)

        summary = report["summary"]
        print(f"Project: {report['project']}")
        print(f"Quality Score: {summary['quality_score']}/100")
        print(f"Total Issues: {summary['total_issues']}")
        print(f"  - Errors: {summary['total_errors']}")
        print(f"  - Warnings: {summary['total_warnings']}")

        print("\nDetailed Results:")
        print("-" * 20)

        for check_name, results in report["detailed_results"].items():
            if isinstance(results, dict):
                status = results.get("status", "unknown")
                issue_count = results.get("total_issues", 0)
                print(f"{check_name.capitalize()}: {status} ({issue_count} issues)")

                if "issues" in results and results["issues"]:
                    print("  Sample issues:")
                    for issue in results["issues"][:3]:
                        file_name = Path(issue["file"]).name
                        print(f"    - {file_name}: {issue['issue']}")

                    if len(results["issues"]) > 3:
                        print(f"    ... and {len(results['issues']) - 3} more")

        print("\n" + "=" * 60)


def main():
    """Main function to run code quality checks."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run code quality checks on the RTM Automation project"
    )
    parser.add_argument(
        "--output", "-o", help="Output file for the report (JSON format)"
    )
    parser.add_argument(
        "--files",
        "-f",
        nargs="+",
        help="Specific files to check (default: all Python files)",
    )
    parser.add_argument(
        "--checks",
        "-c",
        nargs="+",
        choices=["flake8", "all"],
        default=["all"],
        help="Which checks to run",
    )

    args = parser.parse_args()

    # Initialize checker
    checker = CodeQualityChecker()

    # Determine which checks to run
    if "all" in args.checks:
        checks_to_run = ["flake8"]
    else:
        checks_to_run = args.checks

    print("Starting code quality checks...")
    print(f"Checks to run: {', '.join(checks_to_run)}")

    # Run selected checks
    if "flake8" in checks_to_run:
        checker.run_flake8_check(args.files)

    # Generate report
    output_file = args.output or "output/code_quality_report.json"
    checker.generate_report(output_file)

    # Return appropriate exit code
    if checker.results:
        total_errors = sum(
            len(
                [
                    issue
                    for issue in results.get("issues", [])
                    if issue.get("severity") == "error"
                ]
            )
            for results in checker.results.values()
            if isinstance(results, dict)
        )
        return 1 if total_errors > 0 else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
