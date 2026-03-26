import os
import json
import uuid
from typing import Optional
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI(title="Azure AI Translator Web Tool")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="web-translator/templates")

# Azure Translator configuration
AZURE_TRANSLATE_KEY = os.getenv("AZURE_TRANSLATE_KEY")
AZURE_TRANSLATE_REGION = os.getenv("AZURE_TRANSLATE_REGION", "eastus")
AZURE_TRANSLATE_ENDPOINT = os.getenv(
    "AZURE_TRANSLATE_ENDPOINT", "https://api.cognitive.microsofttranslator.com"
)

# Supported languages (subset of Azure's full list)
LANGUAGES = {
    "af": "Afrikaans",
    "ar": "Arabic",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "ca": "Catalan",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "fa": "Persian",
    "fi": "Finnish",
    "fr": "French",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "ms": "Malay",
    "nl": "Dutch",
    "no": "Norwegian",
    "pl": "Polish",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sr": "Serbian",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "vi": "Vietnamese",
    "zh-Hans": "Chinese (Simplified)",
    "zh-Hant": "Chinese (Traditional)",
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main translator page"""
    # Sort languages by name instead of code
    sorted_languages = dict(sorted(LANGUAGES.items(), key=lambda item: item[1]))
    return templates.TemplateResponse(
        "index.html", {"request": request, "languages": sorted_languages}
    )


@app.post("/translate")
async def translate(
    from_lang: str = Form(...), to_lang: str = Form(...), text: str = Form(...)
):
    """
    Translate text using Azure AI Translator API
    Returns the translation along with request/response JSON
    """
    if not AZURE_TRANSLATE_KEY:
        return {
            "success": False,
            "error": "AZURE_TRANSLATE_KEY environment variable not set",
            "request_json": {},
            "response_json": {},
        }

    if not text.strip():
        return {
            "success": False,
            "error": "Input text cannot be empty",
            "request_json": {},
            "response_json": {},
        }

    # Build the API request
    path = "/translate"
    constructed_url = AZURE_TRANSLATE_ENDPOINT + path

    params = {"api-version": "3.0", "from": from_lang, "to": to_lang}

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_TRANSLATE_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_TRANSLATE_REGION,
        "Content-type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4()),
    }

    body = [{"text": text}]

    # Prepare request JSON for display
    request_json = {
        "url": constructed_url,
        "params": params,
        "headers": {
            k: v if k != "Ocp-Apim-Subscription-Key" else "***REDACTED***"
            for k, v in headers.items()
        },
        "body": body,
    }

    try:
        # Make the API call
        response = requests.post(
            constructed_url, params=params, headers=headers, json=body
        )

        response_json = response.json()

        if response.status_code == 200:
            # Extract translation from response
            translation = response_json[0]["translations"][0]["text"]
            detected_lang = response_json[0].get("detectedLanguage", {})

            return {
                "success": True,
                "translation": translation,
                "detected_language": detected_lang,
                "request_json": request_json,
                "response_json": response_json,
            }
        else:
            return {
                "success": False,
                "error": f"API Error: {response.status_code}",
                "request_json": request_json,
                "response_json": response_json,
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Exception: {str(e)}",
            "request_json": request_json,
            "response_json": {},
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
