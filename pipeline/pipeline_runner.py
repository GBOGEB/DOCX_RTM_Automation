import os
import subprocess


def run_pipeline(pipeline_script, *args):
    """
    Executes the given pipeline script with optional arguments.

    :param pipeline_script: Path to the pipeline script to execute.
    :param args: Additional arguments to pass to the script.
    :return: The output and error messages from the script execution.
    """
    if not os.path.exists(pipeline_script):
        raise FileNotFoundError(f"Pipeline script not found: {pipeline_script}")

    command = ["python", pipeline_script] + list(args)
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the pipeline: {e}")
        return e.stdout, e.stderr


if __name__ == "__main__":
    # Example usage
    pipeline_script_path = "example_pipeline.py"  # Replace with your script path
    arguments = ["--arg1", "value1", "--arg2", "value2"]  # Replace with your arguments

    try:
        stdout, stderr = run_pipeline(pipeline_script_path, *arguments)
        print("Pipeline Output:")
        print(stdout)
        if stderr:
            print("Pipeline Errors:")
            print(stderr)
    except Exception as e:
        print(f"Failed to execute pipeline: {e}")
