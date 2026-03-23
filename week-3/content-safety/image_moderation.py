import os
import json
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

try:
    from pygments import highlight
    from pygments.lexers import JsonLexer
    from pygments.formatters import TerminalFormatter
    HAS_PYGMENTS = True
except ImportError:
    HAS_PYGMENTS = False


def analyze_image(image_path):
    key = os.environ["CONTENT_SAFETY_KEY"]
    endpoint = os.environ["CONTENT_SAFETY_ENDPOINT"]
    client = ContentSafetyClient(endpoint, AzureKeyCredential(key))
    try:
        with open(image_path, "rb") as file:
            request = AnalyzeImageOptions(image=ImageData(content=file.read()))

        response = client.analyze_image(request)

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
    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")


if __name__ == "__main__":
    image_path = input("Enter the path to the image: ")
    analyze_image(image_path)
