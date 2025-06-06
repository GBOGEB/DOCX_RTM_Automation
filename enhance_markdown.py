import markdown
from bs4 import BeautifulSoup


def enhance_markdown(input_markdown):
    """
    Enhances the given markdown content by converting it to HTML and applying additional formatting.
    """
    # Convert markdown to HTML
    html_content = markdown.markdown(input_markdown)

    # Use BeautifulSoup to parse and enhance the HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Example enhancement: Add a CSS class to all <p> tags
    for p in soup.find_all("p"):
        p["class"] = p.get("class", []) + ["enhanced-paragraph"]

    # Return the enhanced HTML
    return str(soup)


if __name__ == "__main__":
    # Example usage
    sample_markdown = """
    # Sample Title

    This is a sample paragraph in markdown.

    - Item 1
    - Item 2
    - Item 3
    """
    enhanced_html = enhance_markdown(sample_markdown)
    print(enhanced_html)
