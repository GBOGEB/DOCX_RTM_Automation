#!/usr/bin/env python3
"""
Test runner that executes all test scripts to ensure the pipeline is working correctly
"""
import os
import sys
import subprocess
import time

def print_separator(message):
    """Print a separator with a message"""
    width = 80
    print("\n" + "=" * width)
    print(f" {message}")
    print("=" * width + "\n")

def run_test(command, description):
    """Run a test command and print the result"""
    print(f"Running: {description}")
    print(f"Command: {command}")

    start_time = time.time()
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    elapsed_time = time.time() - start_time

    if result.returncode == 0:
        print(f"✓ Passed in {elapsed_time:.2f}s")
    else:
        print(f"✗ Failed in {elapsed_time:.2f}s")
        print("Error:")
        print(result.stderr)
        print("Output:")
        print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)

    print()  # Empty line
    return result.returncode == 0

def main():
    """Run all tests"""
    print_separator("RTM Automation System Tests")
    print("This script will run a series of tests to ensure all components of the system are working correctly.\n")

    # Test OpenAI integration
    print_separator("Testing OpenAI Integration")
    openai_test = run_test(
        "python -c \"from config.openai_integration import initialize_openai; client = initialize_openai(); print(f'API Initialized: {client is not None}')\"",
        "OpenAI API Integration"
    )

    if not openai_test:
        print("⚠️  OpenAI API test failed. Make sure your API key is set correctly.")
        print("You can continue with the tests, but AI-dependent tests will fail.")

    # Test DMAIC example
    print_separator("Testing DMAIC Example")
    dmaic_test = run_test(
        "python examples/dmaic_example.py",
        "DMAIC Example Script"
    )

    # Test document conversion
    print_separator("Testing Document Conversion")

    # Create test docx file
    with open("test_doc.docx", "w") as f:
        f.write("Test document content")

    docx_test = run_test(
        "python utils/docx_converter.py test_doc.docx",
        "DOCX to Markdown Conversion"
    )

    # Clean up test file
    if os.path.exists("test_doc.docx"):
        os.remove("test_doc.docx")

    # Test agent orchestration
    print_separator("Testing Agent Orchestration")
    orchestration_test = run_test(
        "python -c \"from agents.agent_orchestrator import AgentOrchestrator; from dmaic import DMAICHandler; from utils.output_handler import OutputHandler; from config.openai_integration import initialize_openai; client = initialize_openai(); handler = DMAICHandler('Test', client); output = OutputHandler('outputs'); orchestrator = AgentOrchestrator(handler, output); print('Orchestrator initialized successfully')\"",
        "Agent Orchestration Module"
    )

    # Test refactoring
    print_separator("Testing Refactoring")

    # Create test Python file
    with open("test_refactor.py", "w") as f:
        f.write("""
def test_function(a, b, c):
    x = a + b
    y = x * c
    return y
        """)

    refactor_test = run_test(
        "python refactor.py test_refactor.py --mode quick",
        "Code Refactoring"
    )

    # Clean up test file
    if os.path.exists("test_refactor.py"):
        os.remove("test_refactor.py")

    # Test main workflow
    print_separator("Testing Main Workflow")
    main_test = run_test(
        "python -c \"from main import WorkflowController; controller = WorkflowController(); controller.initialize_project('Test Project'); print('Workflow controller initialized successfully')\"",
        "Main Workflow Controller"
    )

    # Test Markdown Fixer
    print_separator("Testing Markdown Fixer")
    # Create a dummy markdown file with known issues
    dummy_md_content = """#Heading1
* list item
```
code
```
End"""
    dummy_md_path = "test_md_fixer_test_all.md"
    with open(dummy_md_path, "w", encoding="utf-8") as f:
        f.write(dummy_md_content)

    markdown_fix_test_passed = run_test(
        f"python -c \"from utils.markdown_fixer import MarkdownFixer; from pathlib import Path; fixer = MarkdownFixer('.'); fixer.fix_markdown_file(Path('{dummy_md_path}')); print('Markdown fixer ran.')\"",
        "Markdown Linting Fixer"
    )
    # Check if file was modified (basic check, more thorough would involve content diff)
    if markdown_fix_test_passed: # Check if the script execution itself passed
        expected_fixed_content = "#Heading1\n\n* list item\n\n```text\ncode\n```\n\nEnd\n"
        try:
            with open(dummy_md_path, "r", encoding="utf-8") as f:
                fixed_content = f.read()
            # Normalize newlines for comparison, as fixer might output \n
            # and git might change them to \r\n on Windows checkout or vice-versa.
            fixed_content_normalized = fixed_content.replace('\r\n', '\n')
            expected_fixed_content_normalized = expected_fixed_content.replace('\r\n', '\n')

            if expected_fixed_content_normalized == fixed_content_normalized:
                 print(f"✓ Markdown file '{dummy_md_path}' content matches expected fixed state.")
            else:
                 print(f"✗ Markdown file '{dummy_md_path}' content not as expected after fix.")
                 print(f"Expected:\n'''{expected_fixed_content_normalized}'''")
                 print(f"Got:\n'''{fixed_content_normalized}'''")
                 markdown_fix_test_passed = False # Mark the test as failed if content doesn't match
        except FileNotFoundError:
            print(f"✗ Markdown file '{dummy_md_path}' not found after fix attempt.")
            markdown_fix_test_passed = False


    if os.path.exists(dummy_md_path):
        os.remove(dummy_md_path)

    # Display summary
    print_separator("Test Summary")
    tests = [
        ("OpenAI Integration", openai_test),
        ("DMAIC Example", dmaic_test),
        ("Document Conversion", docx_test),
        ("Agent Orchestration", orchestration_test),
        ("Refactoring", refactor_test),
        ("Main Workflow", main_test),
        ("Markdown Fixer", markdown_fix_test_passed) # Use the updated status
    ]

    for name, result in tests:
        status = "✓ Passed" if result else "✗ Failed"
        print(f"{name}: {status}")

    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    print(f"\nPassed {passed} of {total} tests ({passed/total*100:.1f}%)")

    # Exit code based on test results
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
