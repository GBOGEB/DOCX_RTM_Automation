# OpenAI Integration Guide

This guide explains how to use OpenAI integration with the DOCX RTM Automation tool to enhance requirements analysis, test case generation, and traceability analysis.

## Configuration

### Setting up your API Key

There are several ways to provide your OpenAI API key:

1. **Environment variable** (recommended):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. **Configuration file**:
   Create a file at `config/openai_key.txt` containing only your API key.

3. **Pass directly** when initializing the helper:
   ```python
   from src.utils.openai_helper import OpenAIHelper
   helper = OpenAIHelper(api_key="your-api-key-here")
   ```

### Customizing the Model

By default, the helper uses GPT-4. You can specify a different model:

```python
helper = OpenAIHelper(model="gpt-3.5-turbo")
```

## Using the OpenAI Integration

### Example 1: Analyze Requirements

```python
from src.utils.openai_helper import OpenAIHelper

# Initialize the helper
helper = OpenAIHelper()

# Analyze a requirement
requirement = "The system shall process files within 5 seconds."
analysis = helper.analyze_requirement(requirement)

print(f"Clarity score: {analysis['clarity_score']}/10")
print(f"Testability score: {analysis['testability_score']}/10")
print(f"Issues found: {', '.join(analysis['issues'])}")
```

### Example 2: Generate Test Cases

```python
from src.utils.openai_helper import OpenAIHelper

# Initialize the helper
helper = OpenAIHelper()

# Generate test cases for a requirement
requirement = "Users must be able to reset their password via email verification."
test_cases = helper.generate_test_cases(requirement, count=3)

for tc in test_cases["test_cases"]:
    print(f"Test ID: {tc['id']}")
    print(f"Description: {tc['description']}")
    print(f"Steps: {', '.join(tc['steps'])}")
    print("---")
```

### Example 3: Analyze Traceability

```python
from src.utils.openai_helper import OpenAIHelper

# Initialize the helper
helper = OpenAIHelper()

# Sample requirements and test cases
requirements = [
    {"id": "REQ-001", "description": "The system shall allow users to log in."},
    {"id": "REQ-002", "description": "The system shall allow users to reset passwords."},
    {"id": "REQ-003", "description": "The system shall log all login attempts."}
]

test_cases = [
    {"id": "TC-001", "description": "Verify successful login with valid credentials."},
    {"id": "TC-002", "description": "Verify login failure with invalid password."}
]

# Analyze traceability between requirements and test cases
traceability = helper.analyze_traceability(requirements, test_cases)

print(f"Coverage: {traceability['coverage_percentage']}%")
print(f"Uncovered requirements: {', '.join(traceability['uncovered_requirements'])}")
```

## Command Line Usage

You can also use the OpenAI helper from the command line:

```bash
# Analyze a requirement
python -m src.utils.openai_helper --analyze-requirement "The system shall process user requests within 3 seconds."

# Generate test cases
python -m src.utils.openai_helper --generate-tests "Users shall be able to export data in CSV format." --count 3
```

## Integration with RTM Workflow

The OpenAI integration can be used throughout the RTM workflow:

1. **Requirements Extraction**: Enhance and clarify extracted requirements
2. **Test Coverage Analysis**: Identify gaps in test coverage
3. **Traceability Enhancement**: Generate suggestions for missing links

## Dependencies

Make sure to install the OpenAI package:

```bash
pip install openai
```

## Error Handling

The helper implements retry logic with exponential backoff for API calls. If all retries fail, check:

- Your API key is valid
- You have sufficient quota/credits
- Your network connection is stable

## Customizing Prompts

If you need to customize the prompts used for analysis, you can extend the `OpenAIHelper` class:

```python
from src.utils.openai_helper import OpenAIHelper

class CustomOpenAIHelper(OpenAIHelper):
    def analyze_requirement(self, requirement, additional_context=""):
        # Custom implementation with your own prompt
        custom_prompt = f"""Your custom prompt here: {requirement}"""
        response = self._call_api(custom_prompt)
        # Process and return the response
        return {...}
```
