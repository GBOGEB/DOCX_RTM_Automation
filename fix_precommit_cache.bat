@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/fix_precommit_cache.bat
REM Fix pre-commit cache issues

echo ====================================
echo Pre-commit Cache Fix Tool
echo ====================================
echo.

REM Set environment variables
setlocal enabledelayedexpansion

REM Define the problematic cache directories
set "USER_CACHE_DIR=%USERPROFILE%\new-pre-commit-cache"
set "PROJECT_CACHE_DIR=%~dp0.pre-commit-cache"

echo Current pre-commit cache directories:
echo - User cache: %USER_CACHE_DIR%
echo - Project cache: %PROJECT_CACHE_DIR%
echo.

echo Step 1: Cleaning up existing cache directories...

REM Check if the user cache directory exists
if exist "%USER_CACHE_DIR%" (
    echo Found user cache directory, removing...
    rmdir /S /Q "%USER_CACHE_DIR%" 2>nul
    if !ERRORLEVEL! NEQ 0 (
        echo WARNING: Unable to remove %USER_CACHE_DIR%
        echo You may need to delete it manually.
    ) else (
        echo User cache directory removed successfully.
    )
) else (
    echo User cache directory not found.
)

REM Check if the project cache directory exists
if exist "%PROJECT_CACHE_DIR%" (
    echo Found project cache directory, removing...
    rmdir /S /Q "%PROJECT_CACHE_DIR%" 2>nul
    if !ERRORLEVEL! NEQ 0 (
        echo WARNING: Unable to remove %PROJECT_CACHE_DIR%
        echo You may need to delete it manually.
    ) else (
        echo Project cache directory removed successfully.
    )
) else (
    echo Project cache directory not found.
)

echo.
echo Step 2: Configuring pre-commit to use project-local cache...

REM Create .pre-commit-config.yaml if it doesn't exist
if not exist "%~dp0.pre-commit-config.yaml" (
    echo .pre-commit-config.yaml not found, creating basic configuration...
    (
        echo # Pre-commit Git hooks configuration
        echo # See https://pre-commit.com for more information
        echo.
        echo repos:
        echo -   repo: https://github.com/pre-commit/pre-commit-hooks
        echo     rev: v4.4.0
        echo     hooks:
        echo     -   id: trailing-whitespace
        echo     -   id: end-of-file-fixer
        echo     -   id: check-yaml
        echo     -   id: check-added-large-files
    ) > "%~dp0.pre-commit-config.yaml"
)

REM Create a pre-commit environment file to use local cache
echo PRE_COMMIT_HOME=%~dp0.pre-commit-cache > "%~dp0.env"
echo Created .env file with local cache configuration.

echo.
echo Step 3: Testing pre-commit setup...

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Python found, checking pre-commit installation...

    REM Check if pre-commit is installed
    python -m pip show pre-commit >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo Pre-commit is installed, running pre-commit clean...
        python -m pre-commit clean

        echo.
        echo Installing pre-commit hooks...
        python -m pre-commit install

        echo.
        echo Testing pre-commit autoupdate...
        python -m pre-commit autoupdate
    ) else (
        echo Pre-commit not installed. Installing...
        python -m pip install pre-commit

        echo.
        echo Installing pre-commit hooks...
        python -m pre-commit install
    )
) else (
    echo Python not found. Please install Python and pre-commit manually.
)

echo.
echo Fix completed. You can now try running pre-commit again with:
echo   ./run_git_hook.sh pre-commit
echo   or
echo   .\.git\hooks\pre-commit
echo.
echo If issues persist, try:
echo 1. Restarting your terminal/command prompt
echo 2. Using 'pre-commit run --all-files' directly
echo 3. Checking the log at %USERPROFILE%\new-pre-commit-cache\pre-commit.log
echo.

pause