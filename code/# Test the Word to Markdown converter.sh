# Test the Word to Markdown converter
# Assuming word_to_md.py is in the code/ directory
python code/word_to_md.py input/YOUR_DOCUMENT.docx -o output/test.md

# Test the outline extraction (using extract_outline.py)
# Assumes output/test.md is the markdown file to process
python code/extract_outline.py output/test.md output/outlines/test_md_outline.yaml

# Test the RTM generator (using extract_rtm.py)
# Assumes output/YOUR_DOCUMENT.md is the markdown file to process
# The script expects an input MD file and an output YAML file path.
python code/extract_rtm.py output/YOUR_DOCUMENT.md output/rtm_extractions/YOUR_DOCUMENT_requirements.yaml

