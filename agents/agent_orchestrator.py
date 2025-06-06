"""
Agent Orchestrator for managing and coordinating various agents in the system.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List, Optional, Union
from threading import Lock
from pathlib import Path

# --- Start of standard boilerplate for scripts in packages ---
_self_path_orchestrator = Path(__file__).resolve()
# project_root/agents/agent_orchestrator.py -> project_root is parents[1]
_project_root_orchestrator = _self_path_orchestrator.parents[1]

if str(_project_root_orchestrator) not in sys.path:
    sys.path.insert(0, str(_project_root_orchestrator))

if __name__ == "__main__" and not __package__:
    # Calculate the package name based on the file's path relative to the project root
    _package_path_obj = _self_path_orchestrator.parent.relative_to(
        _project_root_orchestrator
    )
    __package__ = str(_package_path_obj).replace(
        os.sep, "."
    )  # Changed Path().sep to os.sep
# --- End of standard boilerplate ---

# Application-specific imports
from dmaic import DMAICHandler  # pylint: disable=wrong-import-position # noqa: E402
from utils.output_handler import (
    OutputHandler,
)  # pylint: disable=wrong-import-position # noqa: E402
from utils.paths_manager import (
    PathsManager,
)  # pylint: disable=wrong-import-position # noqa: E402

from agents.agent_common import (  # pylint: disable=wrong-import-position # noqa: E402
    BaseAgent,
    AgentRole,
    AgentMessage,
    AgentPriority,
    AgentCapability,
    PING_REQUEST,
)
from agents.dmaic_cicd_agent import (
    DMAICCICDAgent,
)  # pylint: disable=wrong-import-position # noqa: E402
from agents.git_agent import (
    GitAgent,
)  # pylint: disable=wrong-import-position # noqa: E402
from agents.requirement_analyzer import (  # pylint: disable=wrong-import-position # noqa: E402
    RequirementAnalysisAgent,
    TraceabilityAnalysisAgent,
)
from agents.copilot_agent import (
    CopilotAgent,
)  # pylint: disable=wrong-import-position # noqa: E402


class AgentOrchestrator:
    """
    Orchestrator that manages communication and coordination between all agents in the system.
    Acts as the central hub for agent messages and task assignments.
    """

    def __init__(self, dmaic_handler: DMAICHandler, output_handler: OutputHandler):
        """Initialize the agent orchestrator"""
        self.dmaic_handler = dmaic_handler
        self.output_handler = output_handler
        self.paths = PathsManager()

        # Tracking all registered agents
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_by_role: Dict[AgentRole, List[BaseAgent]] = {
            role: [] for role in AgentRole
        }
        self.agent_capabilities: Dict[str, List[str]] = {}

        # Message management
        self.message_log: List[Dict[str, Any]] = []
        self.pending_responses: Dict[str, Dict[str, Any]] = {}
        self.message_lock = Lock()

        # Automated agents
        self.git_agent = None
        self.copilot_agent = None
        self.cicd_agent = None
        self.req_analysis_agent = None
        self.trace_analysis_agent = None

        # Initialize ourselves as the first agent
        self.orchestrator_agent = BaseAgent()  # Call with no arguments
        self.orchestrator_agent.agent_id = "orchestrator"
        self.orchestrator_agent.role = AgentRole.ORCHESTRATOR
        self.orchestrator_agent.output_handler = self.output_handler
        self.orchestrator_agent.capabilities = (
            []
        )  # Orchestrator might not have specific capabilities

        self.register_agent(self.orchestrator_agent)

        self.output_handler.log_info("Agent Orchestrator initialized")

    def initialize_standard_agents(self):
        """Initialize the standard set of agents used by the system"""
        # Initialize Git agent
        self.git_agent = GitAgent(
            "git_agent_01", self.dmaic_handler, self.output_handler
        )
        self.register_agent(self.git_agent)

        # Initialize Copilot agent
        self.copilot_agent = CopilotAgent(self.dmaic_handler, self.output_handler)
        self.register_agent(self.copilot_agent)

        # Initialize CI/CD agent
        self.cicd_agent = DMAICCICDAgent(self.dmaic_handler, self.output_handler)
        self.register_agent(self.cicd_agent)

        # Initialize Requirement Agents
        self.req_analysis_agent = RequirementAnalysisAgent(
            "req_analyzer_01",
            output_handler_param=self.output_handler,  # Use the correct parameter name
        )
        self.register_agent(self.req_analysis_agent)

        self.trace_analysis_agent = TraceabilityAnalysisAgent(
            "trace_analyzer_01",
            output_handler_param=self.output_handler,  # Use the correct parameter name
        )
        self.register_agent(self.trace_analysis_agent)

        self.output_handler.log_info("Standard agents initialized")

    def register_agent(self, agent: BaseAgent) -> bool:
        """Register an agent with the orchestrator"""
        if agent.agent_id in self.agents:
            self.output_handler.log_error(
                f"Agent with ID {agent.agent_id} already registered"
            )
            return False

        # Register agent
        self.agents[agent.agent_id] = agent
        self.agent_by_role[agent.role].append(agent)

        # Store capabilities, converting enum to name if it's an enum
        self.agent_capabilities[agent.agent_id] = [
            cap.name if isinstance(cap, AgentCapability) else cap
            for cap in agent.capabilities
        ]

        # Connect agent to orchestrator if the method exists
        if hasattr(agent, "register_with_orchestrator") and callable(
            agent.register_with_orchestrator
        ):
            try:
                agent.register_with_orchestrator(self)
            except Exception as e:
                self.output_handler.log_error(
                    f"Error calling register_with_orchestrator for agent {agent.agent_id}: {e}"
                )
        else:
            self.output_handler.log_debug(
                f"Agent {agent.agent_id} does not have a callable 'register_with_orchestrator' method. Skipping call."
            )

        self.output_handler.log_info(
            f"Agent {agent.agent_id} registered with role {agent.role.name}"
        )
        return True

    def route_message(self, message: AgentMessage) -> Optional[str]:
        """Route a message to the appropriate agent(s)"""
        with self.message_lock:
            # Log the message
            log_entry = message.to_dict()
            # For StandardAgentResponse in content, log a summary
            if isinstance(message.content, dict) and "status" in message.content:
                log_entry["content_summary"] = {
                    "status": message.content.get("status"),
                    "message": (
                        str(message.content.get("message", ""))[:100] + "..."
                        if message.content.get("message")
                        else None
                    ),
                    "has_data": message.content.get("data") is not None,
                    "has_markdown": message.content.get("markdown_content") is not None,
                }
                if "data" in log_entry:
                    del log_entry["data"]
                if "content" in log_entry:
                    del log_entry["content"]

            self.message_log.append(log_entry)

            # If broadcast, send to all agents except sender
            if message.target == "broadcast":
                for agent_id, agent in self.agents.items():
                    if agent_id != message.source:
                        agent.receive_message(message)
                return message.id

            # Direct message to specific agent
            if message.target in self.agents:
                self.agents[message.target].receive_message(message)

                # If response required, track it
                if message.requires_response:
                    self.pending_responses[message.id] = {
                        "source": message.source,
                        "timestamp": message.timestamp,
                        "status": "pending",
                    }
                return message.id
            else:
                self.output_handler.log_error(f"Unknown target agent: {message.target}")
                return None

    def find_agent_by_capability(
        self, capability: Union[str, AgentCapability]
    ) -> List[str]:
        """Find agents that have a specific capability"""
        matching_agents = []
        cap_name_to_find = (
            capability.name if isinstance(capability, AgentCapability) else capability
        )

        for agent_id, capabilities in self.agent_capabilities.items():
            if cap_name_to_find in capabilities:
                matching_agents.append(agent_id)

        return matching_agents

    def update_all_agents(self) -> Dict[str, Any]:
        """Update all registered agents"""
        agent_statuses = {}

        for agent_id, agent in self.agents.items():
            try:
                status = agent.update()
                agent_statuses[agent_id] = status
            except Exception as e:
                self.output_handler.log_error(f"Error updating agent {agent_id}: {e}")
                agent_statuses[agent_id] = {"status": "error", "error": str(e)}

        return agent_statuses

    def check_message_timeouts(self):
        """Check for and handle timed-out messages"""
        # Implementation placeholder for handling message timeouts
        current_time = time.time()
        with self.message_lock:
            for msg_id, response_info in list(self.pending_responses.items()):
                if current_time - response_info["timestamp"] > 30:  # 30 seconds timeout
                    self.output_handler.log_warning(
                        f"Message {msg_id} timed out waiting for response"
                    )
                    self.pending_responses[msg_id]["status"] = "timeout"

    def ping_agent(
        self, target_agent_id: str, timeout_seconds: float = 5.0
    ) -> Dict[str, Any]:
        """
        Sends a PING_REQUEST to a target agent and waits for a response.

        Args:
            target_agent_id: The ID of the agent to ping.
            timeout_seconds: How long to wait for a PONG response.

        Returns:
            A dictionary indicating the status of the ping (success, error, timeout).
        """
        if target_agent_id not in self.agents:
            self.output_handler.log_error(
                f"Ping failed: Agent '{target_agent_id}' not found."
            )
            return {
                "status": "error",
                "message": f"Agent '{target_agent_id}' not found.",
            }

        ping_payload = {"data": f"Ping from orchestrator at {time.time()}"}
        ping_message = AgentMessage(
            source=self.orchestrator_agent.agent_id,
            target=target_agent_id,
            message_type=PING_REQUEST,
            content=ping_payload,
            requires_response=True,
            priority=AgentPriority.HIGH,
        )
        # The correlation_id is automatically generated if not provided,
        # and will be used to match the response.

        self.output_handler.log_info(
            f"Pinging agent '{target_agent_id}' with message ID {ping_message.id} (correlation: {ping_message.correlation_id})."
        )

        # Send the message. The response will come back as another message to the orchestrator.
        # The BaseAgent.process_inbox will handle sending the response message.
        self.route_message(ping_message)

        start_time = time.time()
        expected_response_message_type = f"{PING_REQUEST}_response"

        while time.time() - start_time < timeout_seconds:
            with self.message_lock:  # Ensure thread-safe access to message_log
                # Iterate backwards for recent messages first
                for logged_msg_dict in reversed(self.message_log):
                    if (
                        logged_msg_dict.get("source") == target_agent_id
                        and logged_msg_dict.get("target")
                        == self.orchestrator_agent.agent_id
                        and logged_msg_dict.get("message_type")
                        == expected_response_message_type
                        and logged_msg_dict.get("correlation_id")
                        == ping_message.correlation_id
                    ):
                        pong_content = logged_msg_dict.get("content", {})
                        round_trip_time = (time.time() - start_time) * 1000  # ms
                        self.output_handler.log_info(
                            f"Pong received from '{target_agent_id}' in {round_trip_time:.2f} ms. Content: {pong_content}"
                        )
                        return {
                            "status": "success",
                            "message": f"Pong received from {target_agent_id}.",
                            "data": {
                                "pong_content": pong_content,
                                "round_trip_time_ms": round_trip_time,
                                "correlation_id": ping_message.correlation_id,
                            },
                        }
            time.sleep(0.1)  # Poll every 100ms

        self.output_handler.log_warning(
            f"Ping to '{target_agent_id}' timed out after {timeout_seconds} seconds (correlation: {ping_message.correlation_id})."
        )
        return {
            "status": "timeout",
            "message": f"Ping to '{target_agent_id}' timed out.",
            "data": {"correlation_id": ping_message.correlation_id},
        }

    def execute_workflow(
        self, workflow_name: str, workflow_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a predefined workflow involving multiple agents"""
        self.output_handler.log_info(f"Starting workflow: {workflow_name}")

        # Log workflow start
        workflow_id = f"workflow_{workflow_name}_{int(time.time())}"
        workflow_status = {
            "workflow_id": workflow_id,
            "name": workflow_name,
            "start_time": time.time(),
            "status": "running",
            "steps": [],
        }

        try:
            if workflow_name == "repository_analysis":
                # Example workflow: Analyze a repository and generate reports
                repo_url = workflow_config.get("repository_url")
                if not repo_url:
                    raise ValueError(
                        "repository_url is required for repository_analysis workflow"
                    )
                branch = workflow_config.get("branch", "main")
                target_dir_name = (
                    repo_url.split("/")[-1].replace(".git", "")
                    if repo_url
                    else "cloned_repo"
                )
                workflow_specific_local_repo_path = os.path.join(
                    self.paths.data_dir, "workflow_clones", target_dir_name
                )

                # Step 1: Git agent clones/pulls the repo
                self.output_handler.log_info(
                    f"Workflow step 1: Cloning/pulling repository {repo_url} to {workflow_specific_local_repo_path}"
                )
                workflow_status["steps"].append(
                    {
                        "step": 1,
                        "name": "clone_or_pull_repository",
                        "status": "running",
                        "input": {
                            "url": repo_url,
                            "branch": branch,
                            "local_path": workflow_specific_local_repo_path,
                        },
                    }
                )
                if not self.git_agent:
                    raise ValueError(
                        "Git agent not initialized for repository_analysis workflow"
                    )

                # Ensure the target directory for cloning exists
                os.makedirs(
                    os.path.dirname(workflow_specific_local_repo_path), exist_ok=True
                )

                # Directly call the agent's method for synchronous execution within the workflow
                repo_path_result = self.git_agent.clone_repository(
                    repo_url, branch, local_path=workflow_specific_local_repo_path
                )

                if not repo_path_result or not os.path.isdir(repo_path_result):
                    workflow_status["steps"][-1]["status"] = "failed"
                    workflow_status["steps"][-1][
                        "error"
                    ] = f"Failed to clone/pull repository. Path: {repo_path_result}"
                    raise ValueError(
                        f"Failed to clone/pull repository. Path: {repo_path_result}"
                    )

                workflow_status["steps"][-1]["status"] = "completed"
                workflow_status["steps"][-1]["output"] = {"repo_path": repo_path_result}
                final_repo_path = repo_path_result

                # Step 2: Copilot agent analyzes repository
                self.output_handler.log_info(
                    f"Workflow step 2: Analyzing repository at {final_repo_path}"
                )
                workflow_status["steps"].append(
                    {
                        "step": 2,
                        "name": "analyze_repository",
                        "status": "running",
                        "input": {"repo_path": final_repo_path},
                    }
                )
                if not self.copilot_agent:
                    raise ValueError(
                        "Copilot agent not initialized for repository_analysis workflow"
                    )

                analysis_summary = self.copilot_agent.analyze_repository(
                    final_repo_path
                )
                workflow_status["steps"][-1]["status"] = "completed"
                workflow_status["steps"][-1]["output"] = {
                    "analysis_summary": analysis_summary
                }

                # Step 3: Generate report
                self.output_handler.log_info("Workflow step 3: Generating report")
                report_output_filename = (
                    f"repo_analysis_{target_dir_name}_{int(time.time())}.md"
                )
                report_output_path = os.path.join(
                    self.paths.get_output_dir(), "reports", report_output_filename
                )
                os.makedirs(os.path.dirname(report_output_path), exist_ok=True)

                workflow_status["steps"].append(
                    {
                        "step": 3,
                        "name": "generate_report",
                        "status": "running",
                        "input": {
                            "report_type": "repository_analysis_summary",
                            "data_length": len(json.dumps(analysis_summary)),
                        },
                    }
                )

                report_content = self.copilot_agent.generate_report(
                    report_type="repository_analysis_summary",
                    data=analysis_summary,
                    output_path=report_output_path,
                )
                workflow_status["steps"][-1]["status"] = "completed"
                workflow_status["steps"][-1]["output"] = {
                    "report_path": report_output_path,
                    "report_generated": bool(report_content),
                }

                workflow_status["status"] = "completed"
                workflow_status["end_time"] = time.time()
                workflow_status["duration"] = (
                    workflow_status["end_time"] - workflow_status["start_time"]
                )
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "results": {
                        "repository_path": final_repo_path,
                        "analysis_summary": analysis_summary,
                        "report_path": report_output_path,
                    },
                    "workflow_status": workflow_status,
                }

            elif workflow_name == "code_generation_and_analysis":
                # Example workflow: Generate code based on requirements, then analyze it
                language = workflow_config.get("language", "python")
                requirement = workflow_config.get("requirement")
                if not requirement:
                    raise ValueError(
                        "requirement is required for code_generation_and_analysis workflow"
                    )

                # Step 1: Copilot agent generates code
                self.output_handler.log_info(
                    f"Workflow step 1: Generating {language} code for: {requirement}"
                )
                generated_code_filename = f"generated_code_{language}_{int(time.time())}.{language if language != 'shell' else 'sh'}"
                generated_code_path = os.path.join(
                    self.paths.get_output_dir(),
                    "generated_code",
                    generated_code_filename,
                )
                os.makedirs(os.path.dirname(generated_code_path), exist_ok=True)

                workflow_status["steps"].append(
                    {
                        "step": 1,
                        "name": "generate_code",
                        "status": "running",
                        "input": {
                            "language": language,
                            "requirement": requirement,
                            "output_path": generated_code_path,
                        },
                    }
                )
                if not self.copilot_agent:
                    raise ValueError(
                        "Copilot agent not initialized for code_generation_and_analysis workflow"
                    )

                generated_code_content = self.copilot_agent.generate_code(
                    language, requirement, generated_code_path
                )
                if not generated_code_content or not os.path.exists(
                    generated_code_path
                ):
                    workflow_status["steps"][-1]["status"] = "failed"
                    workflow_status["steps"][-1][
                        "error"
                    ] = "Code generation failed or file not saved."
                    raise ValueError("Code generation failed.")

                workflow_status["steps"][-1]["status"] = "completed"
                workflow_status["steps"][-1]["output"] = {
                    "generated_code_path": generated_code_path,
                    "code_length": len(generated_code_content),
                }

                # Step 2: Copilot agent analyzes the generated code
                self.output_handler.log_info(
                    f"Workflow step 2: Analyzing generated code at {generated_code_path}"
                )
                workflow_status["steps"].append(
                    {
                        "step": 2,
                        "name": "analyze_code",
                        "status": "running",
                        "input": {"file_path": generated_code_path},
                    }
                )

                dummy_message_for_analysis = AgentMessage(
                    source=self.orchestrator_agent.agent_id,
                    target=self.copilot_agent.agent_id,
                    message_type="code_analysis_request",
                    content={"file_path": generated_code_path},
                )
                analysis_response = self.copilot_agent.analyze_code(
                    dummy_message_for_analysis.content["file_path"]
                )

                if analysis_response.get("status") != "success":
                    workflow_status["steps"][-1]["status"] = "failed"
                    workflow_status["steps"][-1]["error"] = analysis_response.get(
                        "message", "Code analysis failed."
                    )
                    raise ValueError(
                        analysis_response.get("message", "Code analysis failed.")
                    )

                workflow_status["steps"][-1]["status"] = "completed"
                workflow_status["steps"][-1]["output"] = {
                    "analysis_data": analysis_response.get("data")
                }

                workflow_status["status"] = "completed"
                workflow_status["end_time"] = time.time()
                workflow_status["duration"] = (
                    workflow_status["end_time"] - workflow_status["start_time"]
                )
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "results": {
                        "generated_code_path": generated_code_path,
                        "analysis": analysis_response.get("data"),
                    },
                    "workflow_status": workflow_status,
                }

            elif workflow_name == "pull_request_impact_analysis":
                # Workflow: Analyze a pull request for impact
                repo_url = workflow_config.get("repository_url")
                pr_number = workflow_config.get("pr_number")
                # Comment out the unused target_branch variable to avoid linting errors
                # target_branch = workflow_config.get("target_branch", "main")

                if not repo_url or not pr_number:
                    raise ValueError(
                        "repository_url and pr_number are required for pull_request_impact_analysis workflow"
                    )

                if not self.git_agent:
                    raise ValueError(
                        "Git agent not initialized for pull_request_impact_analysis workflow"
                    )
                if (
                    not self.copilot_agent and not self.req_analysis_agent
                ):  # Need at least one for analysis
                    raise ValueError(
                        "Copilot or Requirement Analysis agent not initialized for impact analysis."
                    )

                workflow_status["steps"].append(
                    {
                        "step": 1,
                        "name": "fetch_pr_details",
                        "status": "running",
                        "input": {"repo_url": repo_url, "pr_number": pr_number},
                    }
                )

                # Step 1: GitAgent fetches PR details (diff, changed files)
                pr_details = {
                    "changed_files": ["file1.py", "file2.md"],
                    "diff": "mock_diff_content",
                    "description": "Mock PR",
                }

                workflow_status["steps"][-1]["status"] = "completed"
                workflow_status["steps"][-1]["output"] = {
                    "pr_details_summary": f"Fetched {len(pr_details['changed_files'])} changed files."
                }

                # Step 2: Parse changed files (e.g., using CopilotAgent)
                parsed_content_summary = {}
                if (
                    self.copilot_agent
                    and AgentCapability.DOCUMENT_PARSING.name
                    in self.agent_capabilities.get(self.copilot_agent.agent_id, [])
                ):
                    workflow_status["steps"].append(
                        {
                            "step": 2,
                            "name": "parse_changed_files",
                            "status": "running",
                            "input": {"files_count": len(pr_details["changed_files"])},
                        }
                    )
                    parsed_content_summary = {
                        "parsed_files": len(pr_details["changed_files"]),
                        "extracted_elements": 5,
                    }  # Mock
                    workflow_status["steps"][-1]["status"] = "completed"
                    workflow_status["steps"][-1]["output"] = parsed_content_summary
                else:
                    workflow_status["steps"].append(
                        {
                            "step": 2,
                            "name": "parse_changed_files",
                            "status": "skipped",
                            "message": "Copilot agent or parsing capability not available.",
                        }
                    )

                # Step 3: Impact Assessment (e.g., using CopilotAgent or ReqAnalysisAgent)
                impact_assessment_result = {}
                analysis_agent_id_to_use = None
                if (
                    self.copilot_agent
                    and AgentCapability.IMPACT_ANALYSIS.name
                    in self.agent_capabilities.get(self.copilot_agent.agent_id, [])
                ):
                    analysis_agent_id_to_use = self.copilot_agent.agent_id
                elif (
                    self.req_analysis_agent
                    and AgentCapability.IMPACT_ANALYSIS.name
                    in self.agent_capabilities.get(self.req_analysis_agent.agent_id, [])
                ):
                    analysis_agent_id_to_use = self.req_analysis_agent.agent_id

                if analysis_agent_id_to_use:
                    workflow_status["steps"].append(
                        {
                            "step": 3,
                            "name": "perform_impact_assessment",
                            "status": "running",
                            "input": {"pr_description": pr_details["description"]},
                        }
                    )
                    impact_assessment_result = {
                        "risk_level": "medium",
                        "affected_requirements": ["REQ-001", "REQ-005"],
                        "suggestions": "Review X, Y, Z.",
                    }  # Mock
                    workflow_status["steps"][-1]["status"] = "completed"
                    workflow_status["steps"][-1]["output"] = impact_assessment_result
                else:
                    workflow_status["steps"].append(
                        {
                            "step": 3,
                            "name": "perform_impact_assessment",
                            "status": "skipped",
                            "message": "No agent with Impact Analysis capability found.",
                        }
                    )

                # Step 4: Generate Report (using OutputHandler or CopilotAgent)
                workflow_status["steps"].append(
                    {
                        "step": 4,
                        "name": "generate_pr_analysis_report",
                        "status": "running",
                    }
                )
                report_filename = (
                    f"pr_{pr_number}_impact_analysis_{int(time.time())}.md"
                )
                report_path = os.path.join(
                    self.paths.get_output_dir(), "reports", report_filename
                )
                os.makedirs(os.path.dirname(report_path), exist_ok=True)

                report_data_for_generation = {
                    "pr_details": pr_details,
                    "parsing_summary": parsed_content_summary,
                    "impact_assessment": impact_assessment_result,
                }
                with open(
                    report_path.replace(".md", ".json"), "w", encoding="utf-8"
                ) as f_json:
                    json.dump(report_data_for_generation, f_json, indent=2)
                report_content = True  # Mock that report was generated

                workflow_status["steps"][-1]["status"] = "completed"
                workflow_status["steps"][-1]["output"] = {
                    "report_path": report_path,
                    "report_generated": bool(report_content),
                }

                workflow_status["status"] = "completed"
                workflow_status["end_time"] = time.time()
                workflow_status["duration"] = (
                    workflow_status["end_time"] - workflow_status["start_time"]
                )
                return {
                    "status": "success",
                    "workflow_id": workflow_id,
                    "results": {
                        "pr_details_summary": pr_details,
                        "parsing_summary": parsed_content_summary,
                        "impact_assessment": impact_assessment_result,
                        "report_path": report_path,
                    },
                    "workflow_status": workflow_status,
                }

            else:
                self.output_handler.log_error(f"Unknown workflow: {workflow_name}")
                workflow_status["status"] = "failed"
                workflow_status["error"] = f"Unknown workflow: {workflow_name}"
                return {
                    "status": "error",
                    "error": f"Unknown workflow: {workflow_name}",
                    "workflow_id": workflow_id,
                    "workflow_status": workflow_status,
                }

        except Exception as e:
            self.output_handler.log_error(f"Error in workflow {workflow_name}: {e}")

            # Mark current step as failed
            if workflow_status["steps"]:
                workflow_status["steps"][-1]["status"] = "failed"
                workflow_status["steps"][-1]["error"] = str(e)

            workflow_status["status"] = "failed"
            workflow_status["end_time"] = time.time()
            workflow_status["error"] = str(e)

            return {
                "status": "error",
                "error": str(e),
                "workflow_id": workflow_id,
                "workflow_status": workflow_status,
            }

    def generate_system_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report about the agent system and its activities"""
        agents_status = {}
        for agent_id, agent in self.agents.items():
            agents_status[agent_id] = {
                "role": agent.role.name,
                "status": agent.status,
                "queue_size": agent.inbox.qsize(),
                "last_activity": agent.last_activity,
                "capabilities": (
                    list(agent.capabilities) if hasattr(agent, "capabilities") else []
                ),
            }

        return {
            "timestamp": time.time(),
            "agents": agents_status,
            "message_count": len(self.message_log),
            "pending_responses": len(self.pending_responses),
        }

    def save_system_state(self, filepath: Optional[str] = None) -> str:
        """Save the current state of the agent system"""
        if not filepath:
            filepath = os.path.join(
                self.paths.get_output_dir(),
                f"agent_system_state_{time.strftime('%Y%m%d_%H%M%S')}.json",
            )

        state = {
            "timestamp": time.time(),
            "agents": {},
            "message_log": self.message_log[-100:],  # Last 100 messages
            "pending_responses": self.pending_responses,
        }

        for agent_id, agent in self.agents.items():
            state["agents"][agent_id] = {
                "role": agent.role.name,
                "status": agent.status,
                "queue_size": agent.inbox.qsize(),
                "last_activity": agent.last_activity,
            }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2)
            self.output_handler.log_info(f"Agent system state saved to {filepath}")
            return filepath
        except IOError as e:
            self.output_handler.log_error(f"Error saving system state: {e}")
            return ""


# --- Test block for direct execution ---
if __name__ == "__main__":
    print(
        "Attempting to test AgentOrchestrator initialization (running agent_orchestrator.py directly)..."
    )

    # Minimal mock for OutputHandler
    class MockOutputHandler:
        """Mock OutputHandler for testing purposes."""

        def __init__(self):
            # Create a temporary output dir for the test if PathsManager needs it via get_output_dir
            # However, PathsManager is instantiated by AgentOrchestrator itself.
            # This mock is primarily for logging.
            self.test_output_dir = (
                _project_root_orchestrator / "temp_orchestrator_test_output"
            )  # Changed project_root_path
            os.makedirs(self.test_output_dir, exist_ok=True)
            print(f"MockOutputHandler: Test output directory at {self.test_output_dir}")

        def log_info(self, message, *args, **_kwargs):
            """Log an informational message."""
            # Handle string formatting with variable arguments
            if args:
                formatted_message = message % args
            else:
                formatted_message = message
            print(f"MOCK_INFO: {formatted_message}")

        def log_error(self, message, *args, **_kwargs):
            """Log an error message."""
            if args:
                formatted_message = message % args
            else:
                formatted_message = message
            print(f"MOCK_ERROR: {formatted_message}")

        def log_warning(self, message, *args, **_kwargs):
            """Log a warning message."""
            if args:
                formatted_message = message % args
            else:
                formatted_message = message
            print(f"MOCK_WARNING: {formatted_message}")

        def log_debug(self, message, *args, **_kwargs):
            """Log a debug message."""
            if args:
                formatted_message = message % args
            else:
                formatted_message = message
            print(f"MOCK_DEBUG: {formatted_message}")

        def log_critical(self, message, *args, **_kwargs):
            """Log a critical message."""
            if args:
                formatted_message = message % args
            else:
                formatted_message = message
            print(f"MOCK_CRITICAL: {formatted_message}")

    # Minimal mock for DMAICHandler
    class MockDMAICHandler:
        """Mock DMAICHandler for testing purposes."""

        def __init__(self, project_name):  # Based on previous error for DMAICHandler
            self.project_name = project_name
            print(f"MOCK_DMAICHandler initialized for project: {self.project_name}")
            # Add any methods that might be called by AgentOrchestrator or its initialized agents
            # For example, if agents call self.dmaic_handler.get_some_config()

    mock_output_handler = MockOutputHandler()

    try:
        # DMAICHandler requires 'project_name'
        mock_dmaic_handler = MockDMAICHandler("TestOrchestratorProject")
    except Exception as e_dmaic:
        print(f"CRITICAL_ERROR: Failed to initialize MockDMAICHandler: {e_dmaic}")
        sys.exit(1)

    try:
        print("Instantiating AgentOrchestrator with mocks...")
        orchestrator = AgentOrchestrator(
            dmaic_handler=mock_dmaic_handler, output_handler=mock_output_handler
        )
        print("AgentOrchestrator instantiated successfully.")

        print("Attempting to initialize standard agents...")
        # This will test if agent constructors are compatible with the mocks
        # and if BaseAgent attributes are correctly set for them.
        orchestrator.initialize_standard_agents()
        print("Standard agents initialized successfully.")

        print("\n--- AgentOrchestrator direct execution test completed. ---")
        print(f"Registered agents: {list(orchestrator.agents.keys())}")
        if orchestrator.git_agent:
            print(
                f"Git Agent ID: {orchestrator.git_agent.agent_id}, Role: {orchestrator.git_agent.role}"
            )
        if orchestrator.copilot_agent:
            print(
                f"Copilot Agent ID: {orchestrator.copilot_agent.agent_id}, Role: {orchestrator.copilot_agent.role}"
            )
        # Add more checks if needed
    except Exception as e:
        print(f"ERROR during AgentOrchestrator test: {e}")
        import traceback

        traceback.print_exc()
