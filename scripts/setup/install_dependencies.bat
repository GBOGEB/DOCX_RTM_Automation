@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/install_dependencies.bat
REM Install missing dependencies detected by debug_helpers.py

echo ====== Installing Missing Dependencies ======
echo.

REM Check for Python and virtual environment
if not exist .venv\Scripts\pip.exe (
    echo Virtual environment not found or not activated.
    echo Please run setup_venv.bat first.
    exit /b 1
)

echo Using Python from virtual environment...
.venv\Scripts\python.exe -V

echo.
echo Installing missing packages...
echo.

REM Install packages identified as missing by debug_helpers.py
echo Installing pyyaml...
.venv\Scripts\pip.exe install pyyaml

echo Installing docx2python...
.venv\Scripts\pip.exe install docx2python

echo Installing rich...
.venv\Scripts\pip.exe install rich

echo Installing isort...
.venv\Scripts\pip.exe install isort

echo Installing mypy...
.venv\Scripts\pip.exe install mypy

echo Installing pylint...
.venv\Scripts\pip.exe install pylint

echo.
echo All dependencies installed. Running debug_helpers.py to verify:
echo.
.venv\Scripts\python.exe debug_helpers.py

echo.
echo ====== Installation Complete ======
echo.

pause