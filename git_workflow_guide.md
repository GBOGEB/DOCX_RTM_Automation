# Git and GitHub Workflow Guide for RTM Automation

## Initial Setup

### 1. Install Git
```bash
# Check if Git is installed
git --version

# If not installed, download from: https://git-scm.com/
```

### 2. Configure Git (First Time Only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Initialize Local Repository
```bash
# Navigate to your project directory
cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0

# Initialize Git repository
git init

# Create .gitignore file
echo "# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
.pytest_cache/

# Output files
output/
*.log
*.tmp

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Sensitive files
config.ini
secrets.json
.env" > .gitignore
```

## Daily Git Workflow

### 1. Check Status
```bash
# See what files have changed
git status

# See detailed changes
git diff
```

### 2. Stage Changes
```bash
# Add specific files
git add filename.py

# Add all Python files
git add *.py

# Add all changes
git add .

# Add all files in a directory
git add pipeline/
```

### 3. Commit Changes
```bash
# Commit with message
git commit -m "Add RTM processing functionality"

# Commit with detailed message
git commit -m "Fix: resolve indentation error in find_output_files.py

- Fixed missing indentation after if statement
- Added proper error handling for file access
- Improved code readability"
```

### 4. View History
```bash
# See commit history
git log --oneline

# See detailed history
git log

# See changes in last commit
git show
```

## GitHub Integration

### 1. Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. Name: `DOCX_RTM_Automation`
4. Description: `Automated RTM processing for DOCX files`
5. Choose Public/Private
6. Don't initialize with README (we have local files)

### 2. Connect Local to GitHub
```bash
# Add remote repository
git remote add origin https://github.com/yourusername/DOCX_RTM_Automation.git

# Verify remote
git remote -v

# Push to GitHub (first time)
git branch -M main
git push -u origin main
```

### 3. Regular Push/Pull Workflow
```bash
# Pull latest changes from GitHub
git pull origin main

# Push your changes to GitHub
git push origin main

# Or just (after first push)
git push
```

## Branching Strategy

### 1. Feature Branches
```bash
# Create and switch to new branch
git checkout -b feature/new-processing-algorithm

# Work on your changes...
git add .
git commit -m "Implement new processing algorithm"

# Push branch to GitHub
git push origin feature/new-processing-algorithm
```

### 2. Merge Back to Main
```bash
# Switch back to main
git checkout main

# Pull latest changes
git pull origin main

# Merge your feature
git merge feature/new-processing-algorithm

# Push merged changes
git push origin main

# Delete feature branch
git branch -d feature/new-processing-algorithm
git push origin --delete feature/new-processing-algorithm
```

## Common Scenarios

### 1. Undo Changes
```bash
# Undo changes to a file (before staging)
git checkout -- filename.py

# Unstage a file
git reset HEAD filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (lose changes)
git reset --hard HEAD~1
```

### 2. Working with Others
```bash
# See who changed what
git blame filename.py

# See differences between branches
git diff main feature/new-feature

# Merge conflicts resolution
# Edit conflicted files, then:
git add resolved_file.py
git commit -m "Resolve merge conflicts"
```

### 3. Tagging Releases
```bash
# Create a tag
git tag -a v1.0 -m "First stable release"

# Push tags
git push origin --tags

# List tags
git tag -l
```

## Recommended Commit Messages

### Format
```
Type: Brief description

Detailed explanation if needed
- Point 1
- Point 2
```

### Types
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

### Examples
```bash
git commit -m "feat: add DOCX parsing functionality"
git commit -m "fix: resolve memory leak in file processing"
git commit -m "docs: update README with installation steps"
git commit -m "refactor: optimize RTM processing pipeline"
```

## GitHub Features to Use

### 1. Issues
- Track bugs and feature requests
- Use labels: `bug`, `enhancement`, `documentation`
- Assign to team members

### 2. Pull Requests
- Code review process
- Link to issues: "Closes #123"
- Use templates for consistency

### 3. Actions (CI/CD)
- Automated testing
- Code quality checks
- Deployment automation

### 4. Wiki
- Extended documentation
- User guides
- API documentation

## Best Practices

1. **Commit Often**: Small, focused commits
2. **Clear Messages**: Descriptive commit messages
3. **Test Before Commit**: Ensure code works
4. **Pull Before Push**: Stay updated
5. **Use Branches**: Feature development
6. **Review Code**: Use pull requests
7. **Document Changes**: Update README/docs
8. **Backup**: GitHub is your backup

## Emergency Commands

```bash
# Save current work without committing
git stash

# Restore stashed work
git stash pop

# Force push (use carefully!)
git push --force

# Reset to remote state
git reset --hard origin/main

# See all branches
git branch -a

# Delete local branch
git branch -d branch-name
```
