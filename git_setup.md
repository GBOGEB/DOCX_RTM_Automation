# Git Setup for DOCX RTM Automation

## Clone the Repository
```bash
git clone https://github.com/your-username/DOCX_RTM_Automation_v1.0.git
cd DOCX_RTM_Automation_v1.0
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
