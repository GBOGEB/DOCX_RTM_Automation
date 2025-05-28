@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/project_setup.bat
REM Project Setup and Navigation Helper

echo =================================================
echo DOCX RTM Automation Project Environment Setup
echo =================================================

REM Set project directory
set PROJECT_DIR=%~dp0
set PROJECT_DIR=%PROJECT_DIR:~0,-1%
echo Project directory: %PROJECT_DIR%

REM Create instruction files for different shells
echo Creating navigation instruction files...

REM For CMD/PowerShell
(
    echo @echo off
    echo REM How to navigate to the project directory in Windows Command Prompt
    echo.
    echo cd /d "%PROJECT_DIR%"
    echo.
    echo REM Common commands:
    echo REM run.bat help - Show available commands
    echo REM setup_venv.bat - Set up Python virtual environment
    echo REM fix_debugger.bat - Fix debugging issues
) > "%PROJECT_DIR%\cmd_navigation.txt"

REM For Git Bash / WSL
(
    echo "# How to navigate to the project directory in Git Bash / WSL"
    echo ""
    echo "# Use forward slashes instead of backslashes:"
    echo "cd \"%PROJECT_DIR:\=/%\""
    echo ""
    echo "# Or try this alternative format:"
    echo "cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0"
    echo ""
    echo "# Common commands:"
    echo "# ./run.sh help - Show available commands"
    echo "# bash setup_venv.sh - Set up Python virtual environment"
    echo "# bash run_tests.sh - Run tests"
) > "%PROJECT_DIR%\bash_navigation.txt"

echo.
echo =================================================
echo Navigation Instructions:
echo =================================================
echo.
echo 1. For Windows Command Prompt / PowerShell:
echo    cd /d "%PROJECT_DIR%"
echo.
echo 2. For Git Bash / WSL:
echo    cd "%PROJECT_DIR:\=/%"
echo    or
echo    cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0
echo.
echo For more details:
echo - See cmd_navigation.txt for Windows CMD instructions
echo - See bash_navigation.txt for Git Bash/WSL instructions
echo.

REM Check Python and create/activate virtual environment if it exists
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Python found. Checking for virtual environment...

    if exist .venv\Scripts\activate.bat (
        echo Virtual environment exists. You can activate it with:
        echo   .venv\Scripts\activate.bat  [Windows CMD]
        echo   source .venv/Scripts/activate  [Git Bash/WSL]
    ) else (
        echo No virtual environment found. Create one with:
        echo   python -m venv .venv
    )
) else (
    echo Python not found in PATH. Please install Python.
)

echo.
echo =================================================
pause