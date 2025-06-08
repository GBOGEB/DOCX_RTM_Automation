@echo off
title RTM Debug Console - Simple Mode
color 0B

echo.
echo ================================================================
echo                   RTM DEBUG CONSOLE - SIMPLE MODE
echo ================================================================
echo.
echo This script runs the debug console without VS Code interference
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if debug_console.py exists
if not exist "debug_console.py" (
    echo ERROR: debug_console.py not found
    echo Please ensure you're in the correct directory
    pause
    exit /b 1
)

echo Starting Debug Console...
echo.

REM Run without debugger
python debug_console.py

echo.
echo Debug Console finished.
pause
