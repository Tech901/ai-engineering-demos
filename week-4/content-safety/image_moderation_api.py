import os
import json
import base64
import requests

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

    # Construct the API endpoint
    url = f"{endpoint}contentsafety/image:analyze?api-version=2024-09-01"

    # Prepare headers
    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }

    try:
        # Read and encode image as base64
        with open(image_path, "rb") as file:
            image_data = base64.b64encode(file.read()).decode("utf-8")

        # Construct request body
        request_body = {
            "image": {
                "content": image_data
            }
        }

        # Make HTTP POST request
        response = requests.post(url, json=request_body, headers=headers)
        response.raise_for_status()

        # Parse and display response
        result = response.json()
        json_str = json.dumps(result, indent=2)

        if HAS_PYGMENTS:
            print(highlight(json_str, JsonLexer(), TerminalFormatter()))
        else:
            print(json_str)

    except FileNotFoundError:
        print(f"Error: Image file '{image_path}' not found.")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}")
        try:
            error_details = e.response.json()
            print(json.dumps(error_details, indent=2))
        except:
            print(e.response.text)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    image_path = input("Enter the path to the image: ")
    analyze_image(image_path)
