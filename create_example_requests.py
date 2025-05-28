# filepath: C:/Users/gbonthuy/Downloads/DOCX_RTM_Automation_v1.0/create_example_requests.py
import json
import os

# Ensure the 'data' directory exists
data_dir = "data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

filename = os.path.join(data_dir, "my_requests.jsonl")
n_requests = 10  # You can change this to the number of requests you want

# Example for embedding requests
# Modify this if you are making chat completion requests
jobs = []
for i in range(n_requests):
    jobs.append({
        "model": "text-embedding-3-small", # Or your desired embedding model
        "input": f"This is sample text to embed, item {i+1}."
        # "metadata": {"original_id": f"doc_{i+1}"} # Optional metadata
    })

# Example for chat completion requests (if you were using this script for completions)
# jobs = []
# for i in range(n_requests):
#     jobs.append({
#         "model": "gpt-3.5-turbo",
#         "messages": [
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": f"Translate 'hello world {i+1}' to French."}
#         ]
#         # "metadata": {"task_id": f"translation_{i+1}"} # Optional metadata
#     })

with open(filename, "w") as f:
    for job in jobs:
        json_string = json.dumps(job)
        f.write(json_string + "\n")

print(f"Successfully created '{filename}' with {n_requests} requests.")
