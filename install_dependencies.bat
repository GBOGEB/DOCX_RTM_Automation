@echo off
echo 🔧 Installing RTM Pipeline Dependencies
echo =====================================

echo.
echo 📦 Installing Python packages...
pip install python-docx
pip install PyYAML
pip install markdown

echo.
echo 🌐 Checking for pandoc (optional but recommended)...
pandoc --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Pandoc is available
    pandoc --version
) else (
    echo ⚠️ Pandoc not found - install from https://pandoc.org/ for best results
)

echo.
echo 📁 Creating required directories...
if not exist "input" mkdir input
if not exist "output" mkdir output
if not exist "temp_processing" mkdir temp_processing

echo.
echo ✅ Dependencies installation complete!
echo.
echo 📋 Quick Start:
echo    1. Place your Word documents in the 'input' folder
echo    2. Run: python word_markdown_pipeline.py input/your_document.docx
echo    3. Find processed documents in the 'output' folder
echo.
pause
