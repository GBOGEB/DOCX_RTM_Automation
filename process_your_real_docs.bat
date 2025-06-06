@echo off
echo 🚀 Processing Your Actual RTM Documents
echo ========================================

echo 📋 First, let's see what documents are available:
python enhance_document_parsing.py --list

echo.
echo 📊 Processing your MASTER document:
python enhance_document_parsing.py input/MASTER_1805_1144.docx -f json

echo.
echo 📋 Processing requirements document:
python enhance_document_parsing.py input/requirements.docx -f json

echo.
echo 📄 Processing sample requirements:
python enhance_document_parsing.py input/sample_requirements.docx -f json

echo.
echo 🔗 Creating digital twin from requirements.md:
python digital_twin_parser.py input/requirements.md -o output/requirements_twin

echo.
echo 🎯 Running comprehensive RTM verification:
python verify_rtm_ready.py

echo.
echo ✅ All your real documents have been processed!
echo Check the output/ directory for JSON, YAML, and digital twin files
pause
