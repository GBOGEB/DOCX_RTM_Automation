# DOCX RTM Automation

A tool for automating Requirements Traceability Matrix (RTM) creation and management.

## Features

- Extract content from DOCX files
- Convert to Markdown format
- Parse Markdown to structured JSON/YAML
- Extract Requirements Traceability Matrix (RTM) data
- Visualize RTM data with an interactive HTML report

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for version control)
- Microsoft Word documents containing requirements and test cases

### Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/yourusername/DOCX_RTM_Automation.git
   cd DOCX_RTM_Automation
   ```

2. **Create and activate a virtual environment**:
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate (Windows)
   .\.venv\Scripts\activate

   # Activate (Unix/macOS)
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   ./install_dependencies.sh
   ```

4. **Configure OpenAI API** (if using AI-assisted features):
   - Edit `config/openai_key.txt` and add your OpenAI API key

## Usage

### Convert Markdown to JSON/YAML

```bash
./run.sh md-to-json path/to/file.md
```

### Extract RTM from Markdown

```bash
./run.sh extract-rtm path/to/file.md
```

### Extract RTM from all Markdown files in a directory

```bash
./run.sh extract-rtm-dir path/to/directory
```

### Visualize RTM data

```bash
./run.sh visualize-rtm path/to/rtm_data.json
```

### Processing Documents

To process a DOCX document and extract RTM information:

1. **Place your DOCX files** in the `input/` directory

2. **Run the RTM pipeline**:
   ```bash
   ./shell_scripts/run_rtm.sh
   ```

3. **View the results** in the `output/` directory:
   - `output/*.md` - Markdown versions of your documents
   - `output/*.json` - JSON structured data
   - `output/*.yaml` - YAML structured data
   - `output/rtm/` - Generated RTM artifacts

## Development

### Run Tests

```bash
./run_tests.sh
```

### Code Quality

```bash
./lint.sh
```

## RTM Format

Requirements and test cases should follow these formats in your Markdown files:

- Requirements: `REQ-123` or `REQ-1-2-3`
- Test Cases: `TC-123` or `TC-1-2-3`

Links between requirements and test cases can be specified using the following syntax:

```
[REQ-123] -> [TC-456]
```

## Troubleshooting

If you encounter issues:

1. **Run the fix script**:
   ```bash
   ./shell_scripts/fix_critical_issues.sh
   ```

2. **Check logs for errors**:
   ```bash
   ./shell_scripts/rtm_status.sh --full-report
   ```

3. **Common issues**:
   - **Missing OpenAI API key**: Check `config/openai_key.txt`
   - **Script errors**: Make sure all scripts are executable (`chmod +x`)
   - **Import errors**: Verify all dependencies are installed correctly

## License

Copyright (c) 2025

## Contributing

[Contribution guidelines]

---

*Powered by OpenAI's language models for enhanced requirement analysis.*
