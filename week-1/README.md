# Week 1 – Azure Sentiment Analysis

This program connects to the **Azure AI Language** service and performs sentiment analysis on text that you provide.

## Prerequisites

- Python 3.8 or higher
- An [Azure AI Language](https://azure.microsoft.com/en-us/products/ai-services/ai-language) resource

## Setup

### 1. Create an Azure AI Language Resource

1. Sign in to the [Azure Portal](https://portal.azure.com).
2. Create a new **Language** resource (under *Azure AI services*).
3. Once deployed, navigate to **Keys and Endpoint** to retrieve:
   - **Endpoint** – looks like `https://<your-resource-name>.cognitiveservices.azure.com/`
   - **Key** – a 32-character string

### 2. Set Environment Variables

Set the following environment variables before running the program:

**macOS / Linux**
```bash
export AZURE_LANGUAGE_ENDPOINT="https://<your-resource-name>.cognitiveservices.azure.com/"
export AZURE_LANGUAGE_KEY="<your-key>"
```

**Windows (Command Prompt)**
```cmd
set AZURE_LANGUAGE_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
set AZURE_LANGUAGE_KEY=<your-key>
```

**Windows (PowerShell)**
```powershell
$env:AZURE_LANGUAGE_ENDPOINT = "https://<your-resource-name>.cognitiveservices.azure.com/"
$env:AZURE_LANGUAGE_KEY = "<your-key>"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Program

```bash
python sentiment_analysis.py
```

## Usage

After launching the program, enter any text when prompted:

```
=== Azure Sentiment Analysis ===
Type 'quit' or 'exit' to stop.

Enter text to analyze: I love learning about AI!

--- Sentiment Analysis Result ---
Overall Sentiment : Positive
Confidence Scores :
  Positive : 99.00%
  Neutral  : 01.00%
  Negative : 00.00%
---------------------------------
```

Type `quit` or `exit` to close the program.
