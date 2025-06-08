import subprocess


def run_jenkins_job(job_name, jenkins_url, username, api_token):
    """
    Trigger a Jenkins job using the Jenkins REST API.

    Args:
        job_name (str): Name of the Jenkins job to trigger.
        jenkins_url (str): Base URL of the Jenkins server.
        username (str): Jenkins username.
        api_token (str): Jenkins API token.

    Returns:
        str: Response from the Jenkins server.
    """
    trigger_url = f"{jenkins_url}/job/{job_name}/build"
    response = subprocess.run(
        ["curl", "-X", "POST", trigger_url, "--user", f"{username}:{api_token}"],
        capture_output=True,
        text=True,
    )
    return response.stdout


def main():
    # Jenkins configuration
    job_name = "RTM_Automation"
    jenkins_url = "http://your-jenkins-url"
    username = "your-username"
    api_token = "your-api-token"

    # Trigger Jenkins job
    print("Triggering Jenkins job...")
    response = run_jenkins_job(job_name, jenkins_url, username, api_token)
    print("Response from Jenkins:")
    print(response)


if __name__ == "__main__":
    main()
