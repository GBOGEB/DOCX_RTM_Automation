
# RTM Automation Testing Guide

This guide will help you test and verify the various components of the DOCX RTM Automation system.

## 1. Testing the Refactoring Functionality

### Basic Refactoring Test

```bash
# Run the simplified refactor interface
python refactor.py path/to/file.py --mode quick

# Run the more detailed refactoring tool
python refactor_project.py path/to/project_directory --type modernize --files 5 --extensions .py,.js
```

### Verifying Refactoring Results

1. Check the output directory (displayed in the console output)
2. Review the generated files:
   - `refactoring_analysis.md` - Analysis of the code structure
   - `refactoring_report.md` - Complete refactoring report
   - `refactored_*.py` - The refactored source files
   - `explanation_*.md` - Explanations of the refactoring changes

## 2. Testing the Debugging Tools

### Full Pipeline Debug

```bash
# Run the full pipeline debugger
python debug_full_pipeline.py
```

Follow the interactive menu to select what components to test:
1. Full pipeline (end-to-end)
2. Git operations only
3. Copilot agent only
4. CI/CD agent only
5. Agent communication only
6. Run all tests

### DMAIC Process Debug

```bash
# Run the DMAIC process debugger
python debug_dmaic_output.py
```

Follow the interactive menu to select what to debug:
1. Run full DMAIC process and show outputs
2. Rerun a specific phase
3. Test factorizing functionality
4. Generate DMAIC report
5. All of the above

## 3. Testing the Agent System

### Running the Agent Orchestration Example

```bash
# Run the agent orchestration example
python examples/agent_orchestration_example.py
```

This demonstrates:
- Agent registration
- Inter-agent messaging
- Workflow execution
- System reporting

### Testing the DMAIC CI/CD Agent

```bash
# Run the DMAIC CI/CD example
python examples/dmaic_cicd_example.py
```

This demonstrates:
- CI/CD pipeline analysis
- DMAIC methodology application to CI/CD
- Report generation

## 4. Processing Input Files

### Document Conversion Testing

```bash
# First, ensure your environment is set up
# Create a testing environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install pandoc if you need document conversion
# On Windows: choco install pandoc
# On macOS: brew install pandoc
# On Linux: sudo apt-get install pandoc

# Run the Copilot agent example to test conversions
python examples/copilot_agent_example.py
```

### Extract Requirements from Documents

Use the Copilot agent to extract requirements from your own document:

```python
from dmaic import DMAICHandler
from config.openai_integration import initialize_openai
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager
from agents.copilot_agent import CopilotAgent, ConversionType

# Initialize components
client = initialize_openai()
paths = PathsManager()
output = OutputHandler(paths.get_output_dir())
dmaic = DMAICHandler("Requirements Extraction", client)
copilot = CopilotAgent(dmaic, output)

# Extract requirements from a DOCX or MD file
requirements_path = copilot.extract_requirements_from_docs(
    "path/to/your/requirements_doc.docx",
    output_format="json"
)
print(f"Requirements extracted to {requirements_path}")
```

## 5. Logs and Verification

### Agent Logs

Each run creates its own log file in the output directory. You can find the logs at:

```
./outputs/TIMESTAMP/workflow_YYYYMMDD_HHMMSS.log
```

### Important Log Files to Check

1. **DMAIC Workflow Log**: Contains all DMAIC interactions and phase transitions
2. **Agent Communication Log**: Records messages between agents
3. **Error Logs**: Any errors encountered during execution

### Reviewing Reports

After running the tests, review the generated reports:
1. DMAIC reports (`dmaic_report_*.md`)
2. Refactoring reports (`refactoring_report.md`)
3. CI/CD reports (`dmaic_cicd_report_*.md`)
4. System state dumps (`agent_system_state_*.json`)

## 6. Understanding the Components

### Key Files and Their Purpose

| File | Purpose |
|------|---------|
| `dmaic/__init__.py` | Core DMAIC methodology implementation |
| `agents/copilot_agent.py` | Handles code generation, analysis, and file conversion |
| `agents/dmaic_cicd_agent.py` | Applies DMAIC to CI/CD pipelines |
| `agents/git_agent.py` | Handles Git operations and repository management |
| `agents/agent_orchestrator.py` | Coordinates all agent activities |
| `refactor_project.py` | Main refactoring interface |
| `debug_full_pipeline.py` | Full pipeline debugging tool |
| `debug_dmaic_output.py` | DMAIC process debugging tool |
| `main.py` | Primary workflow controller |

### Agent Interactions

The agent system uses a message-passing architecture:
1. The `AgentOrchestrator` manages all agents and routes messages
2. Each agent has specific capabilities and responds to specific message types
3. Agents can communicate bidirectionally through the orchestrator
4. The `BaseAgent` class provides common agent functionality
5. All agent activities are logged for debugging and auditing

## 7. Troubleshooting Common Issues

1. **OpenAI API Key Issues**:
   - Check that your API key is correctly set in one of:
     - Environment variable `OPENAI_API_KEY`
     - `config/apikeys.yaml`
     - File specified in `paths.yaml.fixed`

2. **Missing Dependencies**:
   - Ensure all required packages are installed:
   ```
   pip install -r requirements.txt
   ```

3. **Pandoc Missing**:
   - If document conversion fails, install pandoc

4. **Agent Communication Failures**:
   - Check that agents are properly registered with the orchestrator
   - Verify message formats match expected schemas

5. **Git Operation Failures**:
   - Ensure git is installed and configured
   - Check repository paths and permissions

## 8. Adding Your Own Tests

You can create your own test scripts by following this pattern:

```python
# test_my_feature.py
import os
import sys
from config.openai_integration import initialize_openai
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager
from dmaic import DMAICHandler

# Initialize components
client = initialize_openai()
paths = PathsManager()
output = OutputHandler(paths.get_output_dir())
dmaic = DMAICHandler("My Test", client)

# Run your tests
def run_my_test():
    # Your test code here
    pass

if __name__ == "__main__":
    run_my_test()
```
