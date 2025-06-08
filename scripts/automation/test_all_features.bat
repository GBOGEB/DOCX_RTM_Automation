@echo off
echo Testing Enhanced Document Parsing - Complete Feature Set
echo ======================================================

echo.
echo 1. Testing sample document with different formats...
python enhance_document_parsing.py --sample -f json
python enhance_document_parsing.py --sample -f yaml

echo.
echo 2. Testing list functionality...
python enhance_document_parsing.py --list

echo.
echo 3. Running integration tests...
python test_integration.py

echo.
echo 4. Testing requirements visualizer...
python src/visualizers/req_visualizer.py output/sample_document_enhanced.json -o output/requirements_graph.png --no-show

echo.
echo 5. Running code quality checks...
flake8 enhance_document_parsing.py --max-line-length=88 --extend-ignore=E203,W503

echo.
echo 6. Testing digital twin parser...
python digital_twin_parser.py input/sample/sample_document.md -o output/digital_twin

echo.
echo All feature tests completed!
echo Check the output/ directory for generated files.
pause
