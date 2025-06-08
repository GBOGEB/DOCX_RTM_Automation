@echo off
color 0A
echo.
echo ███████████████████████████████████████████████████████████
echo                RTM PIPELINE - DEBUG MODE
echo ███████████████████████████████████████████████████████████
echo.
echo This enhanced debug script will:
echo    ✓ Run comprehensive system health checks
echo    ✓ Diagnose outstanding issues
echo    ✓ Generate detailed logs and traces
echo    ✓ Include Ariana extension support
echo    ✓ Provide interactive debugging console
echo    ✓ Export diagnostics to JSON format
echo.
echo Choose your option:
echo    1. Quick Health Check + Run Pipeline
echo    2. Interactive Debug Console
echo    3. Export Full Diagnostics
echo    4. Run with Maximum Tracing
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto quick_run
if "%choice%"=="2" goto debug_console
if "%choice%"=="3" goto export_diagnostics
if "%choice%"=="4" goto max_trace
goto invalid_choice

:quick_run
echo.
echo Running Quick Health Check + Pipeline...
python -c "
from debug_console import RTMDebugConsole
console = RTMDebugConsole()
console.system_health_check()
console.diagnose_outstanding_issues()
"
echo.
echo Running Pipeline...
python setup_and_run_pipeline.py
goto end

:debug_console
echo.
echo Starting Interactive Debug Console...
python debug_console.py
goto end

:export_diagnostics
echo.
echo Exporting Full Diagnostics...
python -c "
from debug_console import RTMDebugConsole
console = RTMDebugConsole()
console.export_all_diagnostics()
print('Diagnostics exported to logs directory')
"
goto end

:max_trace
echo.
echo Running with Maximum Tracing...
python -c "
import json
config = {'debug_level': 'DEBUG', 'trace_all_operations': True, 'diagnostic_depth': 'full'}
with open('debug_config.json', 'w') as f:
    json.dump(config, f, indent=2)
print('Debug configuration updated for maximum tracing')
"
python debug_console.py
goto end

:invalid_choice
echo.
echo Invalid choice. Running default pipeline with health check...
python -c "
from debug_console import RTMDebugConsole
console = RTMDebugConsole()
console.system_health_check()
"
python setup_and_run_pipeline.py

:end
echo.
echo ═══════════════════════════════════════════════════════════
echo                    EXECUTION COMPLETE
echo ═══════════════════════════════════════════════════════════
echo.
echo Check these locations for detailed information:
echo    📁 logs/                    - All log files and reports
echo    📁 logs/health_report_*.json - System health reports
echo    📁 logs/issues_report_*.json - Issue diagnostics
echo    📁 logs/ariana_report_*.json - Ariana extension reports
echo    📁 logs/comprehensive_*.json - Complete diagnostic exports
echo.
echo For troubleshooting, run: python debug_console.py
echo.
pause
