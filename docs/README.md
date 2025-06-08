# DOCX RTM Automation

A tool for extracting Requirements Traceability Matrix (RTM) from DOCX documents and converting them to various formats.

## Repository Structure

```
/DOCX_RTM_Automation
+-- config/                # All configuration files
|   +-- paths.yaml         # Main configuration 
|   +-- filters/           # Pandoc Lua filters
|   +-- secrets/           # For API keys (gitignored)
+-- src/                   # All source code
|   +-- core/              # Core processing modules
|   +-- extractors/        # Document extraction modules
|   +-- utils/             # Utility functions
|   +-- modules/           # Additional modules
+-- scripts/               # Runner scripts
|   +-- run_pipeline.py    # Main pipeline runner
|   +-- commands.sh        # Shell commands
+-- input/                 # Input documents
|   +-- docx/              # Original Word documents
|   +-- external/          # External input files
+-- output/                # Generated outputs
|   +-- markdown/          # Markdown outputs
|   +-- json/              # JSON outputs
|   +-- yaml/              # YAML outputs
|   +-- rtm/               # RTM specific outputs
+-- docs/                  # Documentation
|   +-- guides/            # User guides
|   +-- setup/             # Setup instructions
+-- tests/                 # Unit tests
+-- tools/                 # Additional tools
```

## Quick Start

1. Place your input DOCX files in the `input/docx/` directory
2. Update the paths in `config/paths.yaml` if needed
3. Run the pipeline:

```bash
python scripts/run_pipeline.py
```

## GitHub Integration

The pipeline supports automatic GitHub integration for CI/CD workflows. See `docs/setup/git_setup.md` for details.

## Testing

Run the automated tests to verify functionality:

```bash
# Run all tests
python run_tests.py

# Run a specific test file
python -m unittest tests/test_pipeline.py
```

Tests cover:
- Pipeline integration
- Module functionality
- Data extraction and conversion
