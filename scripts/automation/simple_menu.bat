@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/simple_menu.bat
REM Ultra-simple menu script in case start_here.bat doesn't work

echo RTM Automation - Simple Menu
echo ---------------------------
echo.

:menu
echo Choose an option:
echo 1. Check Python version and path
echo 2. List available Python scripts
echo 3. List available batch files
echo 4. Run RTM visualizer
echo 5. Run port manager
echo 6. Exit
echo.

set /p option=Select option (1-6):

if "%option%"=="1" (
    echo.
    python --version
    echo.
    python -c "import sys; print('PYTHONPATH:'); print('\n'.join(sys.path))"
    echo.
    pause
    cls
    goto :menu
)

if "%option%"=="2" (
    echo.
    echo Available Python Scripts:
    dir /b /s *.py | findstr /v "__pycache__" | findstr /v "\.venv"
    echo.
    pause
    cls
    goto :menu
)

if "%option%"=="3" (
    echo.
    echo Available Batch Files:
    dir /b *.bat
    echo.
    pause
    cls
    goto :menu
)

if "%option%"=="4" (
    echo.
    echo Running RTM Visualizer
    echo.
    python src/visualizers/rtm_visualizer.py
    echo.
    pause
    cls
    goto :menu
)

if "%option%"=="5" (
    echo.
    echo Running Port Manager
    echo.
    python port_manager.py --list
    echo.
    pause
    cls
    goto :menu
)

if "%option%"=="6" (
    echo.
    echo Goodbye!
    exit /b 0
)

echo.
echo Invalid option. Please try again.
echo.
pause
cls
goto :menu