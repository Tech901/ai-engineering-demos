# Azure AI Translator Web Tool

A web-based interface for exploring the Azure AI Translate service with full visibility into API requests and responses.

## Features

- **Language Selection**: Choose from 45+ supported languages for both input and output
- **Text Translation**: Enter text and get instant translations via Azure AI Translate API
- **Developer Insights**: View complete JSON payloads for both HTTP requests and responses
- **Modern UI**: Clean interface using the paper.css framework
- **Error Handling**: Clear error messages and validation

## Setup

### Prerequisites

- Python 3.14+
- Azure AI Translator service subscription
- `uv` package manager

### Azure Credentials

You need to set up Azure AI Translator credentials as environment variables:

```bash
export AZURE_TRANSLATE_KEY="your-api-key-here"
export AZURE_TRANSLATE_REGION="your-region-here"  # e.g., eastus
export AZURE_TRANSLATE_ENDPOINT="your-endpoint-here"  # Optional, defaults to https://api.cognitive.microsofttranslator.com
```

To get these credentials:
1. Create an Azure AI Translator resource in the Azure Portal
2. Navigate to "Keys and Endpoint" section
3. Copy KEY 1 or KEY 2 and the LOCATION/REGION

### Installation

From the project root directory:

```bash
# Install dependencies
uv sync

# Run the application
uv run python web-translator/app.py
```

The application will start on `http://localhost:8000`

## Usage

1. Open your browser to `http://localhost:8000`
2. Select the source language (From Language)
3. Select the target language (To Language)
4. Enter text to translate in the input textarea
5. Click "Translate" button
6. View the translation result and the JSON payloads below

## API Details

The tool displays:
- **Request JSON**: Full HTTP request including URL, parameters, headers (with API key redacted), and body
- **Response JSON**: Complete API response including translations, detected language info, and metadata

## Technology Stack

- **Backend**: FastAPI (Python web framework)
- **Frontend**: HTML5, JavaScript (vanilla)
- **Styling**: paper.css framework
- **HTTP Client**: requests library
- **Template Engine**: Jinja2
- **Server**: Uvicorn (ASGI server)

## Resources

- [Azure AI Translator Documentation](https://learn.microsoft.com/en-us/azure/ai-services/translator/)
- [Supported Languages](https://learn.microsoft.com/en-us/azure/ai-services/translator/language-support)
- [REST API Reference](https://learn.microsoft.com/en-us/azure/ai-services/translator/reference/rest-api-guide)
- [paper.css Framework](https://www.getpapercss.com/)
