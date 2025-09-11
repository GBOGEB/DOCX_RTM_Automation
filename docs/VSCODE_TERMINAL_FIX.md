# VS Code Git Bash Terminal Fix

## Problem

VS Code's integrated terminal fails to start Git Bash with the error:
```
The terminal process "C:\Program Files\Git\bin\bash.exe '--login', '-i'" terminated with exit code: 256.
```

## Solution

This repository provides an automated fix for the VS Code Git Bash terminal configuration issue.

### Quick Fix

1. **Automatic Configuration** (Recommended):
   ```bash
   python scripts/fix_vscode_terminal.py
   ```

2. **Manual Configuration**:
   The `.vscode/settings.json` file in this repository contains the correct terminal configuration.

### What the Fix Does

The fix configures VS Code with multiple Git Bash terminal profiles to handle different installation scenarios:

- **Primary Git Bash**: `C:\Program Files\Git\git-bash.exe`
- **Alternative Bash**: `C:\Program Files\Git\bin\bash.exe` with proper args
- **User Installation**: For portable Git installations
- **32-bit Installation**: For older systems
- **Fallback Options**: Additional paths for edge cases

### Configuration Details

The fix adds these settings to VS Code:

```json
{
  "terminal.integrated.profiles.windows": {
    "Git Bash": {
      "path": "C:\\Program Files\\Git\\git-bash.exe",
      "icon": "terminal-bash"
    },
    "Git Bash (Alternative)": {
      "path": "C:\\Program Files\\Git\\bin\\bash.exe",
      "args": ["--login", "-i"],
      "icon": "terminal-bash"
    }
  },
  "terminal.integrated.defaultProfile.windows": "Git Bash",
  "terminal.integrated.detectLocale": "off",
  "terminal.integrated.shell.windows": null,
  "terminal.integrated.shellArgs.windows": null
}
```

### Key Features

1. **Auto-Detection**: Automatically finds your Git Bash installation
2. **Multiple Fallbacks**: Provides several terminal profile options
3. **Safe Configuration**: Creates backups before making changes
4. **Cross-Platform**: Works on Windows, with graceful handling on other OS

### Troubleshooting

If the terminal still doesn't work after applying the fix:

#### 1. Verify Git Bash Installation
```cmd
# Open Command Prompt and test:
"C:\Program Files\Git\git-bash.exe"
```

#### 2. Check VS Code Settings
- Open `File → Preferences → Settings`
- Search for "terminal.integrated.profiles.windows"
- Verify the Git Bash profile exists

#### 3. Try Different Profile
- In VS Code terminal dropdown, try different Git Bash profiles
- Use the one that works for your system

#### 4. Advanced Debugging
- Press `Ctrl+Shift+P` → "Developer: Toggle Developer Tools"
- Check Console tab for specific error messages
- Look for path or permission issues

#### 5. Alternative Paths
If your Git is installed elsewhere, update the path in settings:
```json
{
  "terminal.integrated.profiles.windows": {
    "Git Bash": {
      "path": "C:\\Your\\Custom\\Path\\To\\git-bash.exe"
    }
  }
}
```

### Common Installation Paths

The fix checks these common Git installation locations:

| Location | Path |
|----------|------|
| Standard 64-bit | `C:\Program Files\Git\git-bash.exe` |
| Standard 32-bit | `C:\Program Files (x86)\Git\git-bash.exe` |
| User Installation | `%USERPROFILE%\AppData\Local\Programs\Git\git-bash.exe` |
| Alternative | `C:\Program Files\Git\bin\bash.exe` |
| Portable | Custom path as specified during installation |

### Running the Auto-Fix

```bash
# From the repository root:
cd /path/to/DOCX_RTM_Automation
python scripts/fix_vscode_terminal.py
```

### Expected Output

```
🚀 VS Code Git Bash Terminal Configuration Fixer
============================================================
This script fixes the common VS Code terminal exit code 256 issue
by configuring proper Git Bash terminal profiles.

🔧 Fixing VS Code Terminal Configuration
==================================================
📋 Backup created: .vscode/settings.json.backup_20240101_120000
🔍 Detecting Git Bash installation...
✅ Found Git Bash at: C:\Program Files\Git\git-bash.exe
✅ VS Code settings updated: .vscode/settings.json

📊 Configuration Summary:
------------------------------
🎯 Primary Git Bash: C:\Program Files\Git\git-bash.exe
🏠 Default terminal: Git Bash
📝 Terminal profiles created: 6
   • Git Bash
   • Git Bash (bash.exe)
   • Git Bash (User Install)
   • Git Bash (x86)
   • PowerShell
   • Command Prompt

🛠️  Troubleshooting Tips:
   • If terminal still fails, try 'Developer: Reload Window' in VS Code
   • Check VS Code Developer Tools console for specific errors
   • Ensure Git for Windows is properly installed
   • Try running VS Code as Administrator if permission issues persist

🎉 Configuration completed successfully!
💡 Restart VS Code or reload the window to apply changes.
```

### After Applying the Fix

1. **Restart VS Code** or use `Ctrl+Shift+P` → "Developer: Reload Window"
2. **Open a new terminal** (`Ctrl+Shift+`` ` or `Terminal → New Terminal`)
3. **Verify Git Bash is working**:
   ```bash
   echo $SHELL
   git --version
   pwd
   ```

### Files Modified

- `.vscode/settings.json` - Main VS Code configuration
- Backup file created with timestamp (e.g., `.vscode/settings.json.backup_20240101_120000`)

### Reverting Changes

If you need to revert the changes:
```bash
# Replace with your actual backup file name
cp .vscode/settings.json.backup_20240101_120000 .vscode/settings.json
```

---

## Additional Help

If you continue to experience issues, check:

1. **Git for Windows Installation**: Download latest from [git-scm.com](https://git-scm.com/download/win)
2. **VS Code Updates**: Ensure you have the latest VS Code version
3. **Windows Updates**: Some terminal issues are resolved with Windows updates
4. **Antivirus Software**: Some antivirus programs block terminal execution

For more help, check the [VS Code Terminal Documentation](https://code.visualstudio.com/docs/editor/integrated-terminal).