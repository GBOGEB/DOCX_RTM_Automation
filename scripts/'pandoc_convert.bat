'pandoc_convert.bat
@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/scripts/pandoc_convert.bat
REM Enhanced Pandoc conversion script for Windows

setlocal enabledelayedexpansion

REM Default settings
set LUA_FILTER=config\extend_headings.lua
set TOC_DEPTH=6
set NUMBER_SECTIONS=true
set EXTRACT_RTM=true
set TOC=--toc

REM Parse arguments
:arg_loop
if "%~1" == "" goto arg_done
if "%~1" == "--help" (
    echo Usage: %0 [options] ^<input_file^> ^<output_file^>
    echo.
    echo Options:
    echo   --no-toc           Disable table of contents
    echo   --toc-depth N      Set TOC depth (default: 6^)
    echo   --no-numbers       Disable section numbering
    echo   --filter FILE      Use custom Lua filter
    echo   --no-rtm           Disable RTM extraction
    echo   --rtm-output FILE  Specify RTM output file
    echo   --help             Show this help message
    echo.
    echo Example:
    echo   %0 input\doc.docx output\doc.md
    echo   %0 --no-toc --filter my_filter.lua input\doc.docx output\doc.md
    exit /b 0
) else if "%~1" == "--no-toc" (
    set TOC=
    shift
) else if "%~1" == "--toc-depth" (
    set TOC_DEPTH=%~2
    shift
    shift
) else if "%~1" == "--no-numbers" (
    set NUMBER_SECTIONS=false
    shift
) else if "%~1" == "--filter" (
    set LUA_FILTER=%~2
    shift
    shift
) else if "%~1" == "--no-rtm" (
    set EXTRACT_RTM=false
    shift
) else if "%~1" == "--rtm-output" (
    set RTM_OUTPUT=%~2
    shift
    shift
) else (
    if not defined INPUT_FILE (
        set INPUT_FILE