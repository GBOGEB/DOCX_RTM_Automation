@echo off
REM This batch file helps with project navigation and setup on Windows
REM Implements IR-1: User Interface for easy project navigation

echo ===============================================
echo DOCX RTM Automation Navigation Helper for Windows
echo ===============================================
echo.

REM Define project path
set PROJECT_PATH=C:\Users\gbonthuy\Downloads\DOCX_RTM_Automation_v1.0

REM Check if project directory exists
if not exist "%PROJECT_PATH%" (
    echo ERROR: Project directory not found at %PROJECT_PATH%
    echo Please update the PROJECT_PATH variable in this script.
    goto :end
)

echo Project located at: %PROJECT_PATH%
echo.

REM Display menu options (Implements IR-1: User Interface)
echo Available options:
echo 1. Open project folder
echo 2. Create virtual environment
echo 3. Install dependencies
echo 4. Run requirements analysis
echo 5. Run debug helpers
echo 6. Exit
echo.

:menu
set /p choice=Enter your choice (1-6):
echo.

if "%choice%"=="1" (
    REM Open project folder
    explorer "%PROJECT_PATH%"
    echo Opened project folder.
) else if "%choice%"=="2" (
    REM Create virtual environment (Implements NFR-2: Scalability)
    cd /d "%PROJECT_PATH%"
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created at %PROJECT_PATH%\.venv
) else if "%choice%"=="3" (
    REM Install dependencies
    cd /d "%PROJECT_PATH%"
    echo Installing dependencies...
    if exist .venv\Scripts\activate.bat (
        call .venv\Scripts\activate.bat
        pip install -r requirements.txt
        echo Dependencies installed.
    ) else (
        echo Virtual environment not found. Please create it first (option 2).
    )
) else if "%choice%"=="4" (
    REM Run requirements analysis (Implements FR-2: Data Management)
    cd /d "%PROJECT_PATH%"
    if exist .venv\Scripts\activate.bat (
        call .venv\Scripts\activate.bat
        python "Project Requirements.py"
        echo Requirements analysis complete.
    ) else (
        echo Virtual environment not found. Please create it first (option 2).
    )
) else if "%choice%"=="5" (
    REM Run debug helpers (Implements IR-3: External System Interfaces)
    cd /d "%PROJECT_PATH%"
    if exist .venv\Scripts\activate.bat (
        call .venv\Scripts\activate.bat
        python debug_helpers.py
        echo Debug helpers executed.
    ) else (
        echo Virtual environment not found. Please create it first (option 2).
    )
) else if "%choice%"=="6" (
    goto :end
) else (
    echo Invalid choice. Please try again.
    goto :menu
)

echo.
goto :menu

:end
echo Thank you for using DOCX RTM Automation.
pause
