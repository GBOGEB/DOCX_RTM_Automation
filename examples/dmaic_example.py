import os
import sys

# Add the project root to path if needed
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from dmaic import DMAICHandler, DMAICPhase
from config.openai_integration import initialize_openai

def run_example_dmaic_session():
    """Run an example DMAIC session with OpenAI integration"""
    print("Starting DMAIC Process Example...")

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

    print("\n=== DMAIC Process Example ===")
    # Create a new DMAIC project
    dmaic_project_name = "Document RTM Automation Improvement"
    dmaic = DMAICHandler(dmaic_project_name, client)
    if not dmaic: # Basic check, constructor might not return None but good practice
        print(f"Error: Failed to initialize DMAICHandler for project '{dmaic_project_name}'.")
        return
    print(f"DMAIC Handler for '{dmaic_project_name}': Initialized successfully.")

    # Start with Define phase
    print("\n" + "=" * 50)
    print(dmaic.start_phase(DMAICPhase.DEFINE))
    print("=" * 50)

    # Example interactions for Define phase
    define_questions = [
        "Our problem is that requirements traceability in our documents is manual and error-prone. Can you help me define this problem more precisely?",
        "Who are the key stakeholders we should consider for this project?",
        "What would be good success metrics for our RTM automation project?"
    ]

    for question in define_questions:
        print(f"\nUser: {question}")
        response = dmaic.interact(question)
        print(f"DMAIC Agent: {response}")

    # Complete Define phase with outputs
    define_outputs = {
        "problem_statement": "Manual requirements traceability in documentation is time-consuming, error-prone, and difficult to maintain, leading to reduced productivity and potential compliance issues.",
        "goal": "Automate 90% of the requirements traceability process within 3 months, reducing manual effort by 70% and documentation errors by 80%.",
        "scope": "The DOCX RTM Automation project will focus on automating requirements traceability in technical documentation across all product lines."
    }

    print("\n" + dmaic.complete_phase(define_outputs))
    print("\n" + dmaic.get_phase_summary(DMAICPhase.DEFINE))

    # Start Measure phase as another example
    print("\n" + "=" * 50)
    print(dmaic.start_phase(DMAICPhase.MEASURE))
    print("=" * 50)

    measure_question = "What metrics should we collect to establish a baseline for our current manual RTM process?"
    print(f"\nUser: {measure_question}")
    response = dmaic.interact(measure_question)
    print(f"DMAIC Agent: {response}")

    # Save the project data
    saved_path = dmaic.save_project()
    if saved_path:
        print(f"\nProject data saved to: {saved_path}")
        if not os.path.exists(saved_path):
            print(f"Warning: DMAIC project save reported success, but file not found at {saved_path}")
    else:
        print("\nWarning: DMAIC project data not saved (save_project returned None or empty).")

    print("\nThis example demonstrates integration of the DMAIC methodology with OpenAI.")
    print("In a real implementation, you would proceed through all DMAIC phases.")

if __name__ == "__main__":
    run_example_dmaic_session()