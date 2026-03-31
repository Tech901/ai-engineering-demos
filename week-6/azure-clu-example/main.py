import requests
import json
import os

endpoint = os.environ["AZURE_ENDPOINT"]
api_key = os.environ["AZURE_API_KEY"]
project_name = "TravelChatbotCLU"
deployment_name = "TravelChatbotDeployment"

# The endpoint for calling the deployed model
url = (
    f"{endpoint.rstrip('/')}"
    "/language/:analyze-conversations"
    "?api-version=2024-11-15-preview"
)

# Headers including the API key
headers = {
    "Ocp-Apim-Subscription-Key": api_key,
    "Content-Type": "application/json"
}

# The data to send in the request
data = {
    "kind": "Conversation",
    "analysisInput": {
        "conversationItem": {
            "id": "1",
            "text": "I want to book a flight to New York next Monday",
            "modality": "text",
            "language": "en",
            "participantId": "1"
        }
    },
    "parameters": {
        "projectName": project_name,
        "verbose": True,
        "deploymentName": deployment_name,
        "stringIndexType": "TextElement_V8"
    }
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(json.dumps(result, indent=2))
