@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/start_here.bat
REM Simple starter script for RTM Automation

echo ================================================
echo         RTM Automation Project Tools
echo ================================================
echo.
echo Current directory: %CD%
echo.

echo Available tools:
echo 1. Run RTM Visualizer
echo 2. Extract RTM Data
echo 3. Debug Tools
echo 4. Check Python Environment
echo 5. Exit
echo.
set /p choice=Enter your choice (1-5):

if "%choice%"=="1" (
    echo.
    echo Running RTM Visualizer...
    python src/visualizers/rtm_visualizer.py
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo Running RTM Extractor...
    python src/extractors/extract_rtm.py
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo Debug Tools:
    echo.
    echo A. Debug Simple Script
    echo B. Check Port Status
    echo C. Force Release Port
    echo D. Back to Main Menu
    echo.
    set /p debug_choice=Enter debug option (A-D):

    if /I "%debug_choice%"=="A" (
        python debug_simple_dynamic.py
    ) else if /I "%debug_choice%"=="B" (
        python port_manager.py --list
        pause
    ) else if /I "%debug_choice%"=="C" (
        python release_port.py 5678 --force
        pause
    ) else (
        goto :start
    )
    goto :end
)

if "%choice%"=="4" (
    echo.
    echo Python Environment:
    python --version
    echo.
    echo Python Path:
    python -c "import sys; print('\n'.join(sys.path))"
    echo.
    echo Installed Packages:
    pip list
    pause
    goto :end
)

if "%choice%"=="5" (
    echo.
    echo Exiting...
    goto :end
)

echo.
echo Invalid choice! Please try again.
pause

:end
echo.
echo Run this script again by typing: start_here.bat
echo.