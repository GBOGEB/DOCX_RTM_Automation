# DOCX RTM Automation

A system for automating Requirements Traceability Matrix (RTM) creation and management using DOCX files and AI-powered analysis.

## Features

- **DOCX to Markdown Conversion**: Converts DOCX files into Markdown format for easier processing and version control.
- **Requirements Extraction**: Automatically identifies and extracts requirements from processed documents.
- **AI-Powered Analysis**: Leverages OpenAI to analyze, refine, and suggest improvements for extracted requirements.
- **DMAIC Integration**: Applies the Define-Measure-Analyze-Improve-Control methodology for systematic process improvement, including CI/CD pipelines.
- **Version Control with Git**: Integrates with Git repositories for managing document versions, code, and RTMs.
- **Agent-Based System**: Utilizes a modular architecture with specialized agents for different tasks.
- **CI/CD Pipeline Enhancement**: Applies DMAIC principles to improve and automate CI/CD processes.

## Getting Started

See [QUICK_START.md](QUICK_START.md) for setup and basic usage instructions.

## Architecture

The system uses a multi-agent architecture where specialized agents collaborate:

- **Orchestrator** - Coordinates all agents and workflows.
- **Copilot Agent** - Handles code generation, repository analysis, and assists with AI-driven tasks.
- **Pandoc Agent** - Manages document conversion from DOCX to Markdown.
- **Requirements Agent** - Focuses on extracting and managing requirements
