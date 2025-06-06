"""
DMAIC CI/CD Agent for the RTM Automation system.
Handles CI/CD operations in the DMAIC framework.
"""

import sys
import logging
from pathlib import Path
from typing import Optional  # Removed Dict, Any
from enum import Enum

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configure logging BEFORE using logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import modules from project
# These imports are placed after sys.path modification
from agents.agent_common import (
    BaseAgent,
    AgentRole,
    AgentCapability,
)  # Removed AgentMessage

# Import DMAICHandler with proper error handling
try:
    from dmaic import (
        DMAICHandler,
        DMAICPhase,
    )  # pylint: disable=wrong-import-position # noqa: E402

    HAS_SET_PHASE = hasattr(DMAICHandler, "set_phase")  # Renamed constant
    if not HAS_SET_PHASE:
        logger.warning(
            "DMAICHandler imported but missing set_phase method. Creating compatibility wrapper."
        )

        class DMAICHandlerWrapper:
            """Wraps the DMAICHandler to provide a consistent interface for the agent."""

            def __init__(
                self,
                dmaic_handler_instance: "DMAICHandler",
                output_handler: Optional["OutputHandler"] = None,
            ):
                self.handler = dmaic_handler_instance
                self.output_handler = output_handler
                self.dmaic_phase_enum_type = DMAICPhase  # Renamed attribute

            def __getattr__(self, name):
                """Delegate attribute access to the wrapped DMAIC handler instance."""
                return getattr(self.handler, name)

except ImportError as e:
    logger.error("Failed to import DMAICHandler: %s", e)  # %-formatting

    # Create a minimal mock class for DMAICHandler to prevent further errors
    class DMAICHandler:
        """Mock DMAICHandler for when the real one can't be imported"""

        def __init__(self, project_name="DefaultProject"):
            self.project_name = project_name
            self.phase = "define"  # Default phase
            logger.warning(
                "Using mock DMAICHandler for %s", project_name
            )  # %-formatting

        def set_phase(self, phase):
            """Set the current DMAIC phase."""
            logger.info("Setting phase to: %s (mock)", phase)  # %-formatting
            self.phase = phase
            return True

        def get_phase(self):
            """Get the current DMAIC phase."""
            return self.phase


from utils.output_handler import (
    OutputHandler,
)  # pylint: disable=wrong-import-position # noqa: E402


class PipelineMetrics(Enum):
    """Critical metrics for CI/CD pipeline analysis"""

    BUILD_TIME = "build_time"
    TEST_COVERAGE = "test_coverage"
    TEST_SUCCESS_RATE = "test_success_rate"
    DEPLOYMENT_FREQUENCY = "deployment_frequency"
    LEAD_TIME = "lead_time"
    CHANGE_FAILURE_RATE = "change_failure_rate"
    MTTR = "mean_time_to_recovery"

    @property
    def lower_is_better(self) -> bool:
        """Indicates if a lower value is better for this metric."""
        return self.value in [
            PipelineMetrics.BUILD_TIME.value,
            PipelineMetrics.CHANGE_FAILURE_RATE.value,
            PipelineMetrics.MTTR.value,
            PipelineMetrics.LEAD_TIME.value,
        ]


