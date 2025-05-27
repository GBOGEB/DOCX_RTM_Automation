from config.openai_integration import initialize_openai
from agents.requirement_analyzer import analyze_requirement, check_traceability
import pandas as pd

def process_requirements_document(document_path):
    """Process a requirements document and generate analysis"""
    # Example pipeline that uses your OpenAI integration

    # 1. Parse document (simplified example)
    requirements = []
    with open(document_path, 'r') as f:
        for line in f:
            if line.strip().startswith("REQ-"):
                requirements.append(line.strip())

    # 2. Analyze each requirement using OpenAI
    results = []
    for req in requirements:
        analysis = analyze_requirement(req)
        results.append({
            "requirement": req,
            "analysis": analysis
        })

    # 3. Check traceability between requirements
    traceability_matrix = check_traceability(requirements)

    # 4. Return results
    return pd.DataFrame(results), traceability_matrix

# Usage example
if __name__ == "__main__":
    results, traceability = process_requirements_document("path/to/requirements.txt")
    results.to_excel("requirements_analysis.xlsx")
    print(traceability)
