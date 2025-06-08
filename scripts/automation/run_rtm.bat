@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/run_rtm.bat

REM RTM Generation Script (Windows)

REM Display help if requested
if "%1"=="-h" goto :help
if "%1"=="--help" goto :help

REM Set default options
set DEBUG=
set FORMATS=json yaml markdown
set INPUT=
set OUTPUT=output
set CONFIG=

REM Parse arguments
:parse
if "%1"=="" goto :run
if "%1"=="-d" (
  set DEBUG=--debug
  shift
  goto :parse
)
if "%1"=="--debug" (
  set DEBUG=--debug
  shift
  goto :parse
)
if "%1"=="-f" (
  set FORMATS=%2
  REM Replace commas with spaces in formats
  set FORMATS=%FORMATS:,= %
  shift
  shift
  goto :parse
)
if "%1"=="-i" (
  set INPUT=--input %2
  shift
  shift
  goto :parse
)
if "%1"=="-o" (
  set OUTPUT=%2
  shift
  shift
  goto :parse
)
if "%1"=="-c" (
  set CONFIG=--config %2
  shift
  shift
  goto :parse
)

echo Unknown option: %1
exit /b 1

:run
REM Run RTM generation
echo Running RTM generation...
python scripts/SRC_Master.py rtm --output-dir "%OUTPUT%" --format %FORMATS% %INPUT% %CONFIG% %DEBUG%

REM Check exit code
if %ERRORLEVEL% EQU 0 (
  echo RTM generation completed successfully!
) else (
  echo RTM generation failed!
  exit /b 1
)
exit /b 0

:help
echo Usage: run_rtm.bat [OPTIONS]
echo.
echo Options:
echo   -h, --help     Show this help message and exit
echo   -d, --debug    Enable debug output
echo   -f FORMAT      Output formats (json,yaml,markdown)
echo   -i INPUT       Input file(s)
echo   -o OUTPUT      Output directory
echo   -c CONFIG      Configuration file
echo.
exit /b 0