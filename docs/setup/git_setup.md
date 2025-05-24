# Navigate to your project directory
cd /C:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0

# Make sure your local Git repository is initialized
git init

# Check your Git identity is set 
git config --global user.name "GBOGEB"
git config --global user.email "gerkotze.bonthuys@sckcen.be"

# Verify the Repository URL
Ensure you have the correct repository URL. Replace `<your-username>` and `<repository-name>` with the actual values.

```
https://github.com/<your-username>/<repository-name>.git
```

# Clone the Repository
To clone the repository, use the following command:

```bash
git clone https://github.com/<your-username>/<repository-name>.git
```

# Add the Remote Repository
If the remote repository is not already added, you can add it using the command below. Replace `<your-username>` and `<repository-name>` with the actual values:

```bash
git remote add origin https://github.com/<your-username>/<repository-name>.git
```

# Update All Items in the Input Directory
Ensure all files in the `input/docx` directory are updated as needed:

```plaintext
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\input\docx
```

# Additional Files in the Project
Here is a list of other important files in the project directory:

```plaintext
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\fix_errors.py
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\full_integration.py
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\GIT_push.py
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\git_setup.md
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\global_config.yaml
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\project_cleanup.py
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\project_manifest.md
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\project_update.py
C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0\verify_setup.py
```

# Add all files to the repository
git add .

# Make the initial commit
git commit -m "Initial commit"

# Push to GitHub (main branch)
git push -u origin main