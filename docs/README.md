# DOCX RTM Automation

A tool for extracting Requirements Traceability Matrix (RTM) from DOCX documents and converting them to various formats.

[![CI](https://github.com/GBOGEB/DOCX_RTM_Automation/actions/workflows/python-ci.yml/badge.svg)](https://github.com/GBOGEB/DOCX_RTM_Automation/actions/workflows/python-ci.yml)
![Coverage Threshold](https://img.shields.io/badge/coverage-threshold%2070%25-brightgreen)
![Lineage](https://img.shields.io/badge/lineage-commit--backed-blue)

## Navigation Hub

- **Primary UI entrypoint:** `server/templates/index.html`
- **Pipeline controller:** `pipeline/main.py`
- **Idempotency contract:** `src/core/idempotency_contract.py`
- **Lineage metadata:** `src/core/lineage_metadata.py`
- **Recursive alignment verifier:** `scripts/verify_recursive_alignment.py`
- **Locked alignment manifest/index:**
  - `config/recursive_alignment_manifest.json`
  - `config/recursive_alignment_index.json`

## Phase Map (DMAIC)

The active phase execution map is implemented in `pipeline/main.py`:

1. Define
2. Measure
3. Analyze
4. Improve
5. Control

## Artifact Explorer Links

- Generated dashboard JSON: `pipeline_output/dmaic_dashboard.json`
- Generated lineage snapshot: `pipeline_output/lineage_snapshot.json`
- Generated compliance CSV: `pipeline_output/compliance_metrics.csv`
- Generated RTM processing outputs: `output/`

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

# Run lineage + idempotency + alignment focused tests with coverage
python -m pytest tests/test_basic.py tests/test_all.py tests/core -v
```

Tests cover:
- Pipeline integration
- Module functionality
- Data extraction and conversion
