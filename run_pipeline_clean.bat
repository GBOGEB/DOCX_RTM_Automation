@echo off
echo RTM Pipeline Quick Start
echo ===========================
echo.
echo This script will:
echo    1. Create required directories
echo    2. Generate sample documents
echo    3. Run the RTM pipeline
echo    4. Show you the results
echo.
echo Starting RTM Pipeline...
echo.

python setup_and_run_pipeline.py

echo.
echo Pipeline execution complete!
echo.
echo Check these folders for results:
echo    * input/     - Your source documents
echo    * output/    - Processed RTM documents
echo    * temp_processing/ - Temporary files
echo.
pause
