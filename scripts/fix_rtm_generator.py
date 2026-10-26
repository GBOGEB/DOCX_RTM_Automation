from pathlib import Path


def fix_rtm_generator():
    """Fix RTMGenerator initialization issue"""
    rtm_file = Path("generate_rtm.py")
    if not rtm_file.exists():
        print(f"RTM generator file not found: {rtm_file}")
        return False

    with open(rtm_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if class definition is missing self in __init__
    if "def __init__(config):" in content:
        # Fix the missing self parameter
        fixed_content = content.replace(
            "def __init__(config):", "def __init__(self, config):"
        )

        with open(rtm_file, "w", encoding="utf-8") as f:
            f.write(fixed_content)

        print("Fixed RTMGenerator.__init__ method to include self parameter")
        return True
    else:
        print("RTMGenerator.__init__ method looks correct, no changes made")
        return False


if __name__ == "__main__":
    fix_rtm_generator()
