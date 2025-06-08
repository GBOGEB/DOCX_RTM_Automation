"""
Creates example JSON requests for integration testing.

Implements:
- IM-1: Push/Pull Mechanisms - Creates sample push requests
- IR-2: API Interface - Demonstrates API request formatting
"""

import json
import os

# Ensure the 'data' directory exists
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

filename = os.path.join(data_dir, "my_requests.jsonl")
n_requests = 10  # You can change this to the number of requests you want

# Example for embedding requests (implements IR-2: API Interface)
jobs = []
for i in range(n_requests):
    # Create standardized API request format as per IR-2
    jobs.append(
        {
            "model": "text-embedding-3-small",  # Or your desired embedding model
            "input": f"This is sample text to embed, item {i + 1}.",
            "metadata": {
                "original_id": f"doc_{i + 1}",
                "request_type": "embedding",
                "implements": "IR-2",
            },
        }
    )

# Example for chat completion requests (implements IM-1: Push mechanism)
chat_jobs = []
for i in range(n_requests):
    # Create standardized push request format as per IM-1
    chat_jobs.append(
        {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": f"Translate 'hello world {i + 1}' to French.",
                },
            ],
            "metadata": {
                "task_id": f"translation_{i + 1}",
                "push_target": "translation_service",
                "implements": "IM-1",
            },
        }
    )

# Write embedding requests to file
with open(filename, "w") as f:
    for job in jobs:
        json_string = json.dumps(job)
        f.write(json_string + "\n")

# Write chat requests to a separate file (implements IM-1: Push mechanism)
chat_filename = os.path.join(data_dir, "chat_requests.jsonl")
with open(chat_filename, "w") as f:
    for job in chat_jobs:
        json_string = json.dumps(job)
        f.write(json_string + "\n")

print("Successfully created:")
print(f"- '{filename}' with {len(jobs)} embedding requests (IR-2)")
print(f"- '{chat_filename}' with {len(chat_jobs)} chat requests (IM-1)")
