# Within activated virtual environment
pip install -r requirements.txt

# Check installations
pip list

# Run the main pipeline
python run.py

# Run individual steps
python -m src.core.word_to_md
python -m src.extractors.extract_outline

# Run all tests
python run_tests.py

# Run specific test module
python -m unittest tests.test_pipeline

# Run with coverage report
pip install coverage
coverage run -m unittest discover
coverage report
coverage html  # Generates HTML report in htmlcov/

# List directory structure (Windows)
dir /s /b

# List directory structure (Linux/Mac)
find . -type f | sort

# Count files by extension
dir /s *.py | find /c "py"  # Windows
find . -name "*.py" | wc -l  # Linux/Mac

# View markdown output
type output\markdown\MASTER_1805_1144.md  # Windows
cat output/markdown/MASTER_1805_1144.md   # Linux/Mac

# View yaml output 
type output\yaml\MASTER_outline.yaml      # Windows
cat output/yaml/MASTER_outline.yaml       # Linux/Mac

# Create logs directory if it doesn't exist
mkdir -p logs

# Run with logging
python run.py > logs/pipeline_run.log 2>&1

# Check for errors
findstr "Error" logs\pipeline_run.log     # Windows
grep "Error" logs/pipeline_run.log        # Linux/Mac

# Check for running Python processes
tasklist | findstr python   # Windows
ps aux | grep python        # Linux/Mac

# Kill process if needed
taskkill /F /PID <process_id>  # Windows
kill -9 <process_id>           # Linux/Mac

# Validate YAML config
python -c "import yaml; yaml.safe_load(open('config/paths.yaml'))"

# Print Python path
python -c "import sys; print(sys.executable)"

# Check Pandoc version
pandoc --version

# Simply run the pipeline script
python run_pipeline.py

# Clone the repository
git clone <https://github.com/GBOGEB/DOCX_RTM_Automation.git>

# Navigate into the cloned directory
cd DOCX_RTM_Automation

# Check the status
git status

# Make changes to files...
# Then stage the changes
git add .

# Commit with a descriptive message
git commit -m "Updated RTM extraction logic"

# Push to GitHub
git push origin main

