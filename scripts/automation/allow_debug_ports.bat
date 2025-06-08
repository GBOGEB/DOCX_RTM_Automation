@echo off
REM This script needs to be run as Administrator
echo Creating Windows Firewall rules for debugging ports

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script must be run as Administrator.
    echo Please right-click and select "Run as Administrator".
    pause
    exit /b 1
)

REM Add rules for debugging ports
echo Adding rule for port 5678 (Python debugpy)...
netsh advfirewall firewall add rule name="Python Debugger (5678)" dir=in action=allow protocol=TCP localport=5678

echo Adding rule for port 8000 (Web Debug Server)...
netsh advfirewall firewall add rule name="Web Debug Server (8000)" dir=in action=allow protocol=TCP localport=8000

echo Adding rule for port 9229 (Node.js Debugger)...
netsh advfirewall firewall add rule name="Node.js Debugger (9229)" dir=in action=allow protocol=TCP localport=9229

echo.
echo Firewall rules have been added.
echo.
pause
