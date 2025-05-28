@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/goto_project.bat
REM Quick navigation script for DOCX RTM Automation project

echo DOCX RTM Automation Project Navigator
echo =====================================

REM Go to project directory
cd /d "C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0"
echo Current directory: %CD%

REM Display available commands
echo.
echo Available commands:
echo 1. run.bat help        - Show run commands
echo 2. fix_debugger.bat    - Fix debugger issues
echo 3. project_setup.bat   - Setup project environment
echo.
echo Git hooks can be found in .git\hooks directory
echo.

REM Check for Git
where git >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Git status:
    git status
    echo.
    echo Use 'git hooks' to manage Git hooks
) else (
    echo Git not found. Install Git to use version control features.
)

REM Set up command prompt to stay in this directory
echo Type 'exit' to close this window.
cmd /k