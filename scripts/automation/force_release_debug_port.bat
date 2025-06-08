@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/run_force_release_debug_port.bat
REM Wrapper script to run force_release_debug_port.bat

echo Launching Force Release Debug Port Tool...
echo.

REM Check if the original file exists
if exist "%~dp0force_release_debug_port.bat" (
    call "%~dp0force_release_debug_port.bat"
) else (
    echo ERROR: force_release_debug_port.bat not found.
    echo This file should be in the same directory.
    echo.
    echo Current directory: %CD%
    echo Script location: %~dp0

    echo.
    echo Files in current directory:
    dir /b "%~dp0"*.bat

    pause
)