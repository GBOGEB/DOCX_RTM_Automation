# Quick Start Guide

This guide will help you get started with the DOCX RTM Automation tool in minutes.

## 1. Prepare Your Document

First, prepare your Word document with requirements and test cases. For best results:

- Use consistent ID formats: `REQ-XXX` for requirements and `TC-XXX` for test cases
- Make traceability links explicit: `[REQ-001] -> [TC-001]`
- Use heading styles for proper document structure

Example:
```
# System Requirements Document

## Requirements

### REQ-001 - User Authentication
The system shall provide secure user authentication.

### REQ-002 - Data Encryption
The system shall encrypt all sensitive data.

## Test Cases

### TC-001 - Verify Login
This test verifies the user authentication process.

### TC-002 - Verify Data Security
This test verifies that data is properly encrypted.

## Traceability Matrix

[REQ-001] -> [TC-001]
[REQ-002] -> [TC-002]
```

## 2. Place Your Document

Save your document in the `input/` directory:

```bash
cp your_document.docx /c:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/input/
```

## 3. Run the Pipeline

Execute the RTM pipeline:

```bash
./shell_scripts/run_rtm.sh
```

## 4. Review the Output

Check the generated artifacts:

```bash
# List all output files
ls -la output/

# View the RTM data
cat output/rtm/rtm_matrix.yaml  # or .json if available
```

## 5. Common Commands

Here are some common operations:

```bash
# Check system status
./shell_scripts/rtm_status.sh --verbose

# Generate a comprehensive status report
./shell_scripts/rtm_status.sh --full-report

# Fix common issues
./shell_scripts/fix_critical_issues.sh
```

## 6. Processing Multiple Documents

To process multiple documents:

1. Place all documents in the `input/` directory
2. Run the standard pipeline:
   ```bash
   ./shell_scripts/run_rtm.sh
   ```
3. The system will generate individual outputs for each document
4. A consolidated RTM will be created if cross-document traceability is detected

## 7. Converting Formats

You can convert between formats using the utility scripts:

```bash
# Convert MD to JSON/YAML
python src/core/md_to_json_yaml.py output/document.md

# Sync outline files across formats
python src/utils/sync_outline_files.py output/document_outline.yaml
```

## Next Steps

- Learn about [Advanced Features](advanced_features.md)
- Read the [API Documentation](api_docs.md)
- Explore [Configuration Options](configuration.md)
