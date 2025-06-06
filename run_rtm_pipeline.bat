@echo off
REM Run RTM Pipeline Script

REM Set environment variables
set SCRIPT_DIR=%~dp0
set LOG_FILE=%SCRIPT_DIR%rtm_pipeline.log

REM Log start time
echo Starting RTM Pipeline at %date% %time% > %LOG_FILE%

REM Example: Activate Python environment
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

REM Run the RTM pipeline script
python "%SCRIPT_DIR%rtm_pipeline.py" >> %LOG_FILE% 2>&1

REM Check for errors
if %ERRORLEVEL% NEQ 0 (
    echo RTM Pipeline failed. Check the log file for details. >> %LOG_FILE%
    exit /b %ERRORLEVEL%
)

REM Log completion
echo RTM Pipeline completed successfully at %date% %time% >> %LOG_FILE%
exit /b 0