class DMAICCICDAgent(BaseAgent):
    """
    Agent for handling CI/CD operations within the DMAIC framework.

    This agent monitors and manages CI/CD operations across the DMAIC phases:
    - Define: Set up repository structure and initial CI pipeline
    - Measure: Capture metrics and generate reports
    - Analyze: Analyze metrics and generate insights
    - Improve: Implement improvements and verify results
    - Control: Monitor long-term performance and maintain improvements
    """

    def __init__(
        self,
        dmaic_handler: Optional["DMAICHandler"] = None,
        output_handler: Optional[OutputHandler] = None,
    ):
        """
        Initialize the DMAICCICDAgent.

        Args:
            dmaic_handler: DMAIC handler for accessing project context
            output_handler: Output handler for logging and reporting
        """
        super().__init__()
        self.agent_id = "dmaic_cicd_agent"
        self.role = AgentRole.AUTOMATION  # Changed from AgentRole.ANALYST
        self.capabilities = [
            AgentCapability.CI_CD_AUTOMATION,
            AgentCapability.DMAIC_INTEGRATION,
            AgentCapability.CODE_DEPLOYMENT,
            AgentCapability.TEST_AUTOMATION,
            AgentCapability.GIT_OPERATIONS,
            AgentCapability.CODE_ANALYSIS,  # Changed from CICD_PIPELINE_ANALYSIS to CODE_ANALYSIS
        ]
        self.dmaic_handler = (
            DMAICHandlerWrapper(dmaic_handler, output_handler)
            if dmaic_handler
            else None
        )
        self.output_handler = output_handler
        self.status = "idle"
        self.current_build_id: Optional[str] = None
        self.current_test_run_id: Optional[str] = None
        self.phase: Optional[DMAICPhase] = None

        # Ensure output_handler is available before calling set_current_dmaic_phase
        # which uses self.output_handler.log_info etc.
        if self.output_handler:
            self.set_current_dmaic_phase()
        else:
            # If no output_handler, set_current_dmaic_phase might fail or log to stdout.
            # Consider a default logger or ensuring output_handler is always present.
            # For now, we proceed, but this is a potential point of failure if output_handler is None.
            print(
                "Warning: DMAICCICDAgent initialized without an output_handler. Logging in set_current_dmaic_phase might be affected.",
                file=sys.stderr,
            )
            self.set_current_dmaic_phase()

        self.status = "initialized"
        if self.output_handler:
            self.output_handler.log_info(f"DMAICCICDAgent {self.agent_id} initialized.")

    def set_current_dmaic_phase(self, phase_name: Optional[str] = None):
        """
        Set the current DMAIC phase for this agent.

        Args:
            phase_name: Optional phase name to set. If None, attempt to get from dmaic_handler.
        """
        if not self.dmaic_handler:
            if self.output_handler:
                self.output_handler.log_warning(
                    "No DMAIC handler available to set phase"
                )
            return

        try:
            if phase_name:
                # Convert string to enum if needed
                if isinstance(phase_name, str):
                    try:
                        phase_enum = getattr(
                            self.dmaic_handler.dmaic_phase_enum_type, phase_name.upper()
                        )  # Updated usage
                    except (AttributeError, ValueError):
                        if self.output_handler:
                            self.output_handler.log_error(
                                "Invalid DMAIC phase name: %s", phase_name
                            )  # %-formatting
                        return
                else:
                    phase_enum = phase_name

                # Set the phase using the handler
                if hasattr(self.dmaic_handler, "set_phase"):
                    self.dmaic_handler.set_phase(phase_enum)
                    self.phase = phase_enum
                    if self.output_handler:
                        self.output_handler.log_info(
                            "DMAIC phase set to %s", phase_enum
                        )  # %-formatting
                else:
                    if self.output_handler:
                        self.output_handler.log_warning(
                            "DMAICHandler does not have set_phase method"
                        )
            else:
                # Get current phase from handler
                if hasattr(self.dmaic_handler, "get_current_phase"):
                    self.phase = self.dmaic_handler.get_current_phase()
                    if self.output_handler:
                        self.output_handler.log_info(
                            "Current DMAIC phase: %s", self.phase
                        )  # %-formatting
                else:
                    if self.output_handler:
                        self.output_handler.log_warning(
                            "DMAICHandler does not have get_current_phase method"
                        )

        except Exception as e:
            if self.output_handler:
                self.output_handler.log_error(
                    "Error setting DMAIC phase: %s", e
                )  # %-formatting
            else:
                print(
                    "Error setting DMAIC phase: %s" % e, file=sys.stderr
                )  # %-formatting


# --- Test/Demo block for direct execution ---
if __name__ == "__main__":
    # Configure basic logging for the test run
    # This ensures that if MockOutputHandler uses logging, it's set up.
    logging.basicConfig(
        level=logging.DEBUG,  # Or INFO, depending on desired verbosity for the test
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,  # Explicitly direct to stdout for clarity in test runs
    )

    logger_main = logging.getLogger(__name__)  # __name__ is "__main__" here
    logger_main.info("Running DMAICCICDAgent directly for testing...")

    # Setup mock DMAICHandler and OutputHandler
    class MockDMAICHandler:
        """Mock DMAICHandler for testing DMAICCICDAgent."""

        def __init__(self):
            self._current_phase = DMAICPhase.DEFINE  # Default phase
            logger_main.debug("MockDMAICHandler initialized.")

        def get_current_phase(self) -> DMAICPhase:
            """Get the current DMAIC phase."""
            logger_main.debug(
                "MockDMAICHandler: get_current_phase() returning %s",
                self._current_phase,
            )
            return self._current_phase

        def set_phase(
            self, phase: DMAICPhase, status: str = "current"
        ):  # Added set_phase
            """Set the current DMAIC phase."""
            logger_main.debug(
                "MockDMAICHandler: set_phase called with phase=%s, status=%s",
                phase,
                status,
            )
            self._current_phase = phase

    class MockOutputHandler:
        """Mock OutputHandler for testing DMAICCICDAgent."""

        def __init__(self):
            # Use the logger defined in the __main__ scope for consistency
            self.logger = logger_main
            self.logger.debug("MockOutputHandler initialized.")

        def log_info(self, message, *args):
            """Logs an info message."""
            self.logger.info(message, *args)

        def log_error(self, message, *args):
            """Logs an error message."""
            self.logger.error(message, *args)

        def log_warning(self, message, *args):
            """Logs a warning message."""
            self.logger.warning(message, *args)

        def log_debug(self, message, *args):
            """Logs a debug message."""
            self.logger.debug(message, *args)

        def log_critical(self, message, *args):
            """Logs a critical message."""
            self.logger.critical(message, *args)

    mock_dmaic = MockDMAICHandler()
    mock_output = MockOutputHandler()

    logger_main.info("Initializing DMAICCICDAgent with mocks...")
    agent = DMAICCICDAgent(dmaic_handler=mock_dmaic, output_handler=mock_output)
    logger_main.info(
        "DMAICCICDAgent initialized. Agent ID: %s, Status: %s, Phase: %s",
        agent.agent_id,
        agent.status,
        agent.phase,
    )  # %-formatting

    logger_main.info("DMAICCICDAgent direct execution test completed.")
