@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/fix_debugger.bat
REM Fix Debugger Script - Automation v1.0

REM Set environment variables
setlocal enabledelayedexpansion

REM Define log file
set "LOG_FILE=%~dp0debugger_fix.log"

REM Log start time
echo Fix Debugger Script started at %date% %time% > "%LOG_FILE%"

REM Perform fix operations
echo Running debugger fix script for Windows...

echo.
echo 1. Checking for running Python processes...
tasklist /FI "IMAGENAME eq python.exe" /FO TABLE
tasklist /FI "IMAGENAME eq pythonw.exe" /FO TABLE

echo.
echo 2. Killing any running Python debug sessions...
taskkill /F /IM python.exe /T 2>NUL
taskkill /F /IM pythonw.exe /T 2>NUL
echo Done.

echo.
echo 3. Checking if debugpy is installed in the virtual environment...
if exist .venv\Scripts\python.exe (
    echo Using project virtual environment...
    .venv\Scripts\python.exe -c "import debugpy; print('debugpy version:', debugpy.__version__)" 2>NUL
    if ERRORLEVEL 1 (
        echo Installing debugpy...
        .venv\Scripts\pip.exe install debugpy
    )
) else (
    echo Project virtual environment not found at .venv
    echo Please run setup_venv.sh first
)

echo.
echo 4. Testing port availability...
echo Checking port 5678 (default debug port)...
netstat -an | find "5678"
if ERRORLEVEL 1 (
    echo Port 5678 appears to be available
) else (
    echo Port 5678 is already in use
    echo Try using a different port for debugging
)

echo.
echo 5. Running diagnostics...
if exist debug_helpers.py (
    if exist .venv\Scripts\python.exe (
        .venv\Scripts\python.exe debug_helpers.py
    ) else (
        python debug_helpers.py
    )
) else (
    echo debug_helpers.py not found - skipping diagnostics
)

echo.
echo Fix completed. Try debugging again.
echo If you still encounter issues, try restarting VS Code.
pause

REM Log completion
echo Fix Debugger Script completed at %date% %time% >> "%LOG_FILE%"
echo Debugger fix completed successfully.
exit /b 0