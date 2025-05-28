# Navigation Guide for DOCX RTM Automation Project

This guide helps you navigate to the project directory from different shells.

## Windows Command Prompt (CMD)

```cmd
cd /d C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0
```

## PowerShell

```powershell
Set-Location -Path "C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0"
```

## Git Bash or WSL (Bash)

```bash
cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0
```

Note: In Bash, paths use forward slashes and the Windows drive letter becomes `/c/` instead of `C:\`

## Error: "cd: too many arguments"

If you're seeing this error, you're likely using the Windows CMD syntax (`cd /d`) in a Bash shell.

Instead of:
```bash
cd /d C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0
```

Use the proper Bash syntax:
```bash
cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0
```

## Quick Command Reference

| Action | CMD | PowerShell | Bash |
|--------|-----|------------|------|
| Navigate to dir | `cd /d path\to\dir` | `Set-Location path\to\dir` | `cd /c/path/to/dir` |
| List files | `dir` | `Get-ChildItem` or `dir` | `ls -la` |
| Run script | `script.bat` | `.\script.ps1` | `./script.sh` |
| Edit file | `notepad file.txt` | `notepad file.txt` | `nano file.txt` |
