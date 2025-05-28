# Git Hooks Guide for RTM Automation

This guide explains how to use Git hooks in the DOCX RTM Automation project across different environments.

## What are Git Hooks?

Git hooks are scripts that Git executes before or after events such as commit, push, and merge. They help automate quality checks and enforce standards.

## Available Hooks in This Project

- **pre-commit**: Runs before finalizing a commit
  - Checks for debug print statements
  - Detects large files
  - Checks for trailing whitespace

## Running Git Hooks in Different Environments

### In Windows Command Prompt (CMD)

```cmd
REM Run the helper script
run_git_hook.bat pre-commit

REM Or directly run the hook
.git\hooks\pre-commit
```

### In Git Bash or WSL (Bash)

```bash
# Run the helper script
./run_git_hook.sh pre-commit

# Or directly run the hook
.git/hooks/pre-commit
```

## Common Issues and Solutions

### "command not found" Error

When you see:
```
.git\hooks\pre-commit
bash: .githookspre-commit: command not found
```

**Solution**: In Bash environments, use forward slashes:
```bash
.git/hooks/pre-commit
```

### "Permission denied" Error

When you see:
```
.git/hooks/pre-commit: Permission denied
```

**Solution**: Make the hook executable:
```bash
chmod +x .git/hooks/pre-commit
```
or use the helper script which handles this automatically:
```bash
./run_git_hook.sh pre-commit
```

### "not a directory" Error

When you see:
```
cd: .git/hooks: Not a directory
```

**Solution**: Ensure you're in the project root directory:
```bash
# In Bash
goto_project
./run_git_hook.sh pre-commit

# In Windows CMD
cd /d C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0
run_git_hook.bat pre-commit
```

## Installing Custom Git Hooks

To install custom Git hooks:

1. **In Windows CMD**:
```cmd
install_git_hooks.bat
```

2. **In Bash**:
```bash
chmod +x pre-commit
cp pre-commit .git/hooks/
```

## Bypassing Git Hooks

For cases when you need to bypass the hooks:

```bash
# Skip pre-commit hook
git commit --no-verify -m "Your commit message"
```

## Checking Hook Status

To check if hooks are properly installed:

```bash
# List all hooks
ls -la .git/hooks/

# Check if pre-commit is executable
ls -l .git/hooks/pre-commit
```

## Troubleshooting

1. **Hook not executing**: Make sure the hook file has execute permissions
2. **Incorrect path**: Ensure you're in the project root directory
3. **Line ending issues**: Use LF (not CRLF) for hook scripts
4. **Syntax errors**: Check the hook script for syntax errors
