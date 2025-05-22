import yaml
import os
import subprocess
import sys


def run_pipeline():
    """Run the document processing pipeline defined in paths.yaml"""
    
    # Load configuration
    try:
        with open('config/paths.yaml', 'r') as file:
            config = yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False
    
    # Get pipeline steps
    pipeline_steps = config.get('pipeline', {}).get('steps', [])
    if not pipeline_steps:
        print("No pipeline steps defined in configuration.")
        return False
    
    # Execute each enabled step
    python_path = config.get('python_path', 'python')
    
    for step in pipeline_steps:
        if step.get('enabled', False):
            script_path = step.get('script')
            name = step.get('name', script_path)
            
            if not script_path:
                print(f"Warning: No script defined for step '{name}', skipping.")
                continue
            
            print(f"\n{'=' * 50}")
            print(f"Running pipeline step: {name}")
            print(f"{'=' * 50}")
            
            cmd = [python_path, script_path]
            try:
                process = subprocess.run(cmd, check=True)
                print(f"Step '{name}' completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"Error running step '{name}': {e}")
                return False
    
    print("\nPipeline execution completed successfully!")
    return True

if __name__ == "__main__":
    success = run_pipeline()
    sys.exit(0 if success else 1)