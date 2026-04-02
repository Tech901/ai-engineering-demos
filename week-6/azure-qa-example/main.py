import requests
import json
import os

# Get values from environment variables
endpoint = os.getenv("AZURE_QA_ENDPOINT")
api_key = os.getenv("AZURE_QA_API_KEY")
project_name = os.getenv("AZURE_QA_PROJECT_NAME", "CustomerSupportQA")
deployment_name = os.getenv("AZURE_QA_DEPLOYMENT_NAME", "production")

# Validate required environment variables
if not endpoint:
    raise ValueError("AZURE_QA_ENDPOINT environment variable is required")
if not api_key:
    raise ValueError("AZURE_QA_API_KEY environment variable is required")
# The endpoint for calling the deployed question answering model
url = f"{endpoint}/language/:query-knowledgebases?projectName={project_name}&api-version=2021-10-01&deploymentName={deployment_name}"
# Headers including the API key
headers = {"Ocp-Apim-Subscription-Key": api_key, "Content-Type": "application/json"}
# Prompt the user for a question
question = input("Enter your question: ").strip()
if not question:
    print("No question provided. Exiting.")
    exit(0)
# The data to send in the request
data = {
    "question": question,
    "top": 3,
    "confidenceScoreThreshold": 0.2,
    "includeUnstructuredSources": True,
    "answerSpanRequest": {
        "enable": True,
        "topAnswersWithSpan": 1,
        "confidenceScoreThreshold": 0.2,
    },
}
# Send the request
response = requests.post(url, headers=headers, json=data)
result = response.json()
# Print the result
print(json.dumps(result, indent=2))
