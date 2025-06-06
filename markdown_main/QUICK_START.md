# RTM Automation Quick Start Guide

This guide helps you quickly get started with the DOCX RTM Automation system.

## Prerequisites

1. **Python 3.8+** installed
2. **OpenAI API Key** - [Get one here](https://platform.openai.com/account/api-keys)
3. **Pandoc** (optional but recommended for document conversion)
   - Windows: `choco install pandoc`
   - macOS: `brew install pandoc`
   - Linux: `sudo apt-get install pandoc`

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your OpenAI API key:
   - Option 1: Set environment variable: `OPENAI_API_KEY=your-key-here`
   - Option 2: Create `config/apikeys.yaml` with:
     ```yaml
     openai: "your-api-key-here"
     ```

## Basic Usage

### 1. Process a DOCX file

```bash
# Convert a DOCX file to Markdown
python utils/docx_converter.py input/sample_doc.docx

# Extract requirements from a document
python utils/document_parser.py input/sample_doc.docx --requirements
```

### 2. Run the Main Pipeline

```bash
python main.py
```

### 3. Use the Refactoring Tools

```bash
# Analyze a project structure
python refactor.py path/to/project --mode analyze

# Perform quick refactoring
python refactor.py path/to/file.py --mode quick

# Perform deep refactoring
python refactor.py path/to/project --mode deep
```

## Examples

Run the included examples to see the system in action:

```bash
# Run DMAIC example
python examples/dmaic_example.py

# Run CI/CD example
python examples/dmaic_cicd_example.py

# Run agent orchestration example
python examples/agent_orchestration_example.py

# Run Copilot agent example
python examples/copilot_agent_example.py
```

## Debugging

If you encounter issues, use the debugging tools:

```bash
# Debug the DMAIC process
python debug_dmaic_output.py

# Debug the full pipeline
python debug_full_pipeline.py
```

## Project Optimization

Optimize your project structure:

```bash
# Create recommended project structure
python optimize_project.py --structure

# Create sample files for testing
python optimize_project.py --samples

# Generate documentation
python optimize_project.py --docs
```

## Next Steps

Once you're familiar with basic usage, explore:

1. [Advanced DMAIC workflows](docs/dmaic_workflows.md)
2. [Agent orchestration](docs/agent_orchestration.md)
3. [CI/CD integration](docs/cicd_integration.md)
4. [Custom requirements extraction](docs/requirement_extraction.md)

## Getting Help

If you run into issues:
1. Check the logs in the `outputs` directory
2. Run the debug scripts
3. Review documentation in the `docs` directory