@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/scripts/pandoc_convert.bat
REM Enhanced Pandoc conversion script for Windows

setlocal enabledelayedexpansion

REM Default settings
REM Assuming this script is in 'scripts' and config is in project root's 'config' folder
set LUA_FILTER=..\config\extend_headings.lua
set TOC_DEPTH=6
set NUMBER_SECTIONS=true
set EXTRACT_RTM=true
set TEMPLATE_DIR=templates
set CSS_TEMPLATE=templates\default.css
set MD_TEMPLATE=templates\template.md

REM Parse arguments
:arg_loop
if "%~1" == "" goto arg_done
if "%~1" == "--help" (
    call :show_help
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
) else if "%~1" == "--template" (
    set MD_TEMPLATE=%~2
    shift
    shift
) else if "%~1" == "--css" (
    set CSS_TEMPLATE=%~2
    shift
    shift
) else (
    REM Assume this is input/output file
    if not defined INPUT_FILE (
        set INPUT_FILE=%~1
    ) else if not defined OUTPUT_FILE (
        set OUTPUT_FILE=%~1
    ) else (
        echo Error: Too many arguments.
        call :show_help
        exit /b 1
    )
    shift
    goto arg_loop
)
goto arg_loop

:show_help
echo Usage: %0 [options] ^<input_file^> ^<output_file^>
echo.
echo Options:
echo   --no-toc           Disable table of contents
echo   --toc-depth N      Set TOC depth (default: 6)
echo   --no-numbers       Disable section numbering
echo   --filter FILE      Use custom Lua filter
echo   --no-rtm           Disable RTM extraction
echo   --rtm-output FILE  Specify RTM output file
echo   --template FILE    Use specific Markdown template
echo   --css FILE         Use specific CSS template
echo   --help             Show this help message
echo.
echo Example:
echo   %0 input\doc.docx output\doc.md
echo   %0 --no-toc --filter my_filter.lua input\doc.docx output\doc.md
exit /b 0

:arg_done

REM Check required arguments
if not defined INPUT_FILE (
    echo Error: Input file is required.
    call :show_help
    exit /b 1
)

if not defined OUTPUT_FILE (
    echo Error: Output file is required.
    call :show_help
    exit /b 1
)

REM Check if input file exists
if not exist "%INPUT_FILE%" (
    echo Error: Input file not found: %INPUT_FILE%
    exit /b 1
)

