@echo off
echo 🔍 RTM System Output Locator
echo ============================

echo.
echo 📁 Checking for output files...
python find_output_files.py

echo.
echo 📂 Opening output directories...

if exist "output" (
    echo ✅ Opening output folder...
    start "" "output"
) else (
    echo ❌ Output folder not found
)

if exist "temp_processing" (
    echo ✅ Opening temp_processing folder...
    start "" "temp_processing"
) else (
    echo ❌ temp_processing folder not found
)

echo.
echo 💡 If no output found, run:
echo    python setup_and_run_pipeline.py
echo.
pause
