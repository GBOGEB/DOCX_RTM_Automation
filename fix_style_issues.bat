@echo off
echo 🔧 Fixing Style Issues in RTM Automation Files
echo =============================================

echo.
echo 1. Installing/updating black formatter...
python -m pip install black

echo.
echo 2. Applying black formatting to problem files...
python -m black --line-length=88 verify_system_status.py
python -m black --line-length=88 test_integration.py

echo.
echo 3. Running flake8 to check remaining issues...
echo Checking verify_system_status.py:
flake8 --max-line-length=88 --extend-ignore=E203,W503,E501 verify_system_status.py

echo.
echo Checking test_integration.py:
flake8 --max-line-length=88 --extend-ignore=E203,W503,E501 test_integration.py

echo.
echo 4. Running quick quality check to verify fixes...
python quick_quality_check.py

echo.
echo Style fixes completed!
pause
