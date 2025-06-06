@echo off
REM Batch script to run various tests and checks

echo Testing DOCX RTM Automation Project
echo ====================================

echo.
echo 1. Checking if flake8 is installed...
python -c "import flake8; print('flake8 is available')" 2>nul
if %errorlevel% neq 0 (
    echo Installing flake8...
    python -m pip install flake8
)

echo.
echo 2. Running flake8 code quality check...
flake8 enhance_document_parsing.py --max-line-length=88 --extend-ignore=E203,W503

echo.
echo 3. Checking dependencies for document parsing...
python enhance_document_parsing.py --check-deps

echo.
echo 4. Listing available input files...
python enhance_document_parsing.py --list

echo.
echo 5. Testing with sample document...
python enhance_document_parsing.py --sample

echo.
echo 6. Running integration tests...
python test_integration.py

echo.
echo All tests completed!
pause
