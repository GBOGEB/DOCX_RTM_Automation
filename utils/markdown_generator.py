import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Now import from config
from config.openai_integration import initialize_openai, create_agent

client = initialize_openai()

markdown_generator = create_agent(
    system_prompt="""You are a documentation specialist.
Your task is to generate clear, well-formatted markdown documentation based on the provided information.
Ensure that all markdown elements, especially headers (e.g., '# Header'), lists, and code blocks, are correctly formatted according to standard markdown syntax.
Pay attention to spacing and structure for optimal readability.""",
    client=client,
)


def generate_requirement_report(requirement_data):
    """Generate markdown documentation for requirement analysis"""
    prompt = f"""
    Generate a markdown report for the following requirement analysis:

    Requirement: {requirement_data["requirement"]}
    Analysis: {requirement_data["analysis"]}

    Use proper markdown formatting with headers, bullet points, and tables where appropriate.
    """

    markdown_content, _ = markdown_generator(prompt)
    return markdown_content


def save_markdown_report(content, output_path):
    """Save markdown content to file"""
    with open(output_path, "w") as f:
        f.write(content)
    print(f"Report saved to {output_path}")
