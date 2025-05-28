@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/port_status_helper.bat
REM Helper script to check and manage debug ports WITHOUT recursion

echo =========================================
echo Debug Port Status and Management Tool
echo =========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python not found! Please install Python or check your PATH.
    pause
    exit /b 1
)

REM WARNING: No recursion or goto :MENU loops to avoid stack overflow
echo Choose an option:
echo 1. Check status of all debug ports
echo 2. Release port 5678 (main debug port)
echo 3. Find available port for debugging
echo 4. Run debugger with dynamic port selection
echo 5. Kill process using a specific port
echo 6. Exit
echo.

set /p option=Enter option (1-6):

if "%option%"=="1" (
    echo.
    echo Checking all debug ports...
    python port_manager.py --list
    pause
)

if "%option%"=="2" (
    echo.
    echo Attempting to release port 5678...
    python port_manager.py --release 5678
    pause
)

if "%option%"=="3" (
    echo.
    echo Finding available debug port...
    set /p start_port=Enter starting port number [5678]:
    if "%start_port%"=="" set start_port=5678
    python port_manager.py --find %start_port%
    pause
)

if "%option%"=="4" (
    echo.
    echo Running debugger with dynamic port selection...
    echo.
    echo This will:
    echo 1. Find an available port
    echo 2. Start a debug server on that port
    echo 3. Wait for VS Code to connect
    echo.
    echo Make sure to update your launch.json with the displayed port number
    echo.
    echo Press any key to start the debug server...
    pause >nul
    python debug_simple_dynamic.py
    pause
)

if "%option%"=="5" (
    echo.
    set /p port_to_kill=Enter port number to release:
    if "%port_to_kill%"=="" (
        echo No port specified
    ) else (
        echo Attempting to release port %port_to_kill%...
        python port_manager.py --release %port_to_kill%
    )
    pause
)

if "%option%"=="6" (
    echo Exiting...
    exit /b 0
)

echo.
echo Tool completed. To run again, type: port_status_helper.bat
echo.

pause