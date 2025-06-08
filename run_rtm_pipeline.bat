@echo off
echo 🚀 RTM Pipeline Execution Script
echo ================================

echo.
echo Choose execution mode:
echo 1. Complete Pipeline (all steps)
echo 2. Required Steps Only (faster)
echo 3. Custom JSON Analysis Only
echo 4. System Verification Only
echo 5. Exit

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🎯 Running COMPLETE RTM Pipeline...
    echo This will execute all steps including celebrations
    python rtm_pipeline_executor.py
) else if "%choice%"=="2" (
    echo.
    echo ⚡ Running REQUIRED steps only...
    echo This will execute core functionality only
    python rtm_pipeline_executor.py --required-only
) else if "%choice%"=="3" (
    echo.
    echo 📊 Running JSON Analysis...
    python -c "import sys; sys.path.insert(0, 'src'); from analyzers.json_file_analyzer_safe import main; main()"
) else if "%choice%"=="4" (
    echo.
    echo 🔍 Running System Verification...
    python main_organized.py status
    python verify_rtm_still_perfect.py
) else if "%choice%"=="5" (
    echo Goodbye!
    exit /b 0
) else (
    echo Invalid choice. Please run the script again.
    exit /b 1
)

echo.
echo 🎊 Pipeline execution completed!
echo Check rtm_pipeline_results.json for detailed results
pause
