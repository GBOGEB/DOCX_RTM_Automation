@echo off
echo 🚀 RTM Automation - Quick Command Reference
echo ==========================================

echo.
echo 📋 Available Commands:
echo.
echo 1️⃣ Process all your documents:
echo    python start_building_rtm.py
echo.
echo 2️⃣ Process documents step by step:
echo    python process_all_my_docs.py
echo.
echo 3️⃣ List available documents:
echo    python enhance_document_parsing.py --list
echo.
echo 4️⃣ Process specific documents:
echo    python enhance_document_parsing.py input/MASTER_1805_1144.docx -f json
echo    python enhance_document_parsing.py input/requirements.docx -f json
echo    python enhance_document_parsing.py input/sample_requirements.docx -f yaml
echo.
echo 5️⃣ Create digital twins:
echo    python digital_twin_parser.py input/requirements.md -o output/requirements_twin
echo.
echo 6️⃣ Run system verification:
echo    python verify_rtm_ready.py
echo.
echo 7️⃣ Quick system test:
echo    python rtm_quick_start.py
echo.
echo Choose a command and run it (without extra text)
pause
