@echo off
title RTM Syntax Fix Tool
color 0E

echo.
echo ================================================================
echo                    RTM SYNTAX FIX TOOL
echo ================================================================
echo.
echo This tool will automatically fix common syntax issues in:
echo    ✓ Python files (.py)
echo    ✓ Shell scripts (.sh)
echo.
echo IMPORTANT: Backups will be created before making changes
echo.

pause

echo Running syntax fix tool...
echo.

python complete_syntax_fix.py

echo.
echo ================================================================
echo                    SYNTAX FIX COMPLETE
echo ================================================================
echo.
echo If files were modified, backups were created with .backup extension
echo.
echo Next steps:
echo    1. Test your scripts to ensure they work correctly
echo    2. Run 'python syntax_checker.py' to verify all issues are fixed
echo    3. If satisfied, you can delete the .backup files
echo.
pause
