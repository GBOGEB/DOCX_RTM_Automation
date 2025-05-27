import os
import sys
import json
from datetime import datetime, timedelta

# Add the project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from dmaic import DMAICHandler, DMAICPhase
from config.openai_integration import initialize_openai
from utils.output_handler import OutputHandler
from utils.paths_manager import PathsManager
from agents.dmaic_cicd_agent import DMAICCICDAgent

def generate_mock_pipeline_data():
    """Generate mock CI/CD pipeline data for demonstration purposes"""
    return {
        "pipeline_id": "rtm-automation-pipeline",
        "build_duration": 345,  # seconds
        "start_time": datetime.now() - timedelta(hours=1),
        "end_time": datetime.now() - timedelta(minutes=55),
        "status": "success",
        "test_results": {
            "total": 120,
            "passed": 115,
            "failed": 5,
            "skipped": 0,
            "coverage": 78.5,  # percentage
            "success_rate": 95.8
        },
        "deployments": [
            {"environment": "dev", "status": "success", "duration": 45},
            {"environment": "test", "status": "success", "duration": 62}
        ],
        "lead_time": 96,  # minutes from commit to deployment
        "total": 10,  # total number of changes
        "failures": 1   # number of failed changes
    }

def generate_mock_pipeline_runs(num_runs=10):
    """Generate a series of mock CI/CD pipeline runs"""
    mock_runs = []
    base_duration = 300  # base build duration in seconds

    for i in range(num_runs):
        # Vary the build duration slightly for each run
        build_duration = base_duration + (i - 5) * 10

        # Alternate between success and failure with higher success probability
        status = "success" if i % 5 != 0 else "failure"

        # Create mock test results with some variability
        test_total = 120
        test_passed = test_total - (i % 7)  # Vary the number of passing tests

        run = {
            "run_id": f"run-{i+1}",
            "pipeline_id": "rtm-automation-pipeline",
            "build_duration": build_duration,
            "status": status,
            "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
            "test_results": {
                "total": test_total,
                "passed": test_passed,
                "failed": test_total - test_passed,
                "success_rate": (test_passed / test_total) * 100
            }
        }

        # Add failure reason for failed runs
        if status == "failure":
            failure_reasons = [
                "Test failure in authentication module",
                "Missing dependency in build script",
                "Integration test timeout",
                "Environment configuration error",
                "Resource constraints during deployment"
            ]
            run["failure_reason"] = failure_reasons[i % len(failure_reasons)]

        mock_runs.append(run)

    return mock_runs

def run_dmaic_cicd_example():
    """Run an example of the DMAIC CI/CD agent"""
    print("Starting DMAIC CI/CD Agent Example...")

    # --- Sanity Checks ---
    print("\n--- Sanity Checks ---")
    if not os.path.isdir(project_root):
        print(f"Error: Project root directory not found: {project_root}")
        return
    print(f"Project root: {project_root} (Exists)")

    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set. OpenAI calls will likely fail.")
    else:
        print("OPENAI_API_KEY: Set")
    # --- End Sanity Checks ---

    print("\nInitializing OpenAI client...")
    client = initialize_openai()
    if not client:
        print("Error: Failed to initialize OpenAI client. Check API key and connectivity. Exiting example.")
        return
    print("OpenAI client: Initialized successfully.")

    # Initialize supporting objects
    print("\nInitializing supporting objects (PathsManager, OutputHandler, DMAICHandler)...")
    paths = PathsManager()
    if not paths: # Basic check
        print("Error: Failed to initialize PathsManager.")
        return
    print("PathsManager: Initialized.")

    output_dir_path = paths.get_output_dir(create_timestamped=True)
    if not output_dir_path or not os.path.isdir(os.path.dirname(output_dir_path)): # Check if parent of timestamped dir exists
        print(f"Error: Output directory path from PathsManager is invalid or its parent does not exist: {output_dir_path}")
        # Attempt to create project_root/outputs as a fallback for the OutputHandler
        fallback_output_dir = os.path.join(project_root, "outputs", "dmaic_cicd_example_logs")
        print(f"Attempting to use fallback output directory: {fallback_output_dir}")
        try:
            os.makedirs(fallback_output_dir, exist_ok=True)
            output_dir_path = fallback_output_dir
        except OSError as e:
            print(f"Error: Could not create fallback output directory {fallback_output_dir}. {e}")
            return
    output = OutputHandler(output_dir_path)
    print(f"OutputHandler: Initialized (logs at {output_dir_path}).")

    dmaic_project_name = "CI/CD Pipeline Optimization"
    dmaic = DMAICHandler(dmaic_project_name, client)
    if not dmaic: # Basic check
        print(f"Error: Failed to initialize DMAICHandler for project '{dmaic_project_name}'.")
        return
    print(f"DMAICHandler for '{dmaic_project_name}': Initialized.")

    print("\n=== DMAIC CI/CD Agent Example ===")
    # Create the DMAIC CI/CD agent
    cicd_agent = DMAICCICDAgent(dmaic, output)
    if not cicd_agent: # Basic check
        print("Error: Failed to initialize DMAICCICDAgent.")
        return
    print("DMAICCICDAgent: Initialized successfully.")

    # Initialize the project
    print("\nInitializing CI/CD DMAIC project...")
    pipeline_name = "RTM-Automation-Build-Deploy"
    project_config = {
        "description": "Optimize the CI/CD pipeline for the RTM Automation project",
        "stakeholders": ["Development team", "QA team", "DevOps", "Product owners"],
        "success_metrics": ["Build time reduction", "Test coverage increase", "Deployment frequency"]
    }

    project_init = cicd_agent.initialize_project(pipeline_name, project_config)
    print(f"Project initialized with problem statement: {project_init['problem_statement'][:100]}...")

    # Collect baseline metrics
    print("\nCollecting baseline metrics...")
    mock_pipeline_data = generate_mock_pipeline_data()
    baseline = cicd_agent.collect_baseline_metrics(mock_pipeline_data)
    print(f"Baseline metrics collected: {json.dumps(baseline['baseline_metrics'], indent=2)}")

    # Analyze pipeline performance
    print("\nAnalyzing pipeline performance...")
    mock_runs = generate_mock_pipeline_runs(10)
    analysis = cicd_agent.analyze_pipeline_performance(mock_runs)
    print(f"Analysis completed. Sample findings: {analysis['root_cause_analysis'][:150]}...")

    # Generate improvement plan
    print("\nGenerating improvement plan...")
    improve_plan = cicd_agent.generate_improvement_plan(analysis)
    print(f"Improvement plan generated. Top solution: {improve_plan['proposed_solutions'][:150]}...")

    # Establish control plan
    print("\nEstablishing control plan...")
    control_plan = cicd_agent.establish_control_plan(improve_plan)
    print(f"Control plan established. Monitoring approach: {control_plan['monitoring_plan'][:150]}...")

    # Generate full report
    print("\nGenerating comprehensive DMAIC CI/CD report...")
    project_data = {
        "define": project_init,
        "measure": baseline,
        "analyze": analysis,
        "improve": improve_plan,
        "control": control_plan
    }

    report_path = cicd_agent.generate_report(project_data)
    if report_path and os.path.exists(report_path):
        print(f"\nDMAIC CI/CD report generated and saved to: {report_path}")
    elif report_path:
        print(f"\nDMAIC CI/CD report generation reported success, but file not found at: {report_path}")
    else:
        print("\nWarning: DMAIC CI/CD report not generated or path not returned.")
    print("\nThis example demonstrates integration of DMAIC methodology with CI/CD processes.")

if __name__ == "__main__":
    run_dmaic_cicd_example()
