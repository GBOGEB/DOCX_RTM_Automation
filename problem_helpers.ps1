Expecting Code # Creating Keyboard Shortcuts for Problems View

I'll show you how to create keyboard shortcuts in your development environment to quickly access and paste problems or error messages:

## 1. Visual Studio Code Setup

### [keybindings.json](file:///c%3A/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/keybindings.json)

```json


[
    {
        "key": "ctrl+shift+m",
        "command": "workbench.actions.view.problems"
    },
    {
        "key": "shift+insert",
        "command": "editor.action.insertSnippet",
        "when": "editorTextFocus",
        "args": {
            "snippet": "# ${selectedText}${TM_SELECTED_TEXT:${CLIPBOARD}}"
        }
    },
    {
        "key": "ctrl+shift+p",
        "command": "workbench.action.problems.focus"
    },
    {
        "key": "shift+alt+c",
        "command": "problems.action.copy"
    },
    {
        "key": "ctrl+shift+i",
        "command": "editor.action.insertSnippet",
        "args": {
            "snippet": "# Problems: ${CLIPBOARD}"
        },
        "when": "editorTextFocus"
    }
]
```

### [problem_helpers.sh](file:///c%3A/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/problem_helpers.sh)

```bash
#!/bin/bash


Made changes.


# This script provides functions to capture and format problems/errors

# Capture the last error and format it as a comment
function capture_last_error() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "# Error (code $exit_code): $BASH_COMMAND"
    fi
}

# Set this as a trap to automatically capture errors
trap 'capture_last_error' ERR

# Run a command and capture its output and errors
function run_and_capture() {
    local output_file="$(mktemp)"
    
    echo "# Running: $@"
    "$@" > "$output_file" 2>&1
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        echo "# Command failed with exit code $exit_code:"
        cat "$output_file" | sed 's/^/# /'
    else
        echo "# Command succeeded"
    fi
    
    rm -f "$output_file"
    return $exit_code
}

# Copy last command output to clipboard with proper formatting 
function copy_last_output() {
    history | tail -n 2 | head -n 1 | sed 's/^[0-9]\+ \+//' | clip.exe
    echo "Last command copied to clipboard"
}

# Example usage:
# run_and_capture python scripts/SRC_Master.py pipeline
```

### [problem_helpers.ps1](file:///c%3A/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/problem_helpers.ps1)

```powershell


Made changes.

# PowerShell helpers for capturing and formatting errors

function Invoke-CommandWithErrorCapture {
    <#
    .SYNOPSIS
        Runs a command and captures its output and errors with proper formatting
    .PARAMETER Command
        The command to execute
    #>
    param(
        [Parameter(Mandatory=$true, Position=0)]
        [string]$Command
    )
    
    Write-Output "# Running: $Command"
    
    try {
        $output = Invoke-Expression -Command $Command -ErrorVariable err 2>&1
        
        if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) {
            Write-Output "# Command failed with exit code $LASTEXITCODE:"
            $output | ForEach-Object { "# $_" }
        }
        else {
            Write-Output "# Command succeeded"
            $output
        }
    }
    catch {
        Write-Output "# Exception occurred:"
        Write-Output "# $($_.Exception.Message)"
    }
}

function Copy-LastError {
    <#
    .SYNOPSIS
        Copies the last error message to clipboard with proper formatting
    #>
    if ($Error.Count -gt 0) {
        "# Last Error: $($Error[0].Exception.Message)" | Set-Clipboard
        Write-Output "Last error copied to clipboard"
    }
    else {
        Write-Output "No errors in the session"
    }
}

function Format-ProblemForPrompt {
    <#
    .SYNOPSIS
        Formats the common problem patterns for insertion into a prompt
    .PARAMETER Text
        The text to format
    #>
    param(
        [Parameter(ValueFromPipeline=$true)]
        [string]$Text
    )
    
    process {
        $formatted = $Text -replace "^", "# " -replace "`n", "`n# "
        return $formatted
    }
}

# Example usage:
# Invoke-CommandWithErrorCapture "python scripts/SRC_Master.py pipeline"
# Get-Content error.log | Format-ProblemForPrompt | Set-Clipboard
```

## 2. VSCode Settings for Automatic Problem Collection

