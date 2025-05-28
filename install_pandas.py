import subprocess
import sys

# install_pandas.py


def install_pandas():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
        print("Pandas installed successfully.")
    except Exception as e:
        print(f"An error occurred while installing pandas: {e}")

if __name__ == "__main__":
    install_pandas()