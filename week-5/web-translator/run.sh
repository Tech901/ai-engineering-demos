#!/bin/bash
# Run the Azure AI Translator Web Tool

# Check if environment variables are set
if [ -z "$AZURE_TRANSLATE_KEY" ]; then
    echo "Warning: AZURE_TRANSLATE_KEY environment variable is not set"
    echo "Please set it with: export AZURE_TRANSLATE_KEY='your-key'"
fi

if [ -z "$AZURE_TRANSLATE_REGION" ]; then
    echo "Warning: AZURE_TRANSLATE_REGION environment variable is not set"
    echo "Using default region: eastus"
    export AZURE_TRANSLATE_REGION="eastus"
fi

if [ -z "$AZURE_TRANSLATE_ENDPOINT" ]; then
    echo "Info: AZURE_TRANSLATE_ENDPOINT not set, using default: https://api.cognitive.microsofttranslator.com"
fi

echo "Starting Azure AI Translator Web Tool..."
echo "Access the application at: http://localhost:8000"
echo ""

uv run python web-translator/app.py
