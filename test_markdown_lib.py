# filepath: test_markdown_lib.py
import markdown
import sys

print(f"Python version: {sys.version}")
print("Attempting to access markdown.__file__: ", end="")
try:
    print(markdown.__file__)
except AttributeError:
    print("markdown module has no __file__ attribute.")

print("Attempting to access markdown.__version__: ", end="")
try:
    print(markdown.__version__)
except AttributeError:
    print("markdown module has no __version__ attribute.")


print("\nAttempting to call markdown.markdown():")
try:
    html = markdown.markdown("## Hello World")
    print("  markdown.markdown() function call successful.")
    print("  HTML output:", html)
except AttributeError as e:
    print(f"  AttributeError: {e}")
except Exception as e:
    print(f"  An unexpected error occurred: {e}")

print("\nAttributes in the imported 'markdown' module (excluding private/dunder):")
try:
    count = 0
    for attr in dir(markdown):
        if not attr.startswith("_"):
            print(f"  - {attr}")
            count += 1
    if count == 0:
        print("  No public attributes found.")
except Exception as e:
    print(f"  Could not list attributes: {e}")
