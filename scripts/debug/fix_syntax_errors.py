#!/usr/bin/env python3
"""
Fix syntax errors in problematic Python files that failed black formatting
"""

import os
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_debug_full_pipeline():
    """Fix syntax errors in debug_full_pipeline.py files"""
    paths = [
        "scripts/debug_full_pipeline.py",
        "DOCX_RTM_Automation/scripts/debug_full_pipeline.py",
    ]

    for path in paths:
        if not os.path.exists(path):
            logger.error("File not found: %s", path)
            continue

        logger.info("Fixing syntax in %s...", path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Fix unclosed string literals
        if 'logging.debug("Pipeline execution' in content:
            fixed_content = content.replace(
                'logging.debug("Pipeline execution',
                'logging.debug("Pipeline execution")',
            )

            with open(path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            logger.info("Fixed unclosed string literal in %s", path)
        else:
            logger.info("No issues found to fix in %s", path)


def fix_docx_rtm_automation():
    """Fix syntax errors in docx_rtm_automation.py files"""
    paths = [
        "scripts/docx_rtm_automation.py",
        "DOCX_RTM_Automation/scripts/docx_rtm_automation.py",
    ]

    for path in paths:
        if not os.path.exists(path):
            logger.error("File not found: %s", path)
            continue

        logger.info("Fixing syntax in %s...", path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Look for unclosed parentheses, brackets, or multiline strings
            opening_count = 0
            closing_count = 0

            fixed_lines = []
            in_multiline_string = False
            multiline_quote = None

            for _i, line in enumerate(lines):  # Mark unused variable with underscore
                # Count opening and closing parentheses/brackets/braces
                opening_count += line.count("(") + line.count("[") + line.count("{")
                closing_count += line.count(")") + line.count("]") + line.count("}")

                # Check for multiline strings
                if not in_multiline_string:
                    if '"""' in line.split("#")[0]:
                        if line.count('"""') % 2 == 1:  # Odd number of triple quotes
                            in_multiline_string = True
                            multiline_quote = '"""'
                    elif "'''" in line.split("#")[0]:
                        if line.count("'''") % 2 == 1:  # Odd number of triple quotes
                            in_multiline_string = True
                            multiline_quote = "'''"
                else:
                    if multiline_quote in line:
                        in_multiline_string = False
                        multiline_quote = None

                fixed_lines.append(line)

            # If we're still in a multiline string at the end, close it
            if in_multiline_string:
                fixed_lines.append(multiline_quote + "\n")
                logger.info("Fixed unclosed multiline string")

            # If there are unbalanced parentheses/brackets/braces, add closing ones
            diff = opening_count - closing_count
            if diff > 0:
                fixed_lines.append(")" * diff + "\n")
                logger.info(
                    "Added %d missing closing parentheses/brackets/braces", diff
                )

            with open(path, "w", encoding="utf-8") as f:
                f.writelines(fixed_lines)

            logger.info("Attempted to fix syntax issues in %s", path)

        except Exception as e:
            logger.error("Error processing %s: %s", path, e)


def fix_safe_refactor_utility():
    """Fix syntax errors in safe_refactor_utility.py files"""
    paths = [
        "scripts/safe_refactor_utility.py",
        "DOCX_RTM_Automation/scripts/safe_refactor_utility.py",
    ]

    for path in paths:
        if not os.path.exists(path):
            logger.error("File not found: %s", path)
            continue

        logger.info("Fixing syntax in %s...", path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if the issue is a shebang line with python command
            if re.search(r"^python\s+", content, re.MULTILINE):
                fixed_content = re.sub(
                    r"^python\s+", "# python ", content, flags=re.MULTILINE
                )

                with open(path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                logger.info("Fixed invalid python command in %s", path)
            else:
                logger.info("No issues found to fix in %s", path)

        except Exception as e:
            logger.error("Error processing %s: %s", path, e)


def fix_extract_outline():
    """Fix syntax errors in extract_outline.py files"""
    paths = [
        "src/extractors/extract_outline.py",
        "DOCX_RTM_Automation/src/extractors/extract_outline.py",
    ]

    for path in paths:
        if not os.path.exists(path):
            logger.error("File not found: %s", path)
            continue

        logger.info("Fixing syntax in %s...", path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for incomplete if statement at end of file
            if content.rstrip().endswith("if len(sys.argv) > 1:"):
                fixed_content = content.rstrip() + "\n    pass\n"

                with open(path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                logger.info("Fixed incomplete if statement in %s", path)
            else:
                logger.info("No issues found to fix in %s", path)

        except Exception as e:
            logger.error("Error processing %s: %s", path, e)


def fix_extract_rtm():
    """Fix syntax errors in extract_rtm.py files"""
    paths = [
        "src/extractors/extract_rtm.py",
        "DOCX_RTM_Automation/src/extractors/extract_rtm.py",
    ]

    for path in paths:
        if not os.path.exists(path):
            logger.error("File not found: %s", path)
            continue

        logger.info("Fixing syntax in %s...", path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Fix incomplete sys.path.append statement
            if (
                "sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"
                in content
                and not content.rstrip().endswith(")")
            ):
                # Fix missing parenthesis
                fixed_content = content.rstrip() + ")"

                with open(path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                logger.info(
                    "Fixed missing parenthesis in sys.path.append statement in %s", path
                )
            else:
                logger.info("No issues found to fix in %s", path)

        except Exception as e:
            logger.error("Error processing %s: %s", path, e)


def fix_server_app():
    """Fix syntax errors in server/app.py file"""
    path = "server/app.py"

    if not os.path.exists(path):
        logger.error("File not found: %s", path)
        return

    logger.info("Fixing syntax in %s...", path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Look for unclosed code blocks or indentation issues
        if "self.input_dir = str(job_input_dir)" in content:
            # Add missing indentation or fix incomplete block
            lines = content.split("\n")
            fixed_lines = []

            for i, line in enumerate(lines):
                fixed_lines.append(line)
                if line.strip() == "self.input_dir = str(job_input_dir)":
                    # Check the next line to see if we need to add a placeholder
                    if i + 1 >= len(lines) or not lines[i + 1].strip():
                        indentation = len(line) - len(line.lstrip())
                        fixed_lines.append(" " * indentation + "pass")

            fixed_content = "\n".join(fixed_lines)

            with open(path, "w", encoding="utf-8") as f:
                f.write(fixed_content)
            logger.info("Fixed incomplete code block in %s", path)
        else:
            logger.info("No issues found to fix in %s", path)

    except Exception as e:
        logger.error("Error processing %s: %s", path, e)


if __name__ == "__main__":
    logger.info("Fixing syntax errors in files that failed Black formatting...")

    # Fix each problematic file type
    fix_debug_full_pipeline()
    fix_docx_rtm_automation()
    fix_safe_refactor_utility()
    fix_extract_outline()
    fix_extract_rtm()
    fix_server_app()

    logger.info(
        "Attempted to fix syntax errors. Please review the files before running black again."
    )
    logger.info("After reviewing, you can run black again with:")
    logger.info("black .")
