# RTM Automation Run Guide

This guide provides step-by-step instructions for running the various components of the DOCX RTM Automation system.

## Prerequisites

1. Ensure Python 3.8+ is installed
2. Set up your OpenAI API key using one of these methods:
   - Environment variable: `export OPENAI_API_KEY=your-api-key`
   - Create `config/apikeys.yaml` with:
     ```yaml
     openai: "your-api-key"
     ```

## Quick Start Commands

Here are the primary commands for running different components:

```bash
# Run the main workflow
python main.py

# Run refactoring (simplified interface)
python refactor.py path/to/file_or_directory --mode quick|deep|analyze

# Run detailed refactoring
python refactor_project.py path/to/directory --type general --files 10

# Debug the full pipeline
python debug_full_pipeline.py

# Debug DMAIC output
python debug_dmaic_output.py

# Run examples
python examples/dmaic_example.py
python examples/dmaic_cicd_example.py
python examples/agent_orchestration_example.py
python examples/copilot_agent_example.py
```

## Detailed Usage Instructions

### Main Workflow

The main workflow integrates DMAIC methodology with the RTM automation process:

```bash
python main.py
```

This will:
1. Initialize the OpenAI client
2. Set up the DMAIC handler
3. Execute the Define phase with sample questions
4. Run the Measure phase
5. Save results

### Refactoring Code

The refactoring tool has two interfaces:

1. **Simple interface** (recommended for most users):
   ```bash
   python refactor.py path/to/code --mode quick
   ```

   Available modes:
   - `quick`: Basic improvements (faster)
   - `deep`: Comprehensive refactoring (slower)
   - `analyze`: Only analyze without changes

2. **Advanced interface** (for fine-grained control):
   ```bash
   python refactor_project.py path/to/project --type general --files 10 --extensions .py,.js
   ```

   Parameters:
   - `--type`: Refactoring type (general, performance, readability, modernize, patterns)
   - `--files`: Maximum number of files to process
   - `--extensions`: File extensions to include

### Debugging and Testing

For debugging the system, use:

```bash
python debug_full_pipeline.py
```

This provides an interactive menu to test specific components or the entire pipeline.

For debugging DMAIC output specifically:

```bash
python debug_dmaic_output.py
```

### Working with Documents

To test document processing:

```python
# Create a simple test script
from dmaic import DMAICHandler
from config.openai_integration import initialize_openai
from agents.copilot_agent import CopilotAgent, ConversionType
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager

# Initialize components
client = initialize_openai()
paths = PathsManager()
output = OutputHandler(paths.get_output_dir())
dmaic = DMAICHandler("Document Processing", client)
copilot = CopilotAgent(dmaic, output)

# Convert a DOCX to Markdown
input_file = "path/to/document.docx"
output_file = "path/to/output.md"
result = copilot.convert_file(input_file, output_file, ConversionType.DOCX_TO_MD)
print(f"Conversion successful: {result}")

# Extract requirements
requirements_path = copilot.extract_requirements_from_docs(input_file)
print(f"Requirements extracted to: {requirements_path}")
```

### Agent Orchestration

To see how the agent system works together:

```bash
python examples/agent_orchestration_example.py
```

This demonstrates:
1. Agent registration and initialization
2. Message passing between agents
3. Running coordinated workflows
4. System state monitoring

## CI/CD Integration

To test the CI/CD integration with DMAIC:

```bash
python examples/dmaic_cicd_example.py
```

This will:
1. Generate mock CI/CD pipeline data
2. Analyze the pipeline using DMAIC
3. Generate improvement recommendations
4. Create a control plan
5. Output a comprehensive report

## Understanding Output Directories

All outputs are saved in the `outputs` directory:

- Regular runs: `./outputs/`
- Timestamped runs: `./outputs/YYYYMMDD_HHMMSS/`

Important files to check:
- `workflow_*.log`: Log of all operations
- `*_report.md`: Generated reports
- `requirements_*.json`: Extracted requirements
- `refactored_*.py`: Refactored code files

## Agent Communication Logs

To check agent communication:

1. Run with the agent orchestrator:
   ```bash
   python examples/agent_orchestration_example.py
   ```

2. Check the log file in the output directory
3. Look for entries with patterns like:
   - "Message sent from agent X to agent Y"
   - "Agent X processing message of type Z"
   - "Broadcasting message to all agents"

## Best Practices

1. **Before processing large projects:**
   - Start with small test files/projects
   - Check output quality
   - Adjust configurations as needed

2. **For document conversion:**
   - Ensure pandoc is installed for best results
   - Verify document formatting is consistent
   - Check output for conversion issues

3. **For refactoring:**
   - Make backup copies of important code
   - Review refactoring reports carefully
   - Test refactored code before deploying

4. **For debugging:**
   - Check log files for detailed error messages
   - Use the debug tools to isolate issues
   - Set logging level to DEBUG for more details