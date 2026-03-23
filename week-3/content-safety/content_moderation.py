import os
import json
from azure.ai.contentsafety import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

try:
    from pygments import highlight
    from pygments.lexers import JsonLexer
    from pygments.formatters import TerminalFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


def analyze_text(input_text):
    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
    try:
        response = client.analyze_text({"text": input_text})

        # Convert response to dictionary
        response_dict = {
            "categories_analysis": [
                {
                    "category": cat.category,
                    "severity": cat.severity
                }
                for cat in response.categories_analysis
            ],
            "results_details": response.result_details if hasattr(response, 'result_details') else None
        }

        # Pretty print JSON
        json_str = json.dumps(response_dict, indent=2)

        # Apply syntax highlighting if available
        if HAS_PYGMENTS:
            print(highlight(json_str, JsonLexer(), TerminalFormatter()))
        else:
            print(json_str)
    except HttpResponseError as e:
        print("An error occurred:", e.message)


if __name__ == "__main__":
    input_text = input("Enter your text: ")  # Replace this with text to analyze
    analyze_text(input_text)
