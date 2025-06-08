@echo off
echo 🚀 RTM Automation System - Ready to Use!
echo ========================================

echo.
echo 1️⃣ Process your first document:
echo python enhance_document_parsing.py input/your_document.docx -f json

echo.
echo 2️⃣ Create digital twin:
echo python digital_twin_parser.py input/your_document.md -o output/digital_twin

echo.
echo 3️⃣ Run comprehensive verification:
echo python verify_rtm_ready.py

echo.
echo 4️⃣ Convert DOCX to Markdown:
echo python pandoc_converter.py input/your_document.docx --analyze

echo.
echo Your RTM system has these capabilities:
echo ✅ Document parsing (DOCX, MD → JSON, YAML)
echo ✅ Requirements extraction (REQ-, FR-, NFR- patterns)
echo ✅ Digital twin generation with relationships
echo ✅ Multi-format output generation
echo ✅ Integration with Project Requirements.py
echo ✅ Quality assurance system (light/quick/heavy checks)

echo.
echo 🎯 Core files are CLEAN and ready for production use!
pause
