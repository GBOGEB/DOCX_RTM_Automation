@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/go_to_project.bat
REM Simple navigation helper

cd /d C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0
echo You are now in the RTM Automation project directory:
echo %CD%
echo.

echo Available batch files:
dir /b *.bat

echo.
echo Type the name of the batch file to run it.
echo For example: start_here.bat
echo.