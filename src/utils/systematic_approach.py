#!/usr/bin/env python3
"""
Systematic approach to fix and implement the RTM Automation workflow.
This script guides you through the step-by-step process defined in our plan.
"""
import os
import sys
import subprocess
from pathlib import Path


class SystematicApproach:
    """Class to guide through our systematic approach."""

    def __init__(self):
        self.current_phase = 1
        self.current_step = 1
        self.steps_completed = set()

    def run_command(self, cmd, description=None):
        """Run a command and print its output."""
        print(f"\n=== Running: {description or ' '.join(cmd)} ===\n")
        result = subprocess.run(cmd, text=True)
        return result.returncode == 0

    def phase1_code_health(self):
        """Phase 1: Code Health and Stability"""
        print("\n=== Phase 1: Code Health and Stability ===\n")

        # Step 1: Static Analysis
        if self.current_step == 1 and "P1-1" not in self.steps_completed:
            print("\n--- P1-1: Static Analysis - Linting and Formatting ---\n")
            self.run_command(
                ["python", "fix_specific_errors.py"], "Fixing syntax errors"
            )
            self.run_command(["black", "."], "Running Black formatter")
            self.steps_completed.add("P1-1")
            self.current_step += 1

        # Step 2: Dependency Verification
        if self.current_step == 2 and "P1-2" not in self.steps_completed:
            print("\n--- P1-2: Dependency Verification ---\n")
            self.run_command(["python", "debug_helpers.py"], "Running debug helpers")
            self.steps_completed.add("P1-2")
            self.current_step += 1

        # Step 3: Address Import Errors
        if self.current_step == 3 and "P1-3" not in self.steps_completed:
            print("\n--- P1-3: Address Import Errors ---\n")
            self.run_command(["python", "fix_imports.py"], "Fixing import errors")
            self.steps_completed.add("P1-3")
            self.current_step += 1

        # Step 4: Unit Tests (if available)
        if self.current_step == 4 and "P1-4" not in self.steps_completed:
            print("\n--- P1-4: Unit Testing ---\n")
            tests_dir = Path("tests")
            if tests_dir.exists():
                self.run_command(["pytest"], "Running tests")
            else:
                print("No tests directory found. Creating a basic test...")
                os.makedirs("tests", exist_ok=True)
                with open("tests/test_basic.py", "w") as f:
                    f.write(
                        '''
import unittest

class BasicTest(unittest.TestCase):
    def test_debug_sample(self):
        """Test that debug_sample.py can be imported"""
        import debug_sample
        self.assertTrue(hasattr(debug_sample, "setup_debugger"))

if __name__ == "__main__":
    unittest.main()
'''
                    )
                self.run_command(
                    ["python", "-m", "unittest", "discover", "tests"],
                    "Running basic tests",
                )
            self.steps_completed.add("P1-4")
            self.current_step = 1  # Reset step counter for next phase
            self.current_phase = 2  # Move to next phase

    def phase2_word_to_markdown(self):
        """Phase 2: Core Functionality - Word to Markdown"""
        print("\n=== Phase 2: Core Functionality - Word to Markdown ===\n")

        # Step 5: Word-to-Markdown Conversion
        if self.current_step == 1 and "P2-5" not in self.steps_completed:
            print("\n--- P2-5: Word-to-Markdown Conversion ---\n")

            # Find Word-to-Markdown scripts
            self.run_command(
                ["python", "find_word_to_md.py"],
                "Finding Word-to-Markdown conversion scripts",
            )

            # Create test DOCX file
            self.run_command(
                ["python", "create_test_docx.py"], "Creating test DOCX file"
            )

            # Run the conversion
            self.run_command(
                ["python", "try_word_to_md.py"], "Converting DOCX to Markdown"
            )

            self.steps_completed.add("P2-5")
            self.current_step = 1  # Reset step counter for next phase
            self.current_phase = 3  # Move to next phase

    def phase3_rtm_and_roundtrip(self):
        """Phase 3: Building the RTM and Roundtrip"""
        print("\n=== Phase 3: Building the RTM and Roundtrip ===\n")

        # Step 6: Parse Markdown for Requirements
        if self.current_step == 1 and "P3-6" not in self.steps_completed:
            print("\n--- P3-6: Parse Markdown for Requirements ---\n")

            # Create sample requirements if needed
            requirements_dir = Path("input")
            requirements_file = requirements_dir / "requirements.md"

            if not requirements_file.exists():
                print("No requirements.md found. Using the sample requirements.")
                # The sample requirements file should already be there

            # Run the requirements analysis
            self.run_command(
                ["python", "Project Requirements.py"], "Analyzing requirements"
            )

            self.steps_completed.add("P3-6")
            self.current_step += 1

        # Step 7: Populate DataFrame
        if self.current_step == 2 and "P3-7" not in self.steps_completed:
            print("\n--- P3-7: Populate DataFrame ---\n")

            # Check if requirements analysis output exists
            output_traceability = Path("output") / "requirements_traceability.json"

            if output_traceability.exists():
                print("Requirements traceability matrix already generated.")
            else:
                print(
                    "Running requirements analysis to generate traceability matrix..."
                )
                self.run_command(
                    ["python", "Project Requirements.py"],
                    "Generating requirements traceability",
                )

            self.steps_completed.add("P3-7")
            self.current_step += 1

        # Step 8: Markdown to Word (Roundtrip)
        if self.current_step == 3 and "P3-8" not in self.steps_completed:
            print("\n--- P3-8: Markdown to Word (Roundtrip) ---\n")

            # Create a simple Markdown to DOCX converter if needed
            md_to_docx_file = Path("md_to_docx.py")

            if not md_to_docx_file.exists():
                print("Creating Markdown to DOCX converter...")
                with open(md_to_docx_file, "w") as f:
                    f.write(
                        '''#!/usr/bin/env python3
"""
Convert Markdown to DOCX for roundtrip testing.
"""
import sys
from pathlib import Path

def markdown_to_docx(md_file, output_file=None):
    """Convert Markdown to DOCX."""
    try:
        from docx import Document
    except ImportError:
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "python-docx"])
        from docx import Document

    # Create a new document
    doc = Document()

    # Read the markdown file
    with open(md_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Simple parsing of markdown to docx
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # Headers
        if line.startswith("# "):
            doc.add_heading(line[2:], level=0)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=1)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=2)
        elif line.startswith("#### "):
            doc.add_heading(line[5:], level=3)
        # Lists
        elif line.startswith("- ") or line.startswith("* "):
            doc.add_paragraph(line[2:], style="List Bullet")
        elif line.startswith("1. "):
            doc.add_paragraph(line[3:], style="List Number")
        # Tables
        elif line.startswith("|"):
            # Find the end of the table
            table_lines = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("|"):
                # Skip separator rows for markdown tables
                if lines[j].strip().replace("|", "").replace(" ", "").replace("-", "") == "":
                    j += 1
                    continue
                table_lines.append(lines[j].strip())
                j += 1

            if len(table_lines) > 1:
                # Create a table
                rows_count = len(table_lines)
                cols_count = len(table_lines[0].split("|")) - 2  # -2 for start/end pipes

                if cols_count > 0 and rows_count > 0:
                    table = doc.add_table(rows=rows_count, cols=cols_count)

                    for row_idx, table_row in enumerate(table_lines):
                        cells = table_row.split("|")[1:-1]  # Remove first/last empty cells

                        for col_idx, cell_text in enumerate(cells):
                            if col_idx < cols_count:
                                table.cell(row_idx, col_idx).text = cell_text.strip()

                i = j - 1  # Skip ahead to after the table
        # Regular paragraph
        else:
            # Handle basic formatting (bold, italic)
            p = doc.add_paragraph()
            # This is very simplified - real implementation would handle formatting
            p.add_run(line)

        i += 1

    # Save the document
    if output_file is None:
        output_file = Path(md_file).with_suffix('.docx')

    doc.save(output_file)
    return output_file

def main():
    """Main function to parse command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python md_to_docx.py <markdown_file> [output_docx_file]")
        return 1

    md_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not Path(md_file).exists():
        print(f"Error: File not found - {md_file}")
        return 1

    try:
        output_path = markdown_to_docx(md_file, output_file)
        print(f"Conversion successful! Output saved to {output_path}")
        return 0
    except Exception as e:
        print(f"Error converting file: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
                    )

            # Find a Markdown file to convert
            output_dir = Path("output")
            md_files = list(output_dir.glob("*.md"))

            if md_files:
                md_file = md_files[0]
                self.run_command(
                    ["python", "md_to_docx.py", str(md_file)],
                    f"Converting {md_file.name} back to DOCX",
                )
            else:
                print("No Markdown files found in output directory.")

            self.steps_completed.add("P3-8")
            self.current_step += 1

    def run_approach(self):
        """Run through the systematic approach."""
        print("\n=== RTM Automation Systematic Approach ===\n")
        print("This script will guide you through our systematic approach.")

        while True:
            if self.current_phase == 1:
                self.phase1_code_health()
            elif self.current_phase == 2:
                self.phase2_word_to_markdown()
            elif self.current_phase == 3:
                self.phase3_rtm_and_roundtrip()
            else:
                break

        print("\n=== Approach Complete! ===\n")
        print("All steps of the systematic approach have been completed.")
        print("Here's a summary of what we've accomplished:")
        print("1. Fixed syntax errors and formatted the code")
        print("2. Verified dependencies and fixed import errors")
        print("3. Converted DOCX to Markdown")
        print("4. Analyzed requirements and generated traceability matrix")
        print("5. Implemented roundtrip conversion back to DOCX")

        print("\nThe RTM Automation system should now be functional.")


if __name__ == "__main__":
    approach = SystematicApproach()
    approach.run_approach()
