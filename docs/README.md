# RTM Automation Pipeline

This document provides an overview of the RTM (Requirements Traceability Matrix) Automation pipeline, its core components, and how to use them.

## Core Components

- **`scripts/extract_structure.py`**: Extracts headings and `QQQ` tags (or other specified patterns) from a DOCX file and outputs them as JSON. This script is crucial for initial document parsing and structuring.
- **`pipeline/commands.sh`**: A shell script that orchestrates various pipeline steps, including setting up the virtual environment, extracting document structure, converting DOCX to Markdown, and potentially triggering AI-driven analysis.
- **Agents System (`agents/`)**: Includes specialized agents (e.g., Git, Copilot, CI/CD) managed by an `AgentOrchestrator` for complex workflows like repository analysis and code generation.

## Pipeline Execution

The main pipeline can be executed using the `commands.sh` script. This script automates the workflow from document input to RTM generation and analysis.

```bash
bash pipeline/commands.sh
```
This script typically performs:
1. Virtual environment setup.
2. Document structure extraction from DOCX files using `scripts/extract_structure.py`.
3. Conversion of DOCX to Markdown (e.g., using Pandoc), preserving structure and images.
4. Extraction of requirements from Markdown or structured data.
5. AI-driven analysis and processing tasks (e.g., using OpenAI).
6. Interaction with Git repositories for version control and analysis.
7. Other automated tasks as defined in the script.

## Supported Inputs and Integrations

The RTM Automation pipeline is designed to work with various inputs and integrations:

- **Document Formats**: Primarily processes `.docx` files, converting them to Markdown for further analysis. It can also ingest requirements directly from Markdown (`.md`) files.
- **Version Control**: Integrates with Git repositories for tracking changes, analyzing repository structure (including submodules), and managing versions of documentation and requirements.
- **AI Services**: Leverages AI models, particularly through the OpenAI API, for tasks like natural language processing, requirement refinement, and code/documentation generation.

## Examples and Snippets

This section provides references to example code and utility snippets.

- **OpenAI API Example**:
  A simple script demonstrating how to use the OpenAI API for chat completions can be found in `docs/examples/openai_example.py`.
  ```python
  # docs/examples/openai_example.py
  import openai
  import os

  # Ensure your OPENAI_API_KEY is set as an environment variable
  # For example: export OPENAI_API_KEY='your_api_key_here'

  # It's good practice to load the API key from an environment variable
  # openai.api_key = os.getenv("OPENAI_API_KEY")

  # if not openai.api_key:
  #     print("Error: OPENAI_API_KEY environment variable not set.")
  # else:
  #     try:
  #         response = openai.ChatCompletion.create(
  #             model="gpt-4",  # Or your preferred model
  #             messages=[
  #                 {"role": "user", "content": "Write a one-sentence bedtime story about a brave little robot."}
  #             ]
  #         )
  #         print(response['choices'][0]['message']['content'])
  #     except Exception as e:
  #         print(f"An API error occurred: {e}")
  print("See docs/examples/openai_example.py for the full script and setup instructions.")
  ```

- **Function Reference Example**:
  The file `docs/function_reference.json` provides an illustrative example of how function metadata could be structured in JSON. It is not directly consumed by the core pipeline but serves as a structural example.

## Usage

To run the main pipeline:
```bash
bash pipeline/commands.sh
```

Refer to specific guides and documentation within this `docs` directory for more detailed information on individual components and processes, including `PRODUCT_REQUIREMENTS.md` and `FUNCTIONAL_SPECIFICATION.md`.
