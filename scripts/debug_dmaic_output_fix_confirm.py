from pathlib import Path


def debug_dmaic_output(file_path_str: str):
    """
    Function to debug and confirm DMAIC output.
    :param file_path_str: Path to the DMAIC output file as a string.
    """
    file_path = Path(file_path_str)
    if not file_path.exists():
        print(f"Error: File '{file_path}' does not exist.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.readlines()

        print("File content successfully read. Debugging output...")
        for line in content:
            print(line.strip())  # Process each line as needed

        print("Debugging complete. Output confirmed.")
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")


if __name__ == "__main__":
    # Example usage
    dmaic_file_path = input("Enter the path to the DMAIC output file: ")
    debug_dmaic_output(dmaic_file_path)
