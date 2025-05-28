@echo off
REM filepath: /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/debug_tools_menu.bat
REM Main menu for all debugging tools

echo ==================================================
echo              Debugging Tools Menu
echo ==================================================
echo.

echo Available debugging tools:
echo.
echo 1. Port Status Helper - Check/manage ports
echo 2. Force Release Debug Port - Free up port 5678
echo 3. Debug Simple Dynamic - Run debug script with dynamic port
echo 4. Run Debug Tests - Comprehensive debug tests
echo 5. Allow Debug Ports - Open firewall rules (run as Administrator)
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    call port_status_helper.bat
) else if "%choice%"=="2" (
    call force_release_debug_port.bat
) else if "%choice%"=="3" (
    python debug_simple_dynamic.py
) else if "%choice%"=="4" (
    call run_debug_tests.bat
) else if "%choice%"=="5" (
    call allow_debug_ports.bat
) else (
    echo Invalid choice!
)

pause