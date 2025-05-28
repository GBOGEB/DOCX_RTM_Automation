@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/run_git_hook.bat
REM Helper script for running Git hooks in Windows

echo Git Hook Runner - Run Git hooks manually

REM Check if argument is provided
if "%~1"=="" (
    echo.
    echo Usage: run_git_hook.bat HOOK_NAME
    echo.
    echo Available hooks:
    if exist .git\hooks (
        for %%F in (.git\hooks\*) do (
            if not "%%~xF"==".sample" echo   - %%~nxF
        )
    ) else (
        echo   No hooks available (.git\hooks directory not found^)
    )
    echo.
    echo Examples:
    echo   run_git_hook.bat pre-commit
    echo   run_git_hook.bat post-commit
    exit /b 0
)

REM Check if .git directory exists
if not exist .git (
    echo Error: Not in git repository root directory
    echo Please run this script from the root of your git repository
    exit /b 1
)

REM Check if hook exists
if exist .git\hooks\%1 (
    echo Running %1 hook...

    REM For pre-commit hook, we need special handling
    if "%~1"=="pre-commit" (
        call :RunPreCommitHook
    ) else (
        REM For other hooks, run directly
        .git\hooks\%1
    )

    exit /b %ERRORLEVEL%
) else (
    echo Error: %1 hook not found
    echo Hook should be located at: .git\hooks\%1
    exit /b 1
)

:RunPreCommitHook
REM Special handling for pre-commit hook
where bash >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    REM If bash is available, use it to run the hook
    bash -c "./.git/hooks/pre-commit"
) else (
    REM Otherwise try running directly
    .git\hooks\pre-commit

    REM If error, try with cmd /c
    if %ERRORLEVEL% NEQ 0 (
        echo Trying alternative execution method...
        cmd /c .git\hooks\pre-commit
    )
)
exit /b %ERRORLEVEL%