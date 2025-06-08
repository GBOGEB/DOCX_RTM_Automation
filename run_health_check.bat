@echo off
title RTM Health Check
color 0A

echo.
echo ================================================================
echo                    RTM QUICK HEALTH CHECK
echo ================================================================
echo.
echo This will quickly diagnose your RTM system status
echo.

python quick_health_check.py

echo.
echo Health check complete. Check the logs folder for detailed report.
echo.
pause
