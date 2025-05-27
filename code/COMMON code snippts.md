# Common Git Command Snippets

This document provides common Git commands for initializing a project, configuring Git, and interacting with a remote GitHub repository.

## 1. Project Initialization and First Commit

These commands are typically run once when starting a new project or adding an existing project to Git.

```bash
# Navigate to your project's root directory.
# IMPORTANT: Replace "/path/to/your/project/DOCX_RTM_Automation_v1.0"
# with the actual path to your project folder.
cd /path/to/your/project/DOCX_RTM_Automation_v1.0

# Initialize a new Git repository in the current directory.
# This creates a hidden .git folder to track changes.
git init

# Check your Git user identity (name and email).
# These are used to attribute your commits.
# If not set, or if you want to set them for this repository only (omit --global):
git config --global user.name "GBOGEB"
git config --global user.email "gerkotze.bonthuys@sckcen.be"
# To check current config:
# git config user.name
# git config user.email

# Add a remote repository named "origin".
# Replace "https://github.com/GBOGEB/DOCX_RTM_Automation.git"
# with your actual GitHub repository URL.
# Use HTTPS URL (as shown) or SSH URL (e.g., git@github.com:GBOGEB/DOCX_RTM_Automation.git).
git remote add origin https://github.com/GBOGEB/DOCX_RTM_Automation.git
# To verify remotes:
# git remote -v

# Stage all files in the current directory and subdirectories for the first commit.
# The "." means "all files in the current directory".
git add .

# Commit the staged files with an initial commit message.
# The -m flag allows you to provide the message inline.
git commit -m "Initial commit: Project setup and first files"

# Push the initial commit to the "main" branch on the remote "origin".
# The -u flag sets the upstream branch, so future `git push` commands
# from the "main" branch will automatically go to "origin/main".
# If your default branch is named "master", use "master" instead of "main".
git push -u origin main
```

## 2. Common Workflow Commands (After Initial Setup)

These commands are used in the day-to-day development workflow.

```bash
# Check the status of your working directory and staging area.
# Shows modified, staged, and untracked files.
git status

# Stage specific files for the next commit.
# git add <file1> <file2>
# Or stage all modified and new files (excluding .gitignored files):
git add .

# Commit staged changes with a descriptive message.
git commit -m "Implemented feature X and fixed bug Y"

# Push committed changes from your local branch to the remote repository.
# Assumes your local branch is tracking a remote branch (e.g., after `git push -u`).
git push

# Fetch changes from the remote repository and merge them into your current local branch.
# This is a combination of `git fetch` and `git merge`.
git pull
```

## 3. Branching (Example)

```bash
# Create a new branch named "feature-branch" and switch to it.
git checkout -b feature-branch

# ... make changes and commit them on "feature-branch" ...
git add .
git commit -m "Added new feature on feature-branch"

# Push the new branch to the remote repository.
git push -u origin feature-branch

# Switch back to the main branch.
git checkout main

# Merge "feature-branch" into "main".
git merge feature-branch

# Delete the feature branch locally (if no longer needed).
git branch -d feature-branch

# Delete the feature branch remotely (if no longer needed).
git push origin --delete feature-branch
```