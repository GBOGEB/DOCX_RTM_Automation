# DOCX RTM Automation Tool - Usage Guide

## Overview

The DOCX RTM Automation Tool helps automate the creation and management of Requirements Traceability Matrix (RTM) documentation using DOCX files. This tool streamlines the process of linking requirements, test cases, and other project artifacts.

## Installation

### Prerequisites

- Python 3.7 or higher
- Required Python packages (install via `pip install -r requirements.txt`):
    - python-docx
    - pandas
    - openpyxl
    - click

### Setup

1. Download the latest release from the repository
2. Extract the files to your desired location
3. Navigate to the extracted directory
4. Install dependencies:
     ```
     pip install -r requirements.txt
     ```

## Getting Started

### Basic Command Structure

```
python rtm_automation.py [OPTIONS] INPUT_FILE OUTPUT_FILE
```

### Quick Start Example

```
python rtm_automation.py --format matrix input_requirements.docx output_rtm.docx
```

## Usage Examples

### Generate a Basic RTM

```
python rtm_automation.py --type basic input.docx output_rtm.docx
```

### Import Requirements from Excel

```
python rtm_automation.py --import-excel requirements.xlsx --sheet "Requirements" input.docx output_rtm.docx
```

### Export RTM to Excel

```
python rtm_automation.py --export-excel --format xlsx input.docx output_rtm.xlsx
```

## Configuration

### Config File

Create a `config.json` file to store default settings:

```json
{
    "default_format": "matrix",
    "include_headers": true,
    "auto_numbering": true,
    "templates": {
        "basic": "templates/basic_template.docx",
        "detailed": "templates/detailed_template.docx"
    }
}
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--format` | Output format (matrix, list, detailed) | matrix |
| `--template` | Path to template file | default_template.docx |
| `--config` | Path to config file | config.json |

## Advanced Features

### Custom Templates

Create your own templates in DOCX format with placeholders:

- `{{REQUIREMENT_ID}}` - Will be replaced with requirement ID
- `{{DESCRIPTION}}` - Will be replaced with requirement description
- `{{TEST_CASE}}` - Will be replaced with linked test case

### Automatic Validation

Use the validation feature to check for:
- Orphaned requirements
- Missing test cases
- Incomplete traceability

```
python rtm_automation.py --validate input.docx
```

## Troubleshooting

### Common Issues

1. **File Permission Errors**: Ensure you have write access to the output location
2. **Format Errors**: Verify your input files follow the expected format
3. **Missing Dependencies**: Run `pip install -r requirements.txt` again

### Debug Mode

Enable debug mode for detailed logs:

```
python rtm_automation.py --debug input.docx output.docx
```

## Support

For additional help or to report bugs:
- Open an issue on the project repository
- Email support at: support@example.com

## License

This tool is licensed under MIT License. See LICENSE.md for details.