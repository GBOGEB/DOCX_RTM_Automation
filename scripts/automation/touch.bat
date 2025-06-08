@echo off
REM Create a new empty file with the specified name

REM Check if a filename is provided
if "%~1"=="" (
    echo Usage: touch.bat <filename>
    exit /b 1
)

REM Create an empty file
type nul > "%~1"

REM Confirm the file creation
echo File "%~1" has been created.