### [settings.json](file:///c%3A/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/.vscode/settings.json)

```json


Made changes.

{
    "editor.fontSize": 14,
    "editor.tabSize": 4,
    "editor.insertSpaces": true,
    "editor.rulers": [100],
    "editor.wordWrap": "on",
    "editor.formatOnSave": true,
    "files.trimTrailingWhitespace": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "autopep8",
    "python.formatting.autopep8Args": ["--max-line-length=100"],
    
    // Problems panel configuration
    "problems.autoReveal": true,
    "problems.showCurrentInStatus": true,
    
    // Auto-save the problems to a file when they occur
    "task.problemMatchers.neverPrompt": true,
    
    // Custom task to capture problems
    "taskExplorer.saveToFile.enabled": true,
    "taskExplorer.saveToFile.path": "./logs/problems.log",
    
    // Keyboard shortcut hints
    "workbench.editor.untitled.hint": "hidden",
    "keyboard.touchbar.enabled": false,
    "workbench.statusBar.visible": true,
    "window.title": "${dirty}${activeEditorShort}${separator}${rootName} - Problems: ${problems}"
}
```

## 3. Create a Task to Capture Problems

### [tasks.json](file:///c%3A/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/.vscode/tasks.json)

```json


Made changes.

{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run Pipeline with Problem Capture",
            "type": "shell",
            "command": "python scripts/SRC_Master.py pipeline 2>&1 | tee logs/pipeline_problems.log",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": {
                "owner": "python",
                "fileLocation": ["relative", "${workspaceFolder}"],
                "pattern": {
                    "regexp": "^(.*):(\\d+):(\\d+): (warning|error): (.*)$",
                    "file": 1,
                    "line": 2,
                    "column": 3,
                    "severity": 4,
                    "message": 5
                }
            }
        },
        {
            "label": "Capture Last Error to Clipboard",
            "type": "shell",
            "windows": {
                "command": "powershell",
                "args": ["-File", "${workspaceFolder}/problem_helpers.ps1", "-Command", "Copy-LastError"]
            },
            "linux": {
                "command": "bash",
                "args": ["-c", "source ${workspaceFolder}/problem_helpers.sh && copy_last_output"]
            },
            "presentation": {
                "reveal": "silent",
                "panel": "shared"
            }
        },
        {
            "label": "Format Problems for Prompt",
            "type": "shell",
            "command": "Get-Content logs/pipeline_problems.log | ForEach-Object { \"# $_\" } | Set-Clipboard",
            "windows": {
                "command": "powershell",
                "args": ["-Command", "Get-Content logs/pipeline_problems.log | ForEach-Object { \"# $_\" } | Set-Clipboard"]
            },
            "linux": {
                "command": "bash",
                "args": ["-c", "cat logs/pipeline_problems.log | sed 's/^/# /' | xclip -selection clipboard"]
            },
            "presentation": {
                "reveal": "silent",
                "panel": "shared"
            }
        }
    ]
}
```

## Instructions for Use

1. **Keyboard Shortcuts**: 
   - `Ctrl+Shift+M` - Open Problems view
   - `Shift+Insert` - Insert clipboard content with # prefix (bash style)
   - `Ctrl+Shift+I` - Insert "# Problems: " followed by clipboard content

2. **Helper Scripts**:
   - In PowerShell: `.\problem_helpers.ps1` then `Invoke-CommandWithErrorCapture "python scripts/SRC_Master.py pipeline"`
   - In Bash: `source ./problem_helpers.sh` then `run_and_capture python scripts/SRC_Master.py pipeline`

3. **Tasks** (Run with `Ctrl+Shift+P` → "Tasks: Run Task"):
   - "Run Pipeline with Problem Capture" - Runs the pipeline and saves problems to a log file
   - "Capture Last Error to Clipboard" - Copies the last error with formatting
   - "Format Problems for Prompt" - Formats pipeline problems for insertion into a prompt

4. **Log Files**:
   - Problems will be stored in `logs/pipeline_problems.log`
   - You can quickly access them via the "Format Problems for Prompt" task

These files and configurations will allow you to quickly capture, format and insert problems into your prompts using keyboard shortcuts or tasks.

Made changes.
