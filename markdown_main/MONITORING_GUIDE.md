# Monitoring and Logging Guide

This document explains where to find logs and how to monitor the RTM Automation system's operation.

## Log File Locations

All logs are stored in the `outputs` directory. There are two types of output directories:

1. **Default output directory**: `./outputs/`
2. **Timestamped output directories**: `./outputs/YYYYMMDD_HHMMSS/`

### Key Log Files

| File Pattern | Description |
|--------------|-------------|
| `workflow_*.log` | Main log file containing all operations and interactions |
| `agent_system_state_*.json` | JSON snapshot of the agent system state |
| `*_report.md` | Generated reports (CI/CD, DMAIC, refactoring) |
| `refactored_*.py` | Output of code refactoring operations |
| `requirements_*.json` | Extracted requirements |

## Monitoring Agent Activity

### Agent System Report

To generate a snapshot of the current agent system:

```python
from dmaic import DMAICHandler
from config.openai_integration import initialize_openai
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager
from agents.agent_orchestrator import AgentOrchestrator

# Initialize components
client = initialize_openai()
paths = PathsManager()
output = OutputHandler(paths.get_output_dir())
dmaic = DMAICHandler("System Monitoring", client)

# Create and initialize orchestrator
orchestrator = AgentOrchestrator(dmaic, output)
orchestrator.initialize_standard_agents()

# Update all agents
agent_statuses = orchestrator.update_all_agents()
print("Agent statuses:")
for agent_id, status in agent_statuses.items():
    print(f"- {agent_id}: {status['status']} ({status['queue_size']} messages in queue)")

# Generate system report
system_report = orchestrator.generate_system_report()
print(f"Total agents: {len(system_report['agents'])}")
print(f"Total messages processed: {system_report['message_count']}")

# Save the system state
state_path = orchestrator.save_system_state()
print(f"System state saved to: {state_path}")
```

### Creating a Monitoring Dashboard

You can create a simple monitoring dashboard script:

```python
# monitor_agents.py
import os
import sys
import time
import json
from pathlib import Path
import threading
import datetime

# Add the project root to path if needed
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from dmaic import DMAICHandler
from config.openai_integration import initialize_openai
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager
from agents.agent_orchestrator import AgentOrchestrator

class AgentMonitor:
    def __init__(self):
        self.client = initialize_openai()
        self.paths = PathsManager()
        self.output = OutputHandler(self.paths.get_output_dir(create_timestamped=True))
        self.dmaic = DMAICHandler("Agent Monitoring", self.client)
        self.orchestrator = AgentOrchestrator(self.dmaic, self.output)
        self.orchestrator.initialize_standard_agents()
        self.running = False

    def start_monitoring(self, interval=5):
        """Start monitoring agents at specified interval (seconds)"""
        self.running = True

        def monitor_thread():
            while self.running:
                self._show_status()
                time.sleep(interval)

        # Start monitoring in a separate thread
        thread = threading.Thread(target=monitor_thread)
        thread.daemon = True
        thread.start()

        print(f"Monitoring started. Press Ctrl+C to stop.")
        try:
            while True:
                cmd = input("\nEnter command (report/state/quit): ").strip().lower()
                if cmd == "report":
                    self._generate_report()
                elif cmd == "state":
                    self._save_state()
                elif cmd == "quit":
                    self.running = False
                    break
        except KeyboardInterrupt:
            self.running = False
            print("\nMonitoring stopped.")

    def _show_status(self):
        """Show current agent status"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"=== Agent Status at {datetime.datetime.now()} ===\n")

        statuses = self.orchestrator.update_all_agents()
        for agent_id, status in statuses.items():
            queue_size = status.get("queue_size", 0)
            status_str = status.get("status", "unknown")
            role = status.get("role", "unknown")

            # Color coding based on queue size
            if queue_size > 5:
                queue_indicator = f"\033[91m{queue_size}\033[0m"  # Red
            elif queue_size > 0:
                queue_indicator = f"\033[93m{queue_size}\033[0m"  # Yellow
            else:
                queue_indicator = f"\033[92m{queue_size}\033[0m"  # Green

            print(f"Agent: {agent_id:<15} Role: {role:<12} Status: {status_str:<10} Queue: {queue_indicator}")

    def _generate_report(self):
        """Generate and display a system report"""
        report = self.orchestrator.generate_system_report()
        print("\n=== System Report ===")
        print(f"Timestamp: {datetime.datetime.fromtimestamp(report['timestamp'])}")
        print(f"Total agents: {len(report['agents'])}")
        print(f"Messages processed: {report['message_count']}")
        print(f"Pending responses: {report['pending_responses']}")

    def _save_state(self):
        """Save the current system state"""
        path = self.orchestrator.save_system_state()
        print(f"\nSystem state saved to: {path}")

if __name__ == "__main__":
    monitor = AgentMonitor()
    monitor.start_monitoring()
```

## Reading Log Files

The log files contain detailed information about the system's operation:

### Workflow Log Format

```
YYYY-MM-DD HH:MM:SS - dmaic_workflow - INFO - Message
```

Example message types:
- Agent initialization: `Agent X registered with role Y`
- Phase transitions: `Starting DEFINE phase`
- Interactions: `Q: [question] | R: [response]`
- Operations: `File saved to [path]`

### Agent Communication Logs

Messages between agents are logged with:
- Source agent
- Target agent
- Message type
- Content summary
- Timestamp

## Monitoring CI/CD Integration

The CI/CD integration can be monitored through:

1. **CI/CD logs**: Found in the workflow logs
2. **CI/CD reports**: Generated markdown reports
3. **Agent status**: The CI/CD agent status in the system report

## Troubleshooting Common Issues

### 1. OpenAI API Errors

If you see errors related to the OpenAI API:

1. Check the API key configuration
2. Look for rate limiting messages
3. Verify network connectivity

### 2. Agent Communication Failures

If agents aren't communicating properly:

1. Check that the orchestrator is initialized
2. Verify that agents are registered
3. Look for message routing errors in logs

### 3. Git Integration Issues

For Git operation failures:

1. Verify Git is installed and on the PATH
2. Check repository paths and permissions
3. Look for specific Git error messages in the logs

## Creating Custom Monitoring Tools

You can create custom monitoring tools using the agent orchestrator API. Example:

```python
def monitor_specific_agent(agent_id):
    # Initialize the agent system...

    # Get the specific agent
    agent = orchestrator.agents.get(agent_id)
    if agent:
        # Monitor this specific agent
        agent_status = agent.update()

        # Check message queue
        queue_size = agent.inbox.qsize()

        # Process messages if needed
        processed = agent.process_all_messages()

        return {
            "status": agent_status,
            "queue_size": queue_size,
            "messages_processed": processed
        }
    return None
```

This guide should help you effectively monitor and understand the RTM Automation system's operation.