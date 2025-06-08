@echo off
echo 🚀 Processing Your Real RTM Documents
echo =====================================

echo.
echo 📊 Processing DOCX documents to JSON format...

echo.
echo 1️⃣ Processing MASTER document...
python enhance_document_parsing.py input/MASTER_1805_1144.docx -f json

echo.
echo 2️⃣ Processing requirements document...
python enhance_document_parsing.py input/requirements.docx -f json

echo.
echo 3️⃣ Processing sample requirements...
python enhance_document_parsing.py input/sample_requirements.docx -f json

echo.
echo 📝 Creating digital twin from Markdown...
python digital_twin_parser.py input/requirements.md -o output/requirements_twin

echo.
echo 🔄 Converting DOCX to enhanced Markdown...
python pandoc_converter.py input/requirements.docx --analyze

echo.
echo ✅ RTM Processing Complete!
echo Check the output/ directory for results
pause
