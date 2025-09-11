```bash
# Python 3.7+
python --version

# Git (for version control)
git --version
```

### Quick Setup

```bash
# 1. Navigate to project directory
cd /c/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0

# 2. Set up virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install python-docx
# 4. Run project setup
python setup_project.py

# 5. Scan project structure
python project_scanner.py
```

## 🎯 Usage

### Basic Usage

```bash
# Run the complete RTM pipeline
python main.py

# Check generated output files
python find_output_files.py

# Scan project for analysis
python project_scanner.py
```

### Advanced Usage

```bash
# Fix pipeline issues
python fix_main_pipeline.py

# Quick Git setup
python quick_setup.py

# Test document converter directly
python document_converter.py
```

## 📊 Features

### ✅ Document Processing

- **DOCX File Reading**: Extract content from Word documents
- **Table Analysis**: Parse and structure table data
- **Text Extraction**: Clean text content extraction
- **Metadata Analysis**: Document structure information

### ✅ RTM Specific Features

- **Requirements Parsing**: Identify requirement statements
- **Traceability Matrix**: Build relationship mappings
- **Data Validation**: Verify RTM completeness
- **Report Generation**: Automated RTM reports

### ✅ Automation & Tools

- **Pipeline Processing**: Automated workflow execution
- **File Management**: Organized output structure
- **Error Handling**: Robust error recovery
- **Progress Tracking**: Detailed logging

### ✅ Development Tools

- **Git Integration**: Version control setup
- **Project Analysis**: Structure scanning
- **Troubleshooting**: Automated problem detection
- **Documentation**: Comprehensive guides

## 🔧 Configuration

### Input Configuration

```python
# Place DOCX files in the input/ directory
input/
├── MASTER_1805_1144.docx
├── requirements_matrix.docx
└── other_rtm_files.docx
```

### Output Configuration

```python
# Generated files appear in output/ directory
output/
├── MASTER_1805_1144_extracted_text.txt
├── MASTER_1805_1144_tables_data.json
├── MASTER_1805_1144_conversion_summary.json
└── project_scan_results.json
```

## 🐛 Troubleshooting

### Common Issues

#### 1. `run_document_conversion` not found

```bash
# Fix: Run the pipeline fixer
python fix_main_pipeline.py

# Or manually add import to main.py:
from document_converter import run_document_conversion
```

#### 2. No DOCX files found

```bash
# Solution: Add DOCX files to input directory
mkdir input
# Copy your .docx files to input/
```

#### 3. python-docx not installed

```bash
# Install the required package
pip install python-docx
```

#### 4. Git configuration issues

```bash
# Run quick setup
python quick_setup.py

# Or configure manually:
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

#### 5. VS Code Terminal (Git Bash) Exit Code 256

If VS Code's integrated terminal fails to start Git Bash with exit code 256:

```bash
# Automatic fix (recommended):
python scripts/fix_vscode_terminal.py

# This configures proper Git Bash terminal profiles
# and sets fallback options for different Git installations
```

**What it fixes:**
- Configures multiple Git Bash terminal profiles
- Sets proper paths for different Git installation locations
- Creates fallback options for edge cases
- Sets Git Bash as the default terminal on Windows

See [VS Code Terminal Fix Documentation](docs/VSCODE_TERMINAL_FIX.md) for detailed troubleshooting.

## 🔄 Git Workflow

### Initial Setup

```bash
# Initialize repository
git init

# Add files
git add *.py *.md

# Create first commit
git commit -m "Initial commit: RTM Automation project setup"

# Connect to GitHub
git remote add origin https://github.com/yourusername/DOCX_RTM_Automation.git
git push -u origin main
```

### Daily Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "feat: add new RTM processing feature"

# Push to GitHub
git push
```

See `git_workflow_guide.md` for detailed Git instructions.

## 📚 Documentation

- **`git_workflow_guide.md`**: Complete Git and GitHub workflow
- **`README.md`**: This comprehensive project guide
- **Code Comments**: Inline documentation in all Python files
- **Function Docstrings**: Detailed function documentation

## 🧪 Testing

```bash
# Test document converter
python document_converter.py

# Test output file finder
python find_output_files.py

# Test project scanner
python project_scanner.py
```

## 📊 7-Day Metadata Scan

Quick start with repository activity scanning:

1. Copy files from patches into your repo.
2. Run `bash scripts/bootstrap.sh` (or `.\scripts\bootstrap.ps1` on Windows).
3. Run `make scaffold && make qa`.
4. Use `python tools/pairwise_rank.py --example` to compare host/terminal options.
5. Run `make scan-7d` to generate last-7-days report.
6. Run `make package` to produce `dist/orchestration_bundle.zip`.

### Keywords in this repo
- BASELINE()
- candidate_Baseline()

### 7-day metadata scan
- Configure repos: edit config/repositories.yaml (pre-seeded with your top repos).
- Optional preferences: config/scan_prefs.yaml.
- Auth: set `GITHUB_TOKEN` for better API limits.
- Output: docs/SCAN_7D.md (human), docs/scan_7d.json (machine).
- The scan also records a candidate_Baseline() note for traceability.

### Sessions ledger
- Maintain docs/SESSIONS.md with session titles and timestamps (e.g., "Deep agent orchestration").
- Reports can reference the ledger for context.

### Trusted ports/interfaces
- Ports are not exposed publicly by default. See `.devcontainer/devcontainer.json`.

### QA gates
- Pre-commit runs ruff, black, isort, pylint, markdownlint-cli2, yamllint, eslint/prettier, shellcheck, hadolint.

### Transfer to deep agent
- See `docs/AGENT_README.md` and `agent/agent_manifest.yaml`.
- Build the bundle with `make package`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🚀 Next Steps

1. **Review Project Structure**: Run `python project_scanner.py`
2. **Set Up Git**: Run `python setup_project.py`
3. **Process Documents**: Run `python main.py`
4. **Check Results**: Run `python find_output_files.py`
5. **Read Documentation**: Review `git_workflow_guide.md`

---

**Happy RTM Processing! 🎉**
