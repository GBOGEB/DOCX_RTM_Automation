# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import subprocess
import logging

# --- Start of sys.path modification ---
# Calculate the project root directory (directory containing this script and the 'agents' package).
_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Ensure the project root is at the beginning of sys.path.
# Remove all occurrences of _PROJECT_ROOT and _PROJECT_ROOT + os.sep first, then insert.
paths_to_remove = [_PROJECT_ROOT, _PROJECT_ROOT + os.sep]
current_sys_path = [p for p in sys.path if p not in paths_to_remove]
sys.path = [_PROJECT_ROOT] + current_sys_path
# --- End of sys.path modification ---

from agents.agent_orchestrator import AgentOrchestrator
from agents.agent_common import BaseAgent  # For type hinting if needed
from dmaic import DMAICHandler
from utils.paths_manager import PathsManager
from utils.output_handler import OutputHandler, LogLevel
from config.openai_integration import initialize_openai, check_openai_availability


def main():
    print("--- Starting Diagnostic Tests ---")

    # 0. Diagnostic Plan & CI/CD Considerations
    print("\n--- 0. Diagnostic Plan & CI/CD Considerations ---")
    print("""
    Diagnostic Run Plan:
    1. Initialize Core Components: Setup paths, output handling, OpenAI client, DMAIC handler, and Agent Orchestrator.
    2. Check OpenAI API Key & Availability: Verify connection and authentication with OpenAI services.
    3. Ping Agents: Test basic responsiveness of all critical agents.
    4. Run Sample Workflow (Repository Analysis): Execute a representative end-to-end workflow to test integration.
    5. Post-Run Log Analysis: Automatically scan logs for errors and critical issues.

    Debugging Strategy:
    - Review console output and the detailed log file ('diagnostic_run.log') for errors and warnings.
    - Isolate failing components by commenting out sections of this script and re-running.
    - For agent-specific issues, check individual agent logs (if configured).
    - For OpenAI issues, verify API key, organization ID, and network connectivity.
    - Use a debugger (e.g., pdb or IDE debugger) to step through problematic code sections.

    CI/CD Integration Points:
    - This script can be a CI/CD pipeline step.
    - The pipeline should fail if critical errors are detected during the run (e.g., OpenAI unavailability, agent ping failures, workflow execution failure).
    - The post-run log analysis can be used to determine build status (e.g., fail build if ERROR count > 0).
    - Test results and logs should be archived as build artifacts.
    """)

    # 1. Initialize Core Components
    print("\n--- 1. Initializing Core Components ---")
    paths = (
        PathsManager()
    )  # Instantiating PathsManager, though get_log_dir is not used from it here.

    # Define log directory relative to the script's project root
    # _PROJECT_ROOT is defined at the top of the script.
    print(f"DEBUG: _PROJECT_ROOT is {_PROJECT_ROOT}")
    log_dir = os.path.join(_PROJECT_ROOT, "logs")
    output_dir = os.path.join(_PROJECT_ROOT, "output")  # Define output directory
    print(f"DEBUG: Attempting to use log_dir: {log_dir}")
    print(f"DEBUG: Attempting to use output_dir: {output_dir}")

    try:
        print(f"DEBUG: Attempting os.makedirs for log_dir: {log_dir}")
        os.makedirs(log_dir, exist_ok=True)  # Ensure log directory exists
        print(f"DEBUG: os.makedirs for log_dir completed.")
        print(f"DEBUG: Attempting os.makedirs for output_dir: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
        print(f"DEBUG: os.makedirs for output_dir completed.")
    except OSError as e:
        print(
            f"CRITICAL_ERROR: Error creating log or output directory: {e}",
            file=sys.stderr,
        )
        # If directory creation fails, file logging will likely fail.
        # Consider exiting or disabling file logging. For now, just print and continue.
        pass

    print("DEBUG: About to initialize OutputHandler.")
    try:
        output_handler = OutputHandler(
            output_dir=output_dir,            log_level=LogLevel.INFO,
            log_to_console=True,
            log_to_file=True,
            log_file_path=os.path.join(
                log_dir, "diagnostic_run.log"
            ),        )
        output_handler.log_debug("OutputHandler object created successfully.")
        output_handler.log_debug(
            f"OutputHandler log_file_path configured to: {output_handler.log_file_path if hasattr(output_handler, 'log_file_path') else 'N/A'}"
        )

        output_handler.log_info("OutputHandler initialized.")
        output_handler.log_debug(
            "First log message with OutputHandler (INFO level) attempted."
        )

    except Exception as e:
        print(
            f"CRITICAL_ERROR: Failed to initialize or use OutputHandler: {e}",
            file=sys.stderr,
        )
        # If OutputHandler fails, we can't use it. Fallback to print or exit.
        print(
            "--- DIAGNOSTIC SCRIPT HALTED DUE TO OutputHandler FAILURE ---",
            file=sys.stderr,
        )
        return  # Exit main if OutputHandler is critical and fails

    # Initialize OpenAI client for DMAICHandler and API key check
    openai_client = initialize_openai()
    if not openai_client:
        output_handler.log_error(
            "Failed to initialize OpenAI client. DMAIC and some agent functions might not work."
        )
        # Decide if to exit or continue with limited functionality
        # For diagnostics, we might want to continue to test other parts.
    else:
        output_handler.log_info(
            "OpenAI client initialized (or API key set for older SDK)."
        )

    dmaic_handler = None
    try:
        output_handler.log_debug("About to initialize DMAICHandler.")
        # Pass project_name derived from _PROJECT_ROOT
        project_name = os.path.basename(_PROJECT_ROOT)
        dmaic_handler = DMAICHandler(
            project_name
        )  # Pass project_name as a positional argument
        output_handler.log_info("DMAICHandler initialized.")
        output_handler.log_debug("DMAICHandler initialized successfully.")
    except Exception as e:
        print(
            f"CRITICAL_ERROR: Failed to initialize DMAICHandler: {e}", file=sys.stderr
        )
        output_handler.log_critical(
            f"Failed to initialize DMAICHandler: {e}", exc_info=True
        )
        print(
            "--- DIAGNOSTIC SCRIPT HALTED DUE TO DMAICHandler FAILURE ---",
            file=sys.stderr,
        )
        logging.shutdown()  # Attempt to flush logs before exiting
        return

    orchestrator = None
    try:
        output_handler.log_debug("About to initialize AgentOrchestrator.")
        orchestrator = AgentOrchestrator(dmaic_handler, output_handler)
        output_handler.log_info("AgentOrchestrator initialized.")
        output_handler.log_debug("AgentOrchestrator initialized successfully.")
    except Exception as e:
        if "output_handler" in locals() and output_handler is not None:
            output_handler.log_critical(
                f"Failed to initialize AgentOrchestrator: {e}", exc_info=True
            )
        else:
            print(
                f"CRITICAL_ERROR: Failed to initialize AgentOrchestrator: {e}",
                file=sys.stderr,
            )
        print(
            "--- DIAGNOSTIC SCRIPT HALTED DUE TO AgentOrchestrator FAILURE ---",
            file=sys.stderr,
        )
        logging.shutdown()  # Attempt to flush logs before exiting
        return

    try:
        output_handler.log_info("Initializing standard agents in orchestrator...")
        orchestrator.initialize_standard_agents()
        output_handler.log_info("Standard agents initialized successfully.")
        output_handler.log_debug("Standard agents initialized successfully.")
    except Exception as e:
        output_handler.log_critical(
            f"Failed to initialize standard agents: {e}", exc_info=True
        )
        # Decide if to exit or continue. For diagnostics, we might continue.
        output_handler.log_warning("Continuing diagnostic run despite failure to initialize all standard agents.")

    # 2. Check OpenAI API Key & Availability
    print("\n--- 2. Checking OpenAI API Key & Availability ---")
    if openai_client:
        try:
            available, message = check_openai_availability(openai_client)
            if available:
                output_handler.log_success(f"OpenAI API Key Check: SUCCESSFUL. {message}")
            else:
                output_handler.log_error(f"OpenAI API Key Check: FAILED. {message}")
        except Exception as e:
            output_handler.log_error(f"Error checking OpenAI availability: {e}", exc_info=True)
    else:
        output_handler.log_warning("OpenAI client not initialized. Skipping API key check.")

    # 3. Ping Agents to Check Responsiveness
    print("\n--- 3. Pinging Agents ---")
    agents_to_ping = {
        "Git Agent": "git_agent_01",
        "Copilot Agent": "copilot_agent",
        "CI/CD Agent": "cicd_agent",
        "Requirement Analysis Agent": "req_analyzer_01",
        "Traceability Analysis Agent": "trace_analyzer_01",
    }

    for agent_name, agent_id in agents_to_ping.items():
        try:
            if agent_id in orchestrator.agents:
                output_handler.log_info(f"Pinging {agent_name} (ID: {agent_id})...")
                ping_result = orchestrator.ping_agent(agent_id, timeout_seconds=5.0)
                if ping_result.get("status") == "success":
                    rtt_data = ping_result.get("data", {}).get("round_trip_time_ms", "N/A")
                    rtt_str = f"{rtt_data:.2f}" if isinstance(rtt_data, float) else str(rtt_data)
                    output_handler.log_success(
                        f"Ping to {agent_name} ({agent_id}) successful. RTT: {rtt_str} ms. Response: {ping_result.get('data', {}).get('pong_content')}"
                    )
                elif ping_result.get("status") == "timeout":
                    output_handler.log_warning(
                        f"Ping to {agent_name} ({agent_id}): TIMEOUT. {ping_result.get('message')}"
                    )
                else:
                    output_handler.log_error(
                        f"Ping to {agent_name} ({agent_id}) FAILED. Status: {ping_result.get('status')}, Message: {ping_result.get('message')}"
                    )
            else:
                output_handler.log_warning(
                    f"Agent {agent_name} (ID: {agent_id}) not found in orchestrator. Skipping ping."
                )
        except Exception as e:
            output_handler.log_error(
                f"Error pinging agent {agent_name} ({agent_id}): {e}", exc_info=True
            )

    # 4. Run a Sample Workflow (Repository Analysis)
    print("\n--- 4. Running Sample Workflow: Repository Analysis ---")
    repo_url_to_analyze = "https://github.com/git-fixtures/basic.git"  # A very small public repo for testing

    workflow_config = {
        "repository_url": repo_url_to_analyze,
        "branch": "master",  # This specific test repo uses 'master'
    }
    output_handler.log_info(
        f"Executing 'repository_analysis' workflow for: {repo_url_to_analyze}"
    )

    if not orchestrator.git_agent:
        output_handler.log_error(
            "Git agent not found. Skipping repository analysis workflow."
        )
    elif not orchestrator.copilot_agent:
        output_handler.log_error(
            "Copilot agent not found. Skipping repository analysis workflow."
        )
    else:
        try:
            workflow_result = orchestrator.execute_workflow(
                "repository_analysis", workflow_config
            )
            output_handler.log_info(
                f"Workflow 'repository_analysis' result status: {workflow_result.get('status')}"
            )
            if workflow_result.get("status") == "success":
                output_handler.log_success( # Changed to log_success for successful workflow
                    f"Workflow 'repository_analysis' completed successfully. Report: {workflow_result.get('results', {}).get('report_path')}"
                )
                # Optionally log more details from results if needed
                # output_handler.log_debug(f"Workflow results: {json.dumps(workflow_result.get('results'), indent=2)}")
            else:
                output_handler.log_error(
                    f"Workflow 'repository_analysis' FAILED. Error: {workflow_result.get('error', 'Unknown error')}, Details: {workflow_result.get('workflow_status', {}).get('error')}"
                )
        except Exception as e:
            output_handler.log_error(
                f"Error executing 'repository_analysis' workflow: {e}", exc_info=True
            )

    # 5. Post-Run Log Analysis (Simplified Example)
    print("\n--- 5. Post-Run Log Analysis ---")
    log_file_to_analyze = os.path.join(log_dir, "diagnostic_run.log")
    if os.path.exists(log_file_to_analyze):
        error_count = 0
        critical_count = 0
        with open(log_file_to_analyze, "r", encoding="utf-8") as f_log:
            for line in f_log:
                if "ERROR" in line:
                    error_count += 1
                if "CRITICAL" in line:
                    critical_count += 1
        output_handler.log_info(f"Log analysis: Found {error_count} ERROR(s) and {critical_count} CRITICAL error(s) in {log_file_to_analyze}.")
        if error_count > 0 or critical_count > 0:
            output_handler.log_warning("Potential issues detected in the log file. Please review.")
        else:
            output_handler.log_success("Log analysis: No ERROR or CRITICAL messages found.")
    else:
        output_handler.log_warning(f"Log file {log_file_to_analyze} not found for analysis.")

    output_handler.log_info("--- Diagnostic Tests Completed ---")
    logging.shutdown() # Ensure all log handlers are closed properly

if __name__ == "__main__":
    main()
