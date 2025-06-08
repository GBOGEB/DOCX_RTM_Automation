@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/list_all_tools.bat
REM Lists all available batch tools and provides navigation help

cls
echo ==============================================
echo          RTM Automation Tools List
echo ==============================================
echo.
echo Current directory: %CD%
echo.

echo === Available Batch Files ===
dir /b *.bat

echo.
echo === Navigation Commands ===
echo cd /d C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0     - Go to project root
echo.

echo === How to run tools ===
echo 1. Make sure you're in the project root directory first.
echo 2. Type the name of the batch file to run it.
echo    Example: port_status_helper.bat
echo.
echo === Fix Recursion Errors ===
echo If you see "BATCH RECURSION exceeds STACK limits" errors:
echo 1. Close command prompt and open a new one
echo 2. Run CMD as administrator
echo 3. Navigate to project directory
echo 4. Run the tools directly without "run_" prefix
echo.

pause