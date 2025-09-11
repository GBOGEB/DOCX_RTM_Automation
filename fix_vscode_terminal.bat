@echo off
REM VS Code Git Bash Terminal Fix for Windows
REM This script fixes the common exit code 256 issue with Git Bash in VS Code

echo.
echo ============================================================
echo VS Code Git Bash Terminal Configuration Fix
echo ============================================================
echo.
echo This script will configure VS Code to properly use Git Bash
echo and fix the common "exit code 256" terminal error.
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python not found in PATH.
    echo Please install Python or add it to your PATH, then try again.
    pause
    exit /b 1
)

echo 🐍 Python found, running VS Code terminal configuration script...
echo.

REM Run the Python configuration script
python scripts/fix_vscode_terminal.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Configuration completed successfully!
    echo.
    echo 📝 Next steps:
    echo   1. Restart VS Code or reload the window
    echo   2. Open a new terminal (Ctrl+Shift+^`)
    echo   3. Git Bash should now work properly
    echo.
    echo 💡 If you still have issues, see docs/VSCODE_TERMINAL_FIX.md
    echo    for detailed troubleshooting steps.
) else (
    echo.
    echo ❌ Configuration failed. Please check the error messages above.
    echo 💡 Try running VS Code as Administrator if permission issues occur.
)

echo.
echo ============================================================
pause