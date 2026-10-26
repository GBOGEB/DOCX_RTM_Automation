#!/usr/bin/env python
"""
Markdown Linter for DOCX RTM Automation
"""

import re
import sys
from typing import List, Dict, Any


class MarkdownLinter:
    def __init__(self):
        self.rules = {
            "heading_format": self._check_heading_format,
            "consecutive_blank_lines": self._check_consecutive_blank_lines,
            "trailing_whitespace": self._check_trailing_whitespace,
            "code_block_format": self._check_code_block_format,
            "requirement_format": self._check_requirement_format,
        }

    def lint(self, markdown_content: str) -> List[Dict[str, Any]]:
        """Lint markdown content and return issues"""
        if not markdown_content:
            return [
                {
                    "rule": "empty_content",
                    "message": "Markdown content is empty",
                    "line": 0,
                }
            ]

        issues = []
        for rule_name, check_func in self.rules.items():
            rule_issues = check_func(markdown_content)
            issues.extend(rule_issues)

        return sorted(issues, key=lambda x: x.get("line", 0))

    def _check_heading_format(self, content: str) -> List[Dict[str, Any]]:
        """Check heading format (#, ##, ###, etc.)"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            # Check if line starts with #
            if line.startswith("#"):
                # Ensure space after #
                match = re.match(r"^(#+)([^#\s])", line)
                if match:
                    issues.append(
                        {
                            "rule": "heading_format",
                            "message": "Missing space after # in heading",
                            "line": i + 1,
                            "content": line,
                        }
                    )

                # Check for consistency in ATX heading closing #s
                if "#" in line[1:].strip():
                    closing_match = re.match(r"^(#+)\s+(.+?)\s+(#+)$", line)
                    if closing_match and len(closing_match.group(1)) != len(
                        closing_match.group(3)
                    ):
                        issues.append(
                            {
                                "rule": "heading_format",
                                "message": "Inconsistent heading closing #s",
                                "line": i + 1,
                                "content": line,
                            }
                        )

        return issues

    def _check_consecutive_blank_lines(self, content: str) -> List[Dict[str, Any]]:
        """Check for consecutive blank lines"""
        issues = []
        lines = content.split("\n")
        blank_line_count = 0

        for i, line in enumerate(lines):
            if line.strip() == "":
                blank_line_count += 1
                if blank_line_count > 2:
                    issues.append(
                        {
                            "rule": "consecutive_blank_lines",
                            "message": "Too many consecutive blank lines",
                            "line": i + 1,
                            "content": "",
                        }
                    )
            else:
                blank_line_count = 0

        return issues

    def _check_trailing_whitespace(self, content: str) -> List[Dict[str, Any]]:
        """Check for trailing whitespace"""
        issues = []
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if line != line.rstrip():
                issues.append(
                    {
                        "rule": "trailing_whitespace",
                        "message": "Line has trailing whitespace",
                        "line": i + 1,
                        "content": line,
                    }
                )

        return issues

    def _check_code_block_format(self, content: str) -> List[Dict[str, Any]]:
        """Check code block format"""
        issues = []
        lines = content.split("\n")
        in_code_block = False
        code_block_start_line = 0
        fence_char = ""

        for i, line in enumerate(lines):
            # Check for code block fence start/end
            if line.startswith("```") or line.startswith("~~~"):
                fence_match = re.match(r"^([`~]{3,})", line)
                current_fence = fence_match.group(1) if fence_match else ""

                if not in_code_block:
                    in_code_block = True
                    fence_char = current_fence[0]  # ` or ~
                    code_block_start_line = i + 1
                else:
                    in_code_block = False
                    # Check if fence characters match
                    if fence_char != current_fence[0]:
                        issues.append(
                            {
                                "rule": "code_block_format",
                                "message": f"Code block fence mismatch (started with {fence_char * 3}, ended with {current_fence})",
                                "line": i + 1,
                                "content": line,
                            }
                        )

        # Check if code block is not closed
        if in_code_block:
            issues.append(
                {
                    "rule": "code_block_format",
                    "message": f"Unclosed code block (started at line {code_block_start_line})",
                    "line": code_block_start_line,
                    "content": lines[code_block_start_line - 1],
                }
            )

        return issues

    def _check_requirement_format(self, content: str) -> List[Dict[str, Any]]:
        """Check requirement format (e.g., REQ-001)"""
        issues = []
        lines = content.split("\n")
        req_pattern = re.compile(r"(REQ-\d+|[A-Z]+-\d+)")

        for i, line in enumerate(lines):
            # Look for requirement IDs
            req_matches = req_pattern.finditer(line)
            for match in req_matches:
                req_id = match.group(1)

                # Verify format consistency
                if not re.match(r"^[A-Z]+-\d{3,}$", req_id):
                    issues.append(
                        {
                            "rule": "requirement_format",
                            "message": f"Requirement ID format is inconsistent: {req_id}",
                            "line": i + 1,
                            "content": line,
                        }
                    )

        return issues


def main():
    """Main function when script is executed directly"""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Lint Markdown files for documentation quality"
    )
    parser.add_argument("files", nargs="+", help="Markdown files to lint")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues (not all can be fixed)",
    )

    args = parser.parse_args()

    linter = MarkdownLinter()
    all_issues = {}

    for file_path in args.files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            issues = linter.lint(content)
            all_issues[file_path] = issues

            if args.fix:
                # Fix issues that can be automatically fixed
                fixed_content = content
                # TODO: Implement fixing logic here

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)

        except Exception as e:
            if args.json:
                all_issues[file_path] = [
                    {"rule": "file_error", "message": str(e), "line": 0}
                ]
            else:
                print(f"Error processing {file_path}: {e}")

    if args.json:
        print(json.dumps(all_issues, indent=2))
    else:
        # Print issues in human-readable format
        for file_path, issues in all_issues.items():
            if issues:
                print(f"\n{file_path}:")
                for issue in issues:
                    print(f"  Line {issue['line']}: {issue['message']}")
                    if "content" in issue and issue["content"]:
                        print(f"    {issue['content']}")
            else:
                print(f"\n{file_path}: No issues found")

    # Return error code if any issues found
    return 1 if any(issues for issues in all_issues.values()) else 0


if __name__ == "__main__":
    sys.exit(main())

# Additional changes:
# 1. Added module files from external GitHub repository.
# 2. Created a comprehensive test procedure file and test runner.
# 3. Updated the refactoring script to incorporate modules and tests.
# 4. Improved the README with information about modules and testing.
# 5. Added instructions for resolving README.md conflicts with Git.
