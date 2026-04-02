# Azure AI Question & Answering Example

A Python project that demonstrates how to connect to Azure AI Question & Answering service to query knowledge bases.

## Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- Azure AI Language resource with Question Answering enabled
- [direnv](https://direnv.net/) (optional, for automatic environment variable loading)

## Setup

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Configure environment variables**:
   
   Copy `.envrc` and update with your Azure credentials:
   ```bash
   export AZURE_QA_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com"
   export AZURE_QA_API_KEY="your-api-key"
   export AZURE_QA_PROJECT_NAME="YourProjectName"  # Optional, defaults to CustomerSupportQA
   export AZURE_QA_DEPLOYMENT_NAME="YourDeploymentName"  # Optional, defaults to CustomerSupportQADep
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

## Running the Application

### With direnv (automatic environment loading):
```bash
uv run main.py
```

### Without direnv (manual environment loading):
```bash
source .envrc && uv run main.py
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_QA_ENDPOINT` | Yes | - | Azure AI Language service endpoint URL |
| `AZURE_QA_API_KEY` | Yes | - | Azure subscription key for authentication |
| `AZURE_QA_PROJECT_NAME` | No | CustomerSupportQA | Name of your QA project |
| `AZURE_QA_DEPLOYMENT_NAME` | No | CustomerSupportQADep | Name of your deployment |

## How It Works

The application:
1. Loads credentials from environment variables
2. Sends a question to the Azure Question Answering service
3. Receives and displays the answer with confidence scores
4. Supports short answer extraction and structured knowledge base queries

## Example Output

```json
{
  "answers": [
    {
      "questions": [...],
      "answer": "You can track your shipment using...",
      "confidenceScore": 0.95,
      "id": 1,
      "source": "...",
      "metadata": {...}
    }
  ]
}
```

## Modifying the Question

Edit `main.py` and change the `question` variable:

```python
question = "Your question here?"
```

## Troubleshooting

- **404 Error**: Verify your project name and deployment name are correct in Azure
- **401 Error**: Check that your API key is valid
- **Environment variables not loaded**: Make sure to run `source .envrc` or use direnv

## Resources

- [Azure AI Question Answering Documentation](https://learn.microsoft.com/azure/ai-services/language-service/question-answering/overview)
- [uv Documentation](https://github.com/astral-sh/uv)