REM Create templates directory if it doesn't exist
if not exist "%TEMPLATE_DIR%" (
    mkdir "%TEMPLATE_DIR%"

    REM Create default CSS template
    echo ^/* Default CSS template for Markdown output *^/ > "%CSS_TEMPLATE%"
    echo body { font-family: Calibri, Arial, sans-serif; margin: 3em; } >> "%CSS_TEMPLATE%"
    echo h1 { color: #004286; font-size: 20pt; margin-top: 24pt; page-break-before: always; } >> "%CSS_TEMPLATE%"
    echo h2 { color: #004286; font-size: 16pt; margin-top: 20pt; } >> "%CSS_TEMPLATE%"
    echo h3 { color: #004286; font-size: 14pt; margin-top: 18pt; } >> "%CSS_TEMPLATE%"
    echo h4 { color: #004286; font-size: 12pt; margin-top: 16pt; } >> "%CSS_TEMPLATE%"
    echo h5 { color: #004286; font-size: 11pt; margin-top: 14pt; font-style: italic; } >> "%CSS_TEMPLATE%"
    echo h6 { color: #004286; font-size: 11pt; margin-top: 14pt; font-style: italic; } >> "%CSS_TEMPLATE%"
    echo .requirement { background-color: #f6f8fa; border-left: 4px solid #004286; padding: 8px; margin: 12px 0; } >> "%CSS_TEMPLATE%"
    echo .note { background-color: #fff8dc; border-left: 4px solid #ffcc00; padding: 8px; margin: 12px 0; } >> "%CSS_TEMPLATE%"
    echo table { width: 100%%; border-collapse: collapse; margin: 16px 0; } >> "%CSS_TEMPLATE%"
    echo th { background-color: #f0f0f0; text-align: left; padding: 8px; border: 1px solid #ddd; } >> "%CSS_TEMPLATE%"
    echo td { padding: 8px; border: 1px solid #ddd; vertical-align: top; } >> "%CSS_TEMPLATE%"
    echo code { background-color: #f5f5f5; padding: 2px 4px; font-family: Consolas, monospace; } >> "%CSS_TEMPLATE%"
    echo .caption { font-style: italic; color: #666; text-align: center; margin-top: 4px; } >> "%CSS_TEMPLATE%"

    REM Create default Markdown template
    echo --- > "%MD_TEMPLATE%"
    echo title: "Document Title" >> "%MD_TEMPLATE%"
    echo author: "DOCX RTM Automation" >> "%MD_TEMPLATE%"
    echo date: "%date%" >> "%MD_TEMPLATE%"
    echo version: "1.0" >> "%MD_TEMPLATE%"
    echo toc-title: "Table of Contents" >> "%MD_TEMPLATE%"
    echo toc-depth: 6 >> "%MD_TEMPLATE%"
    echo fontsize: 11pt >> "%MD_TEMPLATE%"
    echo mainfont: "Calibri" >> "%MD_TEMPLATE%"
    echo sansfont: "Arial" >> "%MD_TEMPLATE%"
    echo monofont: "Consolas" >> "%MD_TEMPLATE%"
    echo header-includes: >> "%MD_TEMPLATE%"
    echo   - \definecolor{reqcolor}{RGB}{0, 67, 134} >> "%MD_TEMPLATE%"
    echo   - \definecolor{linkcolor}{RGB}{0, 123, 255} >> "%MD_TEMPLATE%"
    echo   - \definecolor{codebackground}{RGB}{245, 245, 245} >> "%MD_TEMPLATE%"
    echo   - \definecolor{headingcolor}{RGB}{33, 37, 41} >> "%MD_TEMPLATE%"
    echo   - \setlength{\parindent}{0pt} >> "%MD_TEMPLATE%"
    echo   - \setlength{\parskip}{12pt} >> "%MD_TEMPLATE%"
    echo headingcolor: headingcolor >> "%MD_TEMPLATE%"
    echo linkcolor: linkcolor >> "%MD_TEMPLATE%"
    echo colorlinks: true >> "%MD_TEMPLATE%"
    echo numbersections: true >> "%MD_TEMPLATE%"
    echo --- >> "%MD_TEMPLATE%"
    echo. >> "%MD_TEMPLATE%"
    echo ^<!-- Document styling references --^> >> "%MD_TEMPLATE%"
    echo ^<style^> >> "%MD_TEMPLATE%"
    echo h1 { color: #004286; font-size: 20pt; margin-top: 24pt; page-break-before: always; } >> "%MD_TEMPLATE%"
    echo h2 { color: #004286; font-size: 16pt; margin-top: 20pt; } >> "%MD_TEMPLATE%"
    echo h3 { color: #004286; font-size: 14pt; margin-top: 18pt; } >> "%MD_TEMPLATE%"
    echo h4 { color: #004286; font-size: 12pt; margin-top: 16pt; } >> "%MD_TEMPLATE%"
    echo h5 { color: #004286; font-size: 11pt; margin-top: 14pt; font-style: italic; } >> "%MD_TEMPLATE%"
    echo h6 { color: #004286; font-size: 11pt; margin-top: 14pt; font-style: italic; } >> "%MD_TEMPLATE%"
    echo .requirement { background-color: #f6f8fa; border-left: 4px solid #004286; padding: 8px; margin: 12px 0; } >> "%MD_TEMPLATE%"
    echo .note { background-color: #fff8dc; border-left: 4px solid #ffcc00; padding: 8px; margin: 12px 0; } >> "%MD_TEMPLATE%"
    echo .table { width: 100%%; border-collapse: collapse; margin: 16px 0; } >> "%MD_TEMPLATE%"
    echo .table th { background-color: #f0f0f0; text-align: left; padding: 8px; border: 1px solid #ddd; } >> "%MD_TEMPLATE%"
    echo .table td { padding: 8px; border: 1px solid #ddd; vertical-align: top; } >> "%MD_TEMPLATE%"
    echo code { background-color: #f5f5f5; padding: 2px 4px; font-family: "Consolas", monospace; } >> "%MD_TEMPLATE%"
    echo .caption { font-style: italic; color: #666; text-align: center; margin-top: 4px; } >> "%MD_TEMPLATE%"
    echo ^</style^> >> "%MD_TEMPLATE%"
    echo. >> "%MD_TEMPLATE%"
    echo $body$ >> "%MD_TEMPLATE%"

    echo Created template files in %TEMPLATE_DIR% directory
)

REM Prepare output directory
for %%F in ("%OUTPUT_FILE%") do set OUTPUT_DIR=%%~dpF
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

REM Build pandoc command
set PANDOC_CMD=pandoc "%INPUT_FILE%" -o "%OUTPUT_FILE%" --wrap=none

REM Add template if it exists
if exist "%MD_TEMPLATE%" (
    set PANDOC_CMD=!PANDOC_CMD! --template="%MD_TEMPLATE%"
)

REM Add CSS if it exists
if exist "%CSS_TEMPLATE%" (
    set PANDOC_CMD=!PANDOC_CMD! --css="%CSS_TEMPLATE%"
)

REM Add TOC if enabled
if defined TOC (
    set PANDOC_CMD=!PANDOC_CMD! --toc --toc-depth=%TOC_DEPTH%
)

REM Add section numbering if enabled
if "%NUMBER_SECTIONS%" == "true" (
    set PANDOC_CMD=!PANDOC_CMD! --number-sections
)

REM Add Lua filter if it exists
if exist "%LUA_FILTER%" (
    set PANDOC_CMD=!PANDOC_CMD! --lua-filter="%LUA_FILTER%"
) else (
    echo Warning: Lua filter not found: %LUA_FILTER%
)

REM Add media extraction
set PANDOC_CMD=!PANDOC_CMD! --extract-media="%OUTPUT_DIR%media"

echo Converting: %INPUT_FILE% -^> %OUTPUT_FILE%
echo Command: %PANDOC_CMD%

REM Execute the command
%PANDOC_CMD%
set RESULT=%ERRORLEVEL%

if %RESULT% EQU 0 (
    echo Conversion successful

    REM Extract RTM data if requested
    if "%EXTRACT_RTM%" == "true" (
        if not defined RTM_OUTPUT (
            for %%F in ("%OUTPUT_FILE%") do set RTM_OUTPUT=%%~dpF%%~nF.rtm.json
        )

        echo Extracting RTM data to: %RTM_OUTPUT%

        REM Use Pandoc with RTM extraction filter
        set RTM_FILTER=config\extract_rtm.lua

        if exist "%RTM_FILTER%" (
            pandoc "%OUTPUT_FILE%" -o NUL --lua-filter="%RTM_FILTER%"

            REM Check if extraction produced RTM data
            set RTM_TMP=output\extracted_rtm.json
            if exist "%RTM_TMP%" (
                if not exist "%%~dpF" mkdir "%%~dpF"
                move "%RTM_TMP%" "%RTM_OUTPUT%" > NUL
                echo RTM data extracted successfully
            ) else (
                echo No RTM data was extracted
            )
        ) else (
            echo RTM extraction filter not found: %RTM_FILTER%
        )
    )

    exit /b 0
) else (
    echo Conversion failed with error code: %RESULT%
    exit /b %RESULT%
)