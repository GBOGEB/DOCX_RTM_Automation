import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Try importing the modules
try:
    from utils.markdown_generator import (
        generate_requirement_report,
        save_markdown_report,
    )

    print("Successfully imported markdown_generator modules!")
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


def main():
    """Run the markdown generator with a test requirement"""
    print("Running Markdown Generator...")

    # Example requirement data
    requirement_data = {
        "requirement": "REQ-001: The system shall provide user authentication",
        "analysis": "This requirement is clear, testable, and essential for system security. It clearly defines what the system must do (provide authentication) without specifying implementation details.",
    }

    # Generate markdown report
    print("\nGenerating markdown report...")
    markdown_content = generate_requirement_report(requirement_data)

    # Print the markdown content
    print("\nGenerated Markdown Content:")
    print("-" * 50)
    print(markdown_content)
    print("-" * 50)

    # Save to file
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.join(project_root, "output")
        os.makedirs(output_dir, exist_ok=True)

        # Save the markdown report
        output_path = os.path.join(output_dir, "requirement_analysis.md")
        save_markdown_report(markdown_content, output_path)

        print(f"\nReport saved successfully to: {output_path}")
    except Exception as e:
        print(f"Error saving report: {e}")


if __name__ == "__main__":
    main()
