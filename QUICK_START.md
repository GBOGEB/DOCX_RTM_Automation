# DOCX RTM Automation - Quick Start Guide

This guide will help you get started with the DOCX RTM Automation tool, which helps you extract Requirements Traceability Matrix information from Word documents.

## Setup

1. **Make sure scripts are executable**:
   ```bash
   chmod +x run.sh setup_venv.sh install_dependencies.sh lint.sh
   ```

2. **Set up the virtual environment**:
   ```bash
   ./setup_venv.sh
   ```
   (Answer 'y' when prompted to activate and install dependencies)

3. **Ensure you have input files**:
   Place your Word documents (.docx files) in the `input/` directory.

## Running the RTM Pipeline

The quickest way to generate an RTM is to run the full pipeline:

```bash
./run.sh rtm-pipeline
```

This will:
1. Convert all DOCX files to Markdown
2. Extract RTM data from the Markdown files
3. Generate HTML visualizations of the RTM

## Step-by-Step Usage

### 1. Convert Word Documents to Markdown

```bash
# Convert all documents in the input directory
./run.sh word-to-md-dir

# Convert a specific document
./run.sh word-to-md input/my_requirements.docx
```

### 2. Extract RTM Data

```bash
# Extract from all Markdown files in a directory
./run.sh extract-rtm-dir output

# Extract from a specific file
./run.sh extract-rtm output/requirements.md
```

### 3. Visualize RTM Data

```bash
# Visualize a specific RTM JSON file
./run.sh visualize-rtm output/rtm/requirements_rtm.json
```

## Formatting Requirements and Test Cases

For best results, format your Word documents as follows:

- **Requirements**: Use the format `REQ-123: Description of requirement`
- **Test Cases**: Use the format `TC-456: Description of test case`
- **Links**: Format as `[REQ-123] -> [TC-456]` to indicate traceability

## Troubleshooting

If you encounter issues:

1. Make sure all shell scripts are executable
2. Check that the Python virtual environment is activated
3. Ensure the DOCX files are properly formatted
4. Run the linter to check for code issues: `./lint.sh`
5. Fix import issues with: `./fix_imports.sh`

## Example Commands for Common Tasks

- **Check help**: `./run.sh help`
- **Convert all DOCX files**: `./run.sh word-to-md-dir`
- **Run the full RTM pipeline**: `./run.sh rtm-pipeline`
