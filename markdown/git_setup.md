# Git Setup for DOCX RTM Automation

## Clone the Repository

```bash
git clone https://github.com/your-username/DOCX_RTM_Automation_v1.0.git
cd DOCX_RTM_Automation_v1.0
```

### Working with Submodules

If the project uses Git submodules, you can clone the repository and initialize submodules in one step:

```bash
git clone --recurse-submodules https://github.com/your-username/DOCX_RTM_Automation_v1.0.git
cd DOCX_RTM_Automation_v1.0
```

If you have already cloned the repository without submodules, you can initialize and update them using:

```bash
git submodule update --init --recursive
```

To update submodules to their latest commit from their respective remotes:
```bash
git submodule update --remote
# After this, you'll likely need to commit the updated submodule references in the parent repository.
git add . # Or add specific submodule paths
git commit -m "Update submodules to latest versions"
```

## Set Up Remote

```bash
git remote add origin https://github.com/your-username/DOCX_RTM_Automation_v1.0.git
```

## Push Changes

```bash
git add .
git commit -m "Initial commit"
git push -u origin main
```

## Automated CI/CD Pipeline

The project now includes an integrated CI/CD pipeline that handles Git operations automatically:

### Running the Automated Pipeline

```bash
# Simply run the pipeline script
python run_pipeline.py
```

The automated pipeline will:
1. Clone the repository if not already present
2. Pull latest changes from the remote main branch
3. Run all document processing steps
4. Commit and push changes back to GitHub

### Configuration

All GitHub integration settings are in the `config/paths.yaml` file:
- `enabled`: Set to true/false to enable/disable GitHub integration
- `repo_url`: The URL of your GitHub repository
- `branch`: The branch to work with (default: main)
- `local_path`: Local repository path
- `user_name` and `user_email`: Git identity settings
- `commit_message`: Custom commit message for automated updates

## API Key Management (OpenAI, GitHub)

If your workflows involve direct interactions with OpenAI or GitHub APIs (e.g., for advanced Git operations, AI-assisted tasks), ensure secure management of API keys/tokens:

*   **Environment Variables**: Store API keys as environment variables (e.g., `OPENAI_API_KEY`, `GITHUB_TOKEN`). This is a common and recommended practice.
*   **Secrets Management Tools**: For more robust solutions, especially in CI/CD environments, use dedicated secrets management tools (e.g., HashiCorp Vault, GitHub Secrets).
*   **Configuration Files (Caution)**: Avoid hardcoding API keys directly in scripts or version-controlled configuration files. If a config file is used to point to a key (e.g., a path to a key file), ensure this key file itself is not committed to the repository (add it to `.gitignore`).
