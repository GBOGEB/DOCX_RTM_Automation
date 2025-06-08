import yaml
import sys
import os


def main():
    # Load configuration
    with open("config/paths.yaml") as file:
        yaml.safe_load(file)

    # Import modules (using a relative import strategy)
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    from word_to_md import convert_word_to_md
    from extract_outline import extract_outline
    from extract_rtm import extract_rtm

    # Process workflow
    convert_word_to_md()
    extract_outline()
    extract_rtm()


if __name__ == "__main__":
    main()
