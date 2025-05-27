# Navigate to your project directory
cd <your-chosen-directory-to-clone-into>

# Make sure your Git identity is set
# (Git uses this information for every commit you create)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify the Repository URL
# Ensure you have the correct repository URL.
# Replace `<your-username>` and `<repository-name>` with the actual values from the project.
# Example: https://github.com/GBOGEB/DOCX_RTM_Automation.git

# Clone the Repository
# Replace `<repository-url>` with the actual URL.
git clone <repository-url>

# Navigate into the cloned directory
# Replace `<repository-name>` with the actual name of the repository folder.
cd <repository-name>

# Initialize and Update Git Submodules
# If the project uses Git submodules, initialize and update them:
git submodule init
git submodule update --recursive

# (Optional) Add the Remote Repository if working with an existing local, unversioned project
# This step is typically not needed if you cloned the repository.
# It's for connecting a local project to a new remote repository on GitHub.
# git remote add origin https://github.com/<your-username>/<repository-name>.git

# Update All Items in the Input Directory
# Ensure all necessary files in the `input/docx` directory are up-to-date.
# This directory should be relative to your project root:
# <your-project-directory>/input/docx

echo "Please ensure the content of 'input/docx' is correctly populated."

# Key Files and Directories in the Project
# Here is a list of other important files and directories at the project root:
# (Paths are relative to the project root, e.g., <repository-name>/)

# ```plaintext
# fix_errors.py
# full_integration.py
# GIT_push.py
# git_setup.md
# global_config.yaml
# project_cleanup.py
# project_manifest.md
# project_update.py
# verify_setup.py
# src/
# tests/
# output/
# docs/
# config/
# input/
# ```

# Setup is complete. You can now run the project according to its main README or usage instructions.