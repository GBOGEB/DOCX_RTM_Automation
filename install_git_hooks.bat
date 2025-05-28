@echo off
REM Set the hooks directory
set HOOKS_DIR=.git/hooks

REM Check if the hooks directory exists
if not exist %HOOKS_DIR% (
    echo Git hooks directory does not exist. Ensure this is a Git repository.
    exit /b 1
)

REM Copy custom hooks to the hooks directory
echo Installing Git hooks...
copy /Y pre-commit %HOOKS_DIR%\pre-commit
copy /Y post-commit %HOOKS_DIR%\post-commit

REM Make hooks executable (if needed)
echo Making hooks executable...
attrib +x %HOOKS_DIR%\pre-commit
attrib +x %HOOKS_DIR%\post-commit

echo Git hooks installed successfully.
exit /b 0