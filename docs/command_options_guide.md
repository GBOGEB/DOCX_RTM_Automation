# Command Options Guide

This guide explains how to check available options for scripts in the DOCX RTM Automation project.

## Using the --help Flag

Most Python scripts support the `--help` or `-h` flag to display available options:

```bash
# For enhance_document_parsing.py
python enhance_document_parsing.py --help

# For the requirements visualizer
python src/visualizers/req_visualizer.py --help

# For digital twin parser
python digital_twin_parser.py --help
```

## Example Options for Key Scripts

### enhance_document_parsing.py

```
usage: enhance_document_parsing.py [-h] [-o OUTPUT] [-f {markdown,json,yaml}] [--list] [--sample] [--interactive] [input_file]

Enhanced document parsing tool for RTM automation

positional arguments:
  input_file            Path to input document file (DOCX, MD, JSON, or YAML)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path for the enhanced output file
  -f {markdown,json,yaml}, --format {markdown,json,yaml}
                        Output format (default: markdown)
  --list                List available input files and exit
  --sample              Use sample document if no input file is specified
  --interactive         Run in interactive mode if no input file is specified
```

### req_visualizer.py

```
usage: req_visualizer.py [-h] [-o OUTPUT] [-m METRICS] [--no-show] input_file

Visualize requirements relationships from RTM data

positional arguments:
  input_file            Input RTM data file (JSON or YAML)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to save the visualization image
  -m METRICS, --metrics METRICS
                        Path to save metrics data (JSON or YAML)
  --no-show             Don't display the visualization (just save if --output is provided)
```

## Interactive Mode

For `enhance_document_parsing.py`, you can use interactive mode to select from available files:

```bash
python enhance_document_parsing.py --interactive
```

## List Available Files

For `enhance_document_parsing.py`, you can list available input files:

```bash
python enhance_document_parsing.py --list
```

## Using Sample Files

For `enhance_document_parsing.py`, you can use sample files for testing:

```bash
python enhance_document_parsing.py --sample
```
