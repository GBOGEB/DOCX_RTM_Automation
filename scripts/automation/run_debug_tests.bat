@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/run_debug_tests.bat
REM Run comprehensive debug tests in different modes

echo ===========================
echo Debugging Test Runner
echo ===========================
echo.

REM Check if debugpy is installed
python -c "import debugpy" >nul 2>&1
if %errorLevel% neq 0 (
    echo Debugpy is not installed. Installing...
    pip install debugpy
    if %errorLevel% neq 0 (
        echo Failed to install debugpy.
        echo Please install it manually: pip install debugpy
        pause
        exit /b 1
    )
)

echo.
echo Choose a debugging test mode:
echo 1. Regular mode (no debugging)
echo 2. Debug with debugger enabled (manual attach)
echo 3. Debug with wait for debugger (attach before continuing)
echo.
set /p mode="Enter mode (1-3): "

if "%mode%"=="1" (
    echo.
    echo Running in regular mode...
    python debug_comprehensive.py
) else if "%mode%"=="2" (
    echo.
    echo Running with debugger enabled...
    set ENABLE_DEBUGGER=true
    python debug_comprehensive.py
    set ENABLE_DEBUGGER=
) else if "%mode%"=="3" (
    echo.
    echo Running with wait for debugger...
    python debug_comprehensive.py --wait-for-debugger
) else (
    echo.
    echo Invalid option. Please run again and select 1-3.
    pause
    exit /b 1
)

echo.
echo Test completed.
pause