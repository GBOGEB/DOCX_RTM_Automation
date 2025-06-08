@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/install_simple_hook.bat
REM Install a simple pre-commit hook without using the pre-commit framework

echo ===============================================
echo Installing Simple Pre-commit Hook
echo ===============================================
echo.

REM Check if .git directory exists
if not exist .git (
    echo Error: Not in a Git repository root directory
    echo Please run this script from the root of your project
    exit /b 1
)

REM Make sure hooks directory exists
if not exist .git\hooks mkdir .git\hooks

REM Create the pre-commit hook wrapper
echo Creating pre-commit hook...
(
    echo #!/bin/sh
    echo # Simple pre-commit hook without pre-commit framework
    echo.
    echo # Run the Python hook script
    echo python "%~dp0simple_pre_commit_hook.py"
    echo exit $?
) > .git\hooks\pre-commit

echo Creating Windows-compatible hook...
(
    echo @echo off
    echo REM Windows pre-commit hook wrapper
    echo.
    echo python "%~dp0simple_pre_commit_hook.py"
    echo exit /b %%ERRORLEVEL%%
) > .git\hooks\pre-commit.bat

REM Clean up any pre-commit cache directories
echo Cleaning up pre-commit cache...

if exist .pre-commit-cache (
    echo Removing .pre-commit-cache directory...
    rmdir /s /q .pre-commit-cache
)

if exist "%USERPROFILE%\new-pre-commit-cache" (
    echo Removing user pre-commit cache directory...
    rmdir /s /q "%USERPROFILE%\new-pre-commit-cache"
)

REM Disable any existing pre-commit configuration
if exist .pre-commit-config.yaml (
    echo Backing up .pre-commit-config.yaml...
    move .pre-commit-config.yaml .pre-commit-config.yaml.bak
    echo Moved .pre-commit-config.yaml to .pre-commit-config.yaml.bak
)

echo.
echo Simple pre-commit hook installed successfully!
echo.
echo To test the hook:
echo   git add .
echo   git commit -m "Test commit"
echo.
echo If you need to bypass the hook:
echo   git commit -m "Your message" --no-verify
echo.
echo To uninstall this hook:
echo   del .git\hooks\pre-commit
echo.

